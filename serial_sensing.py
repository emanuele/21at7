import serial,glob,datetime,sys

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

if __name__ == '__main__':
	if len(sys.argv) < 2:
		serials=glob.glob('/dev/ttyUSB*') + glob.glob('/dev/tty.usbserial-*') + glob.glob('/dev/cu.*')
	else:
		serials=[ sys.argv[1] ]


	if len(serials)!=1:
		print 'select one of these devices:'
		for serName in serials: print '  -', serName

	else:
		print 'serial name:', serials[0]
		ser = serial.Serial(serials[0],57600,timeout=2)
		serActive=True
	
		Base = declarative_base()
		class Reading(Base):
			__tablename__ = 'readings'
			id = Column(DateTime, primary_key=True)
			data = Column(String)

		engine = create_engine('sqlite:///:memory:', echo=True)
		Base.metadata.create_all(engine) 
		Session = sessionmaker(bind=engine)

		while serActive and ser.isOpen():
			try:
				msg=ser.readline()
				if msg:
					msg=msg.strip()
					print 'msg:', msg
					if msg.startswith('D:'):
						session = Session()
						session.add(Reading(id=datetime.datetime.now(),data=msg))
						session.commit()
					else:
						print '*** unknown msg ***'
				#else:
				#	print 'no msg...'
			except KeyboardInterrupt:	
				ser.close()
			except:
				print 'ERROR!'
				serActive=False

		try:
			if ser and ser.isOpen(): ser.close()
		except:
			print 'serial close error'
		
