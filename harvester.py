import glob,sys,time,threading,getopt,os

from config import mainDB,lacrosse_serial,ciseco_serial,logdir
from models import SessionMaker,Sensor
from harvesters import *
from daemon import Daemon


class Harvester(Daemon):
	def run(self):
		if lacrosse_serial:
			self.lacrosse_reader=lacrosse.Reader(mainDB,lacrosse_serial,debug=False,dbdebug=False)
			self.lacrosse_reader.start()
		else:
			sys.stderr.write('no lacrosse sensors')

		if ciseco_serial:
			self.ciseco_reader=ciseco.Reader(mainDB,ciseco_serial,debug=False,dbdebug=False)
			self.ciseco_reader.start()
		else:
			sys.stderr.write('no ciseco sensors\n')

		sys.stderr.write('HARVESTING STARTED\n')
		while True:
			time.sleep(1)
		sys.stderr.write('HARVESTING ENDED\n')


if __name__ == '__main__':
	if lacrosse_serial or ciseco_serial:
		pid=os.path.join(os.getcwd(),'21at7_harvester.pid')
		logfile=os.path.join(logdir,'21at7_harvester.log')
		daemon=Harvester(pid,stdout=logfile,stderr=logfile)
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
