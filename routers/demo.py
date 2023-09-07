from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import select
from sqlalchemy import create_engine
from sqlalchemy import inspect
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
from snowflake.sqlalchemy import URL
from sqlalchemy.ext.declarative import as_declarative

demo_marts_engine = create_engine( 
   URL(
      account = 'gc77589.eu-west-2.aws',
      user = 'svc_api',
      password = 'R8CPFfHYCfuhHKXXinkq',
      database = 'marts',
      schema = 'prod',
      warehouse = 'investigating',
      role='investigator',
   )
)     

Base = declarative_base()

class student( Base):
   __tablename__ = "dim_students"

   personid = Column( Integer, primary_key=True)
   lastname = Column( String(256))
   firstname = Column( String(256))
   fullname = Column( String(256))
   email = Column( String(256))
   accid = Column( String(256))
   libid = Column( String(256))
   timeid = Column( String(256))

   def __repr__(self):
      return f"student(id={self.personid!r}, name={self.fullname!r}, email={self.email!r}"  

   def _asdict( self):
      return { c.key: getattr( self, c.key)
         for c in inspect( self).mapper.column_attrs}     
      
class student_schedule( Base):
   __tablename__ = "student_schedule"

   courseid = Column( Integer, primary_key=True)
   day = Column( String(256), primary_key=True)
   studentid = Column( String(256), primary_key=True)
   course_time = Column( String(256))
   location = Column( String(256))
   fullname = Column( String(256))
   email = Column( String(256))
   instructorname = Column( String(256))

   def __repr__(self):
      return f"student_schedule(id={self.courseid!r}, time={self.course_time!r}, location={self.location!r}, instructor={self.instructorname!r}, studentemail={self.email!r}"  
   
   def _asdict( self):
      return { c.key: getattr( self, c.key)
         for c in inspect( self).mapper.column_attrs}     

router = APIRouter(
    prefix="/assured",
    tags=["student"],
    responses={ 404: {"description": "Not found"}},
)

@router.get("/student")
async def get_students():
   session = Session( demo_marts_engine)

   Students = session.query(student).all()

   return Students   
   
@router.get("/student/{student_id}")
async def get_student( student_id: str):
   session = Session(demo_marts_engine)

   Products = session.query( student).filter( student.personid == student_id).all()
   
   return [ eachProduct._asdict() for eachProduct in Products]

@router.get("/student/{student_id}/schedule")
async def get_student_schedule( student_id: str):
   session = Session(demo_marts_engine)

   Schedule = session.query( student_schedule).filter( student_schedule.studentid == student_id).all()
   
   return [ eachSchedule._asdict() for eachSchedule in Schedule]   

@router.get("/student/{student_id}/schedule/{schedule_id}")
async def get_student_schedule( student_id: str, schedule_id: str):
   session = Session(demo_marts_engine)

   Schedule = session.query( student_schedule).filter( student_schedule.studentid == student_id, student_schedule.courseid == schedule_id).all()
   
   return [ eachSchedule._asdict() for eachSchedule in Schedule]   

@router.get("/schedule/{schedule_id}")
async def get_student_schedule( schedule_id: str):
   session = Session(demo_marts_engine)

   Schedule = session.query( student_schedule).filter( student_schedule.courseid == schedule_id).all()
   
   return [ eachSchedule._asdict() for eachSchedule in Schedule]   

@router.get("/schedule/{schedule_id}/day/{day}")
async def get_student_schedule( schedule_id: str, day: str):
   session = Session(demo_marts_engine)

   Schedule = session.query( student_schedule).filter( student_schedule.courseid == schedule_id, student_schedule.day == day).all()
   
   return [ eachSchedule._asdict() for eachSchedule in Schedule]   