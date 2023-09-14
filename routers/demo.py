from fastapi import APIRouter
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import select
from sqlalchemy import inspect
from dataworks.global_engine import BusinessPersistent, globalSession

class student( BusinessPersistent):
   __tablename__ = "dim_student"
   __table_args__ = { 'schema': 'canon.prod'}

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
      
class student_schedule( BusinessPersistent):
   __tablename__ = "student_schedule"
   __table_args__ = { 'schema': 'canon.prod'}

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
   Students = globalSession.query(student).all()

   return Students   
   
@router.get("/student/{student_id}")
async def get_student( student_id: str):
   Students = globalSession.query( student).filter( student.personid == student_id).all()
   
   return [ eachStudent._asdict() for eachStudent in Students]

@router.get("/student/{student_id}/schedule")
async def get_student_schedule( student_id: str):
   Schedule = globalSession.query( student_schedule).filter( student_schedule.studentid == student_id).all()
   
   return [ eachSchedule._asdict() for eachSchedule in Schedule]   

@router.get("/student/{student_id}/schedule/{schedule_id}")
async def get_student_schedule( student_id: str, schedule_id: str):
   Schedule = globalSession.query( student_schedule).filter( student_schedule.studentid == student_id, student_schedule.courseid == schedule_id).all()
   
   return [ eachSchedule._asdict() for eachSchedule in Schedule]   

@router.get("/schedule/{schedule_id}")
async def get_student_schedule( schedule_id: str):
   Schedule = globalSession.query( student_schedule).filter( student_schedule.courseid == schedule_id).all()
   
   return [ eachSchedule._asdict() for eachSchedule in Schedule]   

@router.get("/schedule/{schedule_id}/day/{day}")
async def get_student_schedule( schedule_id: str, day: str):
   Schedule = globalSession.query( student_schedule).filter( student_schedule.courseid == schedule_id, student_schedule.day == day).all()
   
   return [ eachSchedule._asdict() for eachSchedule in Schedule]   