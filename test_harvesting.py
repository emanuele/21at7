import glob,sys,time,threading,getopt

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
	mainDB='sqlite:///21at7.sqlite'
	lacrosse_serial=None
	ciseco_serial=None

	try:                                
		opts, args = getopt.getopt(sys.argv[1:], "dlc", ["db=", "lacrosse=", "ciseco="])

		for opt, arg in opts:
			if opt in ("-d", "--db"):
				mainDB=arg
			elif opt in ("-l", "--lacrosse"):
				lacrosse_serial=arg
			elif opt in ("-c", "--ciseco"):
				ciseco_serial=arg

		other = " ".join(args)

	except getopt.GetoptError:
		print sys.argv[0], '--db SQLALCHEMY_DBURL --lacrosse=SERNAME', '--ciseco=SERNAME'
		if len(sys.argv)==1:
			print 'SERNAME can be one of these:'
			for serName in glob.glob('/dev/ttyUSB*') + glob.glob('/dev/tty.usbserial-*'):
				print '  -', serName

	if lacrosse_serial or ciseco_serial:
		sensors=None

		session_maker=SessionMaker(mainDB,debug=False)
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
			sensors=session.query(Sensor).filter_by(harvester='ciseco')
			if sensors.count()==0:
				ciseco1 = Sensor(harvester='ciseco',desc='ufficio',address='H0')
				session.add(ciseco1)
				session.commit()
				print 'created ciseco test sensor'
		except:
			e = sys.exc_info()[0]
			print 'sensors query error: %s'%e
			sensors=None
		finally:
			try:
				session.close()
			except:
				log(self,'db (sensor) session close error')

		if sensors and sensors.count()>0:
			print 'registered sensors:'
			for sensor in sensors.all():
				print '  - sensor: %s'%sensor.address

			test_runner=TestRunner()
			if lacrosse_serial:
				lacrosse_reader=lacrosse.Reader(mainDB,lacrosse_serial,debug=True,dbdebug=False)
				lacrosse_cleaner=lacrosse.Cleaner(mainDB,debug=True,dbdebug=False)
			if ciseco_serial:
				ciseco_reader=ciseco.Reader(mainDB,ciseco_serial,debug=True,dbdebug=False)
				ciseco_cleaner=ciseco.Cleaner(mainDB,debug=True,dbdebug=False)

			test_runner.start()
			if lacrosse_serial:
				lacrosse_reader.start()
				lacrosse_cleaner.start()
			if ciseco_serial:
				ciseco_reader.start()
				ciseco_cleaner.start()

		else:
			print 'no sensors configured: exiting...'
	else:
		print sys.argv[0], '--db SQLALCHEMY_DBURL --lacrosse=SERNAME', '--ciseco=SERNAME'
		if len(sys.argv)==1:
			print 'SERNAME can be one of these:'
			for serName in glob.glob('/dev/ttyUSB*') + glob.glob('/dev/tty.usbserial-*'):
				print '  -', serName
