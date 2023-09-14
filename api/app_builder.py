from datetime import datetime, timedelta
from typing import Annotated, List, Union
import azure.functions as func
from fastapi import Depends, FastAPI, Request, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from fastapi.responses import JSONResponse
from jose import JWTError, jwt, ExpiredSignatureError
from pydantic import BaseModel, ValidationError

from dataworks.user_control import userLogins, User
from utilities.exceptions import ApiException

from routers import caprice, demo

def build_app():
   oauth2_scheme = OAuth2PasswordBearer(
      tokenUrl="token",
      scopes={ "me": "Read information about the current user.", "items": "Read items."},
   )
   
   app = FastAPI()

   # include the demo router
   app.include_router( demo.router, dependencies=[Depends(oauth2_scheme)])
   app.include_router( caprice.router, dependencies=[Depends(oauth2_scheme)])

   # to get a string like this run:
   # openssl rand -hex 32
   SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
   ALGORITHM = "HS256"
   ACCESS_TOKEN_EXPIRE_MINUTES = 30

   # load the user control db
   logins = userLogins()

   class Token( BaseModel):
      access_token: str
      token_type: str

   class TokenData( BaseModel):
      username: Union[str, None] = None
      scopes: List[str] = []   
      
   # create an access token
   def create_access_token( data: dict, expires_delta: Union[ timedelta, None] = None):
      # take a copy of the dictionary
      to_encode = data.copy()
      # if we've supplied a custom expiry
      if expires_delta:
         # calculate the expiry as now + custom
         expire = datetime.utcnow() + expires_delta
      else:
         # otherwise expire after 15 minutes
         expire = datetime.utcnow() + timedelta(minutes=15)
      #write the expiry to the token
      to_encode.update({"exp": expire})
      # encode the dictionary 
      encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
      # return the encoded dictionary as an access token
      return encoded_jwt  

   async def get_current_user(
      security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]
   ):
      # get the active scopes
      if security_scopes.scopes:
         authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
      else:
         authenticate_value = "Bearer"
         
      # define the credentials exception
      credentials_exception = HTTPException(
         status_code=status.HTTP_401_UNAUTHORIZED,
         detail="Could not validate credentials",
         headers={"WWW-Authenticate": authenticate_value},
      )
      
      try:
         # decode the authentication payload
         payload = jwt.decode( token, SECRET_KEY, algorithms=[ALGORITHM])
         # get the user name
         username: str = payload.get("sub")
         # if the user name is empty then raise a credentials exception
         if username is None:
            raise credentials_exception
         # get the scopes from the token
         token_scopes = payload.get("scopes", [])
         # build the token data
         token_data = TokenData(scopes=token_scopes, username=username)
      except ExpiredSignatureError: # <---- this one
         raise HTTPException(status_code=403, detail="token has been expired")
      except ( JWTError, ValidationError):
         # trap any exceptions and re-raise
         raise credentials_exception
      
      # from the user logins object get the user from the token supplied username
      user = logins.get_user( username=token_data.username)
      
      # if we can't find an enabled user
      if user is None:
         # raise a credentials excepttion
         raise credentials_exception
      
      # iterate through the scopes in the function
      for scope in security_scopes.scopes:
         # if the required scope is not in the token
         if scope not in token_data.scopes:
            # raise an authorisation exception
            raise HTTPException(
               status_code=status.HTTP_401_UNAUTHORIZED,
               detail="Not enough permissions",
               headers={"WWW-Authenticate": authenticate_value},
            )
      # if we have a user and no exceptions then return the user      
      return user

   async def get_current_active_user(
      current_user: Annotated[User, Security(get_current_user, scopes=["me"])]
   ):
      # get the current user and check if they're enabled
      if not current_user.enabled:
         # if not then raise an inactive user error
         raise HTTPException(status_code=400, detail="Inactive user")
      # otherwise return the current user
      return current_user
   
   # exception handler 
   @app.exception_handler(ApiException)
   async def generic_api_exception_handler(request: Request, ex: ApiException):
      return JSONResponse(
         status_code=ex.status_code,
         content={
               "code": ex.code,
               "description": ex.description
         }
      ) 
   
   # token endpoint
   @app.post("/token", response_model=Token)
   async def login_for_access_token(
      form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
   ):
      user = logins.authenticate_user( form_data.username, form_data.password)
      if not user:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
         )
      access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
      access_token = create_access_token(
         data={"sub": user.username, "scopes": form_data.scopes},
         expires_delta=access_token_expires
      )
      return {"access_token": access_token, "token_type": "bearer"}

   @app.get("/users/me", response_model=User)
   async def read_users_me(
      current_user: Annotated[User, Depends(get_current_active_user)]
   ):
      return current_user    

   @app.get("/users/me/items/")
   async def read_own_items(
      current_user: Annotated[User, Security(get_current_active_user, scopes=["items"])]
   ):
      return [{"item_id": "Foo", "owner": current_user.username}]


   @app.get("/status/")
   async def read_system_status(current_user: Annotated[User, Depends(get_current_user)]):
      return {"status": "ok"}
   
   return app