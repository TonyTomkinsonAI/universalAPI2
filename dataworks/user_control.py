##################################################################################################
####                                                                                           ### 
####  the global object created a universal engine and session that can be used by all         ###
####  subsequent sql alchemy classes.  It also defines distinct base classes for system        ### 
####  control separated from the general business classes                                      ### 
####                                                                                           ### 
####  date      by    action                                                                   ### 
####  20230911  AJT   created                                                                  ###
####  20230913  AJT   moved user elements from main and user new base classes                  ###
##################################################################################################
from sqlalchemy import inspect
from sqlalchemy import Column, String, Boolean
from dataworks.global_engine import ControlPersistent, globalSession, BusinessValidated
from typing import Union
from passlib.context import CryptContext
import os

pwd_context = CryptContext( schemes=[ "bcrypt"], deprecated="auto")    

# derive the user control class from the base class and link to the db table
class user_control( ControlPersistent):
   #link the table name
   __tablename__ = "user_control"
   __table_args__ = { 'schema': os.environ.get( "SnowflakeControlDB") + '.' + os.environ.get( "SnowflakeControlSchema")}   

   # define the columns
   username = Column( String( 256), primary_key=True)
   full_name = Column( String( 256))
   email = Column( String( 2048))
   hashed_password = Column( String( 2048))
   enabled = Column( Boolean())

   # define simple representation
   def __repr__(self):
      return f"login(username={self.username!r}, full_name={self.full_name!r}, email={self.email!r}"  

   # return properties as a dictionary
   def _asdict( self):
      return { c.key: getattr( self, c.key)
         for c in inspect( self).mapper.column_attrs}  

# define a wrapper class that will surface the data as a dictionary
class userLogins :
   def __init__( self) -> None:
      # load all of the users from the user control database
      self._userQry = globalSession.query( user_control).all()
      # build the local dictionary
      self._users = {}
      # iterate through the users
      for user in self._userQry :
         # add an entry into the dictionary for each user
         self._users[ user.username] = user._asdict()
      
   # return the completed dictionary
   def get_users( self):
      return self._users  
   
   def get_user( self, username: str):
      for user in self._userQry :
         # if this is the required user
         if user.username == username :
            # return a pointer to the dictionary value of the user
            return UserInDB( **user._asdict())   

   def authenticate_user( self, username: str, password: str):
      user = self.get_user( username)
      if not user:
         return False
      if not user.verify_password( password):
         return False
      return user         

   users = property( get_users)
   
class User( BusinessValidated):
   username: str
   email: Union[str, None] = None
   full_name: Union[str, None] = None
   enabled: Union[bool, None] = None
    
class UserInDB( User):
   hashed_password: str

   def verify_password( self, plain_password):
      return pwd_context.verify( plain_password, self.hashed_password)

   def get_password_hash( self, password):
      return pwd_context.hash( password)



