from businessObjects.caprice import product
from fastapi import APIRouter

router = APIRouter(
    prefix="/caprice",
    tags=["product"],
    responses={404: {"description": "Not found"}},
)

fake_items_db = {"plumbus": {"name": "Plumbus"}, "gun": {"name": "Portal Gun"}}

@router.get("/product")
async def read_items():
   #Products = globalSession.query( product).all()
   Products = product().all
   
   return Products

@router.get("/product/{product_id}")
async def read_item( product_id: str):
   #Products = globalSession.query( product).filter( product.productid == product_id).all()
   Products = product().byProductId( product_id=product_id)
   
   return [ eachProduct._asdict() for eachProduct in Products]

@router.get("/product/measure/{measure}")
async def read_item( measure: str):
   #Products = globalSession.query( product).filter( product.measure == measure).all()
   Products = product().byMeasure( measure=measure)
   
   return [ eachProduct._asdict() for eachProduct in Products]


@router.get("/product/salescategory/{salescategory}")
async def read_item( salescategory: str):
   #Products = globalSession.query( product).filter( product.salescategory == salescategory).all()
   Products = product().bySalesCategory( salescategory=salescategory)
   
   return [ eachProduct._asdict() for eachProduct in Products]

