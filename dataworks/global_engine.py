##################################################################################################
####                                                                                           ### 
####  the global object created a universal engine and session that can be used by all         ###
####  subsequent sql alchemy classes.  It also defines distinct base classes for system        ### 
####  control separated from the general business classes                                      ### 
####                                                                                           ### 
####  date      by    action                                                                   ### 
####  20230911  AJT   Created                                                                  ### 
##################################################################################################
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL
from sqlalchemy.orm import declarative_base, Session
from pydantic import BaseModel
import os

# default global database connection
globalEngine = create_engine( 
   URL(
      account = os.environ.get("SnowflakeAccount"),
      user = os.environ.get("SnowflakeUser"),
      password = os.environ.get("SnowflakePassword"),
      warehouse = os.environ.get("SnowflakeWarehouse"),
      role = os.environ.get("SnowflakeRole")
   )
)     

# create a new control base class
ControlPersistent = declarative_base()
BusinessPersistent = declarative_base()
class BusinessValidated( BaseModel) :
   pass

globalSession = Session( globalEngine)
