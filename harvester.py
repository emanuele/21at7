import glob,sys,time,threading,getopt

from config import mainDB,lacrosse_serial,ciseco_serial
from models import SessionMaker,Sensor
from harvesters import *
from daemon import Daemon


class Harvester(Daemon):
	def run(self):
		if lacrosse_serial:
			self.lacrosse_reader=lacrosse.Reader(mainDB,lacrosse_serial,debug=True,dbdebug=False)
			self.lacrosse_reader.start()
			self.lacrosse_cleaner=lacrosse.Cleaner(mainDB,debug=True,dbdebug=False)
			self.lacrosse_cleaner.start()
		else:
			sys.stderr.write('no lacrosse sensors')
			sys.stderr.flush()

		if ciseco_serial:
			self.ciseco_reader=ciseco.Reader(mainDB,ciseco_serial,debug=True,dbdebug=False)
			self.ciseco_reader.start()
			self.ciseco_cleaner=ciseco.Cleaner(mainDB,debug=True,dbdebug=False)
			self.ciseco_cleaner.start()
		else:
			sys.stderr.write('no ciseco sensors\n')
			sys.stderr.flush()

		sys.stderr.write('HARVESTING STARTED\n')
		sys.stderr.flush()
		while True:
			time.sleep(1)
		sys.stderr.write('HARVESTING ENDED\n')
		sys.stderr.flush()


if __name__ == '__main__':
	if lacrosse_serial or ciseco_serial:
		daemon=Harvester('/tmp/21at7-harvester.pid',stdout='/tmp/21at7-harvester.log',stderr='/tmp/21at7-harvester.log')
		if len(sys.argv) == 2:
			if 'start' == sys.argv[1]:
				daemon.start()
			elif 'stop' == sys.argv[1]:
				daemon.stop()
			elif 'restart' == sys.argv[1]:
				daemon.restart()
			else:
				print "Unknown command"
				sys.exit(2)
			sys.exit(0)
		else:
			print "usage: %s start|stop|restart" % sys.argv[0]
			sys.exit(2)
	else:
		print 'no sensors configured: exiting...'
		sys.exit(1)
