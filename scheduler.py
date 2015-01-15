import sys,datetime,getopt,time

from config import mainDB,lacrosse_serial,ciseco_serial
from models import SessionMaker,Schedule


def log(instance,msg):
	if instance.debug:
		sys.stderr.write('[SCHEDULER] %s %s\n'%(time.strftime("%Y-%m-%d %H:%M:%S"), msg))


class Scheduler():
	def __init__(self, dbUrl, debug=False, dbdebug=False):
		self.debug=debug

		self.dbUrl=dbUrl
		self.session_maker=SessionMaker(dbUrl,debug=dbdebug)

		log(self,'initialized')

	def desired(self,zone_id,what='temp',when=None):
		if not when: when=datetime.datetime.now()
		day=datetime.date(when.year,when.month,when.day)
		hour=datetime.time(when.hour,when.minute,when.second)
		log(self,'hour: %s'%str(hour))

		try:
			session = self.session_maker.get_session()

			log(self,'day: %s'%str(day))
			bydate=session.query(Schedule).filter(Schedule.zone_id==zone_id,Schedule.what==what,Schedule.date==day,Schedule.start<=hour,Schedule.stop>=hour).order_by(Schedule.howmuch.desc()).first()
			if bydate:
				log(self,'by date schedule: %.1f'%bydate.howmuch)
				return bydate.howmuch
			else:
				log(self,'weekday: %d'%when.weekday())
				weekly=session.query(Schedule).filter(Schedule.zone_id==zone_id,Schedule.what==what,Schedule.day==when.weekday(),Schedule.start<=hour,Schedule.stop>=hour).order_by(Schedule.howmuch.desc()).first()
				if weekly:
					log(self,'from weekly schedule: %.1f'%weekly.howmuch)
					return weekly.howmuch

		except:
			e = sys.exc_info()[0]
			log(self,'scheduler query error')
		finally:
			try:
				session.close()
			except:
				log(self,'db (scheduler) session close error')

		return None
