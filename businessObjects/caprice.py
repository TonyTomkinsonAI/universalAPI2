from sqlalchemy import inspect
from sqlalchemy import Column, String, Integer
from dataworks.caprice_engine import BusinessPersistent, globalSession
from fastapi import APIRouter
from typing import Union

class product( BusinessPersistent):
   __tablename__ = "product"
   __table_args__ = { 'schema': 'canon.prod'}   

   productid = Column( Integer, primary_key=True)
   productname = Column( String(256))
   measure = Column( String(18))
   salescategory = Column( String(256))

   def __repr__(self):
      return f"product(id={self.productid!r}, name={self.productname!r}, measure={self.measure!r}, salescategory={self.salescategory!r})"  
     
   def _asdict( self):
      return { c.key: getattr( self, c.key)
         for c in inspect( self).mapper.column_attrs}   
      
   def all( self) :
      return globalSession.query( product).all()   
      
   def byProductId( self, product_id: int) :
      return globalSession.query( product).filter( product.productid == product_id).all()
   
   def byMeasure( self, measure: str) :
      return globalSession.query( product).filter( product.measure == measure).all()   
   
   def bySalesCategory( self, salescategory: str) :
      return globalSession.query( product).filter( product.salescategory == salescategory).all()  