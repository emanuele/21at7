from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.pool import NullPool, QueuePool


Base=declarative_base()

class Session:
	def __init__(self, dbUrl):
		engine = create_engine(dbUrl, echo=True, poolclass=NullPool)
		Base.metadata.create_all(engine) 
		self.SessionMaker = sessionmaker(bind=engine)
	
	def get_session(self):
		return self.SessionMaker()


class Reading(Base):
	__tablename__ = 'readings'
	extend_existing=True
	id = Column(DateTime, primary_key=True)
	type = Column(String)
	data = Column(String)

class Measure(Base):
	__tablename__ = 'measures'
	extend_existing=True
	id = Column(DateTime, primary_key=True)
	where = Column(String,index=True)
	when = Column(DateTime,index=True)
	what = Column(String,index=True)
	howmuch = Column(String,index=True)
