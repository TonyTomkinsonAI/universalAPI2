import logging
from datetime import datetime, timedelta
from typing import Annotated, List, Union

from fastapi import Depends, FastAPI, Request, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from fastapi.responses import JSONResponse
import azure.functions as func
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError

from routers import demo
from utilities.exceptions import ApiException

def build_app():

   app = FastAPI()

   oauth2_scheme = OAuth2PasswordBearer(
      tokenUrl="token",
      scopes={ "me": "Read information about the current user.", "items": "Read items."},
   )

   app.include_router( demo.router, dependencies=[Depends(oauth2_scheme)])
   
# to get a string like this run:
   # openssl rand -hex 32
   SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
   ALGORITHM = "HS256"
   ACCESS_TOKEN_EXPIRE_MINUTES = 30

   fake_users_db = {
      "johnnytinseltown": {
         "username": "johnnytinseltown",
         "full_name": "Johnny Tinseltown",
         "email": "johnnytinseltown@assuredinsights.co.uk",
         "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
         "disabled": False,
      },
      "alicewonderland": {
         "username": "alicewonderland",
         "full_name": "Alice Wonderland",
         "email": "alicewonderland@assuredinsights.co.uk",
         "hashed_password": "fakehashed-MadAsAHatter",
         "disabled": True,
      },
   }

   class Token(BaseModel):
      access_token: str
      token_type: str

   class TokenData(BaseModel):
      username: Union[str, None] = None
      scopes: List[str] = []   

   class User(BaseModel):
      username: str
      email: Union[str, None] = None
      full_name: Union[str, None] = None
      disabled: Union[bool, None] = None
      
   class UserInDB(User):
      hashed_password: str
      
   pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")    

   def verify_password( plain_password, hashed_password):
      return pwd_context.verify( plain_password, hashed_password)

   def get_password_hash( password):
      return pwd_context.hash( password)

   def get_user( db, username: str):
      if username in db:
         user_dict = db[username]
         return UserInDB(**user_dict)

   def authenticate_user( fake_db, username: str, password: str):
      user = get_user( fake_db, username)
      if not user:
         return False
      if not verify_password( password, user.hashed_password):
         return False
      return user

   def create_access_token( data: dict, expires_delta: Union[ timedelta, None] = None):
      to_encode = data.copy()
      if expires_delta:
         expire = datetime.utcnow() + expires_delta
      else:
         expire = datetime.utcnow() + timedelta(minutes=15)
      to_encode.update({"exp": expire})
      encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
      return encoded_jwt  

   async def get_current_user(
      security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]
   ):
      if security_scopes.scopes:
         authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
      else:
         authenticate_value = "Bearer"
      credentials_exception = HTTPException(
         status_code=status.HTTP_401_UNAUTHORIZED,
         detail="Could not validate credentials",
         headers={"WWW-Authenticate": authenticate_value},
      )
      try:
         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
         username: str = payload.get("sub")
         if username is None:
               raise credentials_exception
         token_scopes = payload.get("scopes", [])
         token_data = TokenData(scopes=token_scopes, username=username)
      except ( JWTError, ValidationError):
         raise credentials_exception
      user = get_user(fake_users_db, username=token_data.username)
      if user is None:
         raise credentials_exception
      for scope in security_scopes.scopes:
         if scope not in token_data.scopes:
               raise HTTPException(
                  status_code=status.HTTP_401_UNAUTHORIZED,
                  detail="Not enough permissions",
                  headers={"WWW-Authenticate": authenticate_value},
               )
      return user

   async def get_current_active_user(
      current_user: Annotated[User, Security(get_current_user, scopes=["me"])]
   ):
      if current_user.disabled:
         raise HTTPException(status_code=400, detail="Inactive user")
      return current_user
   
   @app.exception_handler(ApiException)
   async def generic_api_exception_handler(request: Request, ex: ApiException):
      return JSONResponse(
         status_code=ex.status_code,
         content={
               "code": ex.code,
               "description": ex.description
         }
      )
   
   @app.post("/token", response_model=Token)
   async def login_for_access_token(
      form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
   ):
      user = authenticate_user(fake_users_db, form_data.username, form_data.password)
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