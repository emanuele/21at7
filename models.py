from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative.declarative_base import Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DateTime

engine = create_engine('sqlite:///:memory:', echo=True)
declarative_base().metadata.create_all(engine) 
Session = sessionmaker(bind=engine)

class Reading(Base):
	__tablename__ = 'readings'
	id = Column(DateTime, primary_key=True)
	data = Column(String)
