##################################################################################################
####                                                                                           ### 
####  the caprice object created a caprice specific engine and session that can be used by all ###
####  subsequent sql alchemy classes.  It also defines distinct base classes for system        ### 
####  control separated from the general business classes                                      ### 
####                                                                                           ### 
####  date      by    action                                                                   ### 
####  20230913  AJT   Created                                                                  ### 
##################################################################################################
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL
from sqlalchemy.orm import declarative_base, Session
from pydantic import BaseModel
import os

# default global database connection
globalEngine = create_engine( 
   URL( 
      account = os.environ.get("CapriceAccount"),
      user = os.environ.get("CapriceUser"),
      password = os.environ.get("CapricePassword"),
      warehouse = os.environ.get("CapriceWarehouse"),
      role = os.environ.get("CapriceRole")       
   )
)     

# create a new control base class
ControlPersistent = declarative_base()
BusinessPersistent = declarative_base()
class BusinessValidated( BaseModel) :
   pass

globalSession = Session( globalEngine)