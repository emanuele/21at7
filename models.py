from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Time, Float
from sqlalchemy.pool import NullPool, QueuePool


Base=declarative_base()

class SessionMaker:
	def __init__(self, dbUrl, debug=False):
		engine = create_engine(dbUrl, echo=debug, poolclass=NullPool)
		Base.metadata.create_all(engine) 
		self.maker = sessionmaker(bind=engine)
	
	def get_session(self):
		return self.maker()


class Sensor(Base):
	__tablename__ = 'sensors'
	extend_existing=True
	id = Column(Integer, primary_key=True)
	harvester = Column(String)
	desc = Column(String)
	address = Column(String)
	measurements = relationship("Measure", backref="who")

class Reading(Base):
	__tablename__ = 'readings'
	extend_existing=True
	id = Column(DateTime, primary_key=True)
	harvester = Column(String)
	data = Column(String)

class Measure(Base):
	__tablename__ = 'measures'
	extend_existing=True
	id = Column(Integer, primary_key=True)
	sensor_id = Column(Integer, ForeignKey('sensors.id'))
	when = Column(DateTime,index=True)
	what = Column(String,index=True)
	howmuch = Column(Float(precision=1),index=True)

class Schedule(Base):
	__tablename__ = 'schedules'
	extend_existing=True
	id = Column(Integer, primary_key=True)
	what = Column(String,index=True)
	day = Column(Integer,index=True)
	date = Column(Date,index=True)
	howmuch = Column(Float(precision=1),index=True)
	start = Column(Time,index=True)
	stop = Column(Time,index=True)
