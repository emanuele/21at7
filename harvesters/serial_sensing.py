import glob,datetime,sys,serial

from models import Session,Reading


class Reader:
	def __init__(self, serName):
		self.ser = serial.Serial(serName,57600,timeout=2)
		self.active=True

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


if __name__ == '__main__':
	if len(sys.argv) < 2:
		serials=glob.glob('/dev/ttyUSB*') + glob.glob('/dev/tty.usbserial-*')
	else:
		serials=[ sys.argv[1] ]


	if len(serials)==0:
		print 'no supported serial device found among tty devices:'
		for serName in glob.glob('/dev/tty*'): print '  -', serName

	elif len(serials)!=1:
		print 'select one of these devices:'
		for serName in serials: print '  -', serName

	else:
		print 'serial name:', serials[0]
		reader=Reader(serials[0])
		print 'serial DONE.'
