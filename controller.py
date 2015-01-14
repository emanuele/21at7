import glob,sys,time,threading,getopt,os,tempfile

from config import mainDB,lacrosse_serial,ciseco_serial,logdir
from models import SessionMaker,Sensor
from harvesters import *
from daemon import Daemon


def log(msg):
	sys.stderr.write('[CLEANER] %s %s\n'%(time.strftime("%Y-%m-%d %H:%M:%S"), msg))


class Controller(Daemon):
	def run(self):
		if lacrosse_serial:
			self.lacrosse_cleaner=lacrosse.Cleaner(mainDB,debug=False,dbdebug=False)
			self.lacrosse_cleaner.start()
		else:
			log('no lacrosse sensors')

		if ciseco_serial:
			self.ciseco_cleaner=ciseco.Cleaner(mainDB,debug=False,dbdebug=False)
			self.ciseco_cleaner.start()
		else:
			log('no ciseco sensors')

		log('CONTROLLER STARTED')
		while True:
			time.sleep(1)
		log('CONTROLLER ENDED')


if __name__ == '__main__':
	pid=os.path.join(os.getcwd(),'21at7_controller.pid')
	logfile=os.path.join(logdir,'21at7_controller.log')
	daemon=Controller(pid,stdout=logfile,stderr=logfile)
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
