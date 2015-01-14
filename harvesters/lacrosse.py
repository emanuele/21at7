# -*- coding: utf-8 -*-
import datetime,time,serial,threading,sys,traceback

from models import SessionMaker,Reading,Sensor,Measure


def log(instance,msg):
	if instance.debug:
		sys.stderr.write('[%s.%s] %s\n'%(instance.module_name, instance.class_name, msg))
		sys.stderr.flush()


class Reader(threading.Thread):
	def __init__(self, dbUrl, serName, debug=False, dbdebug=False):
		super(Reader,self).__init__()
		self.setDaemon(True)
		self.active=False
		self.debug=debug
		self.error_count=0
		self.module_name=__name__.split('.',1)[1]
		self.class_name=self.__class__.__name__

		self.dbUrl=dbUrl
		self.session_maker=SessionMaker(dbUrl,debug=dbdebug)

		self.serName=serName
		self.ser = serial.Serial(serName,57600,timeout=2)
		
		log(self,'initialized with serial %s'%serName)

	def run(self):
		log(self,'started.')

		self.active=True
		while self.active:
			session=None
			try:
				msg=self.ser.readline()
				if msg:
					msg=msg.strip(' \t\n\r').replace('  ',' ')
					if msg.startswith('D:'):
						#log(self,'msg: %s'%msg)
						session = self.session_maker.get_session()
						session.add(Reading(id=datetime.datetime.now(),harvester=self.module_name,data=msg))
						session.commit()
					#else:
					#	log(self,'unknown msg: %s'%msg)
				#else:
				#	log(self,'no msg...')
				self.error_count=0
			except:
				e = sys.exc_info()[0]
				log(self,'ERROR: %s'%e)
				traceback.print_exc()
				if self.error_count==10:
					log(self,'TOO MANY CONSECUTIVE ERRORS!')
					self.active=False
				else:
					self.error_count+=1
			finally:
				try:
					if session: session.close()
				except:
					e = sys.exc_info()[0]
					log(self,'db session close error: %s'%e)
					traceback.print_exc()
		if self.active: self.active=False

		try:
			if self.ser and self.ser.isOpen(): self.ser.close()
		except:
			log(self,'serial close error')

		log(self,'ended!')


class Cleaner(threading.Thread):
	def __init__(self, dbUrl, debug=False, dbdebug=False):
		super(Cleaner,self).__init__()
		self.setDaemon(True)
		self.active=False
		self.debug=debug
		self.error_count=0
		self.module_name=__name__.split('.',1)[1]
		self.class_name=self.__class__.__name__

		self.dbUrl=dbUrl
		self.session_maker=SessionMaker(dbUrl,debug=dbdebug)

		self.sensors={}
		session = self.session_maker.get_session()
		try:
			sensors=session.query(Sensor).filter_by(harvester=self.module_name)
			for sensor in sensors:
				#log(self,'sensor: %s'%sensor.address)
				self.sensors[sensor.address]=sensor
		except:
			e = sys.exc_info()[0]
			log(self,'sensors query error: %s'%e)
		finally:
			try:
				session.close()
			except:
				e = sys.exc_info()[0]
				log(self,'db (sensors) session close error: %s'%e)
				traceback.print_exc()

		log(self,'initialized')

	def run(self):
		log(self,'started.')

		self.active=True
		while self.active:
			session=None
			try:
				session = self.session_maker.get_session()
				readings=session.query(Reading)
				if readings.count()>0:
					for reading in readings.order_by(Reading.id).limit(10):
						#log(self,reading.id)
						if reading.data and reading.data.startswith('D:'):
							dati=reading.data.split(' ')
							if len(dati)==2:
								sensor_address=dati[0][2:4]
								if sensor_address in self.sensors:
									sensor=self.sensors[sensor_address]
									sensed=dati[1].split(':')
									now=datetime.datetime.now()
									try:
										session.add(Measure(sensor_id=sensor.id,when=reading.id,what='temp',howmuch=sensed[0]))
										session.add(Measure(sensor_id=sensor.id,when=reading.id,what='hum',howmuch=sensed[1]))
										session.commit()
										log(self, u'%s: %s °C, %s %%rH'%(sensor.desc,sensed[0],sensed[1]))
									except:
										e = sys.exc_info()[0]
										log(self,'MEASURE ERROR: %s'%e)
										traceback.print_exc()
									#data = [float(val) for val in sensed]
								else:
									log(self,'unkown sensor: %s'%sensor_address)
							session.delete(reading)
							session.commit()
					time.sleep(.1)
				else:
					log(self,'nothing to clean: will have a little longer nap...')
					time.sleep(2)
				self.error_count=0
			except:
				e = sys.exc_info()[0]
				log(self,'ERROR: %s'%e)
				traceback.print_exc()
				if self.error_count==10:
					log(self,'TOO MANY CONSECUTIVE ERRORS!')
					self.active=False
				else:
					self.error_count+=1
			finally:
				try:
					if session: session.close()
				except:
					e = sys.exc_info()[0]
					log(self,'db (run) session close error: %s'%e)
					traceback.print_exc()
		if self.active: self.active=False

		log(self,'ended!')
