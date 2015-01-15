import glob,sys,time,threading,getopt,os,tempfile,traceback

from config import mainDB,lacrosse_serial,ciseco_serial,logdir
from models import SessionMaker,Sensor,Zone,Measure
from harvesters import *
from scheduler import Scheduler

from daemon import Daemon


def log(msg):
	sys.stderr.write('[CONTROLLER] %s %s\n'%(time.strftime("%Y-%m-%d %H:%M:%S"), msg))


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

		self.scheduler=Scheduler(mainDB,debug=False)
		self.session_maker=SessionMaker(mainDB,debug=False)

		log('CONTROLLER STARTED')
		while True:
			
			zones=None
			try:
				session = self.session_maker.get_session()
				zones=session.query(Zone)
				for zone in zones.filter(Zone.desc!='outside'):
					#log('zone id: %d'%(zone.id))
					desired=self.scheduler.desired(zone_id=zone.id)
					#log('desired temp in "%s": %.1f'%(zone.desc,desired))
					min=None
					for sensor in zone.sensors:
						#log('sensor: %s'%sensor.desc)
						for measure in sensor.measurements:
							if measure.what=='temp':
								#log('%s: %.1f'%(measure.what,measure.howmuch))
								if min==None or measure.howmuch<min:
									min=measure.howmuch
					if min: 
						log('min: %.1f'%min)
						if min<(desired-0.5):
							log('heating ON in "%s"'%zone.desc)
						elif min>(desired+0.5):
							log('heating OFF in "%s"'%zone.desc)
					#latest=zone.sensors.measurements.order_by(Measure.when.desc(),Measure.howmuch).first()
					#print 'latest measurement:',latest
			except:
				e = sys.exc_info()[0]
				log('zones query error: %s'%e)
				traceback.print_exc()
			finally:
				try:
					session.close()
				except:
					zones=None
					log('db (zones) session close error')

			time.sleep(5)
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
