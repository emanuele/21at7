import glob,sys,time,threading
from harvesters import *

class TestRunner(threading.Thread):
	def __init__(self):
		super(TestRunner,self).__init__()
		self.setDaemon(False)

	def run(self):
		time.sleep(10)

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
		reader=lacrosse.Reader('sqlite:///21at7.sqlite',serials[0])
		reader.start()

		runner=TestRunner()
		runner.start()
