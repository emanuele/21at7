import datetime,serial,threading

from models import Session,Reading


class Reader(threading.Thread):
	def __init__(self, dbUrl, serName):
		super(Reader,self).__init__()
		self.setDaemon(True)

		self.name=__name__.split('.',1)[1]

		self.dbUrl=dbUrl
		self.Session=Session(dbUrl)

		self.serName=serName
		self.ser = serial.Serial(serName,57600,timeout=2)
		self.active=True
		
		self.log('initialized serial %s'%serName)

	def log(self,msg):
		print '[%s] %s'%(__name__, msg)

	def run(self):
		self.log('reader started.')

		while self.active and self.ser.isOpen():
			try:
				msg=self.ser.readline()
				if msg:
					msg=msg.strip()
					self.log('msg: %s'%msg)
					if msg.startswith('D:'):
						session = self.Session.get_session()
						session.add(Reading(id=datetime.datetime.now(),type=self.name,data=msg))
						session.commit()
					else:
						self.log('*** unknown msg ***')
				#else:
				#	self.log('no msg...')
			except KeyboardInterrupt:	
				self.ser.close()
			except:
				print 'ERROR!'
				self.active=False
		try:
			if self.ser and self.ser.isOpen(): self.ser.close()
		except:
			self.log('serial close error')

		self.log('reader ended!')
