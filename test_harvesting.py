import glob,sys,time,threading

from models import SessionMaker,Sensor
from harvesters import *

class TestRunner(threading.Thread):
	def __init__(self):
		super(TestRunner,self).__init__()
		self.setDaemon(False)

	def run(self):
		print 'TESTS STARTED'
		time.sleep(10)
		print 'TESTS ENDED'

if __name__ == '__main__':
	if len(sys.argv) < 2:
		serials=glob.glob('/dev/ttyUSB*') + glob.glob('/dev/tty.usbserial-*')
	else:
		serials=[ sys.argv[1] ]
	if len(serials)==1:

		mainDB='sqlite:///21at7.sqlite'

		sensors=None
		session_maker=SessionMaker(mainDB)
		session = session_maker.get_session()
		try:
			sensors=session.query(Sensor).filter_by(harvester='lacrosse')
			if sensors.count()==0:
				lacrosse1 = Sensor(harvester='lacrosse',desc='ufficio',address='50')
				lacrosse2 = Sensor(harvester='lacrosse',desc='esterno',address='A8')
				session.add(lacrosse1)
				session.add(lacrosse2)
				session.commit()
				print 'created lacrosse test sensors'
		except:
			e = sys.exc_info()[0]
			print 'sensors query error: %s'%e
			sensors=None
		finally:
			try:
				session.close()
			except:
				log(self,'db (sensor) session close error')

		if sensors:
			print 'registered sensors:'
			for sensor in sensors.all():
				print ' - sensor: %s'%sensor.address

			reader=lacrosse.Reader(mainDB,serials[0],debug=True)
			cleaner=lacrosse.Cleaner(mainDB,debug=True)

			runner=TestRunner()
			runner.start()

			reader.start()
			cleaner.start()
		else:
			print 'no sensors configured: exiting...'

	elif len(serials)==0:
		print 'looks like no supported tty serial device is available among these:'
		for serName in glob.glob('/dev/tty*'): print '  -', serName
	else:
		print 'select one of these devices:'
		for serName in serials: print '  -', serName
