import sys,datetime,getopt

from models import SessionMaker,Schedule
import scheduler


if __name__ == '__main__':
	mainDB='sqlite:///21at7.sqlite'

	try:                                
		opts, args = getopt.getopt(sys.argv[1:], "d", ["db="])

		for opt, arg in opts:
			if opt in ("-d", "--db"):
				mainDB=arg

		other = " ".join(args)
	except getopt.GetoptError:
		print sys.argv[0], '--db SQLALCHEMY_DBURL'

	session_maker=SessionMaker(mainDB,debug=False)
	session = session_maker.get_session()
	try:
		schedules=session.query(Schedule).filter_by(what='temp',date=None)
		if schedules.count()==0:
			session.add(Schedule(day=0,what='temp',howmuch=21.0,start=datetime.time(8,00),stop=datetime.time(13,00)))
			session.add(Schedule(day=1,what='temp',howmuch=21.0,start=datetime.time(7,00),stop=datetime.time(8,00)))
			session.add(Schedule(day=1,what='temp',howmuch=21.0,start=datetime.time(12,00),stop=datetime.time(14,30)))
			session.add(Schedule(day=1,what='temp',howmuch=21.0,start=datetime.time(16,15),stop=datetime.time(22,00)))
			session.commit()
			print 'created default weekly schedule'
		schedules=session.query(Schedule).filter_by(what='temp',day=None)
		if schedules.count()==0:
			session.add(Schedule(date=datetime.date(2015,01,14),what='temp',howmuch=21.0,start=datetime.time(8,00),stop=datetime.time(12,30)))
			session.add(Schedule(date=datetime.date(2015,01,16),what='temp',howmuch=21.0,start=datetime.time(14,00),stop=datetime.time(19,00)))
			session.commit()
			print 'created default specific dates schedule'
	except:
		e = sys.exc_info()[0]
		print 'schedules query error: %s'%e
	finally:
		schedules=session.query(Schedule).filter_by(what='temp')
		try:
			session.close()
		except:
			schedules=None
			log(self,'db (schedule) session close error')

	if schedules and schedules.count()>0:
		weekly=schedules.filter_by(date=None)
		if weekly and weekly.count()>0:
			print 'saved weekly schedule:'
			for schedule in weekly:
				print '  - on %s: %.1f from %s to %s'%(schedule.day,schedule.howmuch,schedule.start.strftime('%H:%M'),schedule.stop.strftime('%H:%M'))

		dates=schedules.filter_by(day=None)
		if dates and dates.count()>0:
			print 'specific dates schedule:'
			for schedule in dates:
				print '  - on %s: %.1f from %s to %s'%(schedule.date.strftime('%d/%m/%Y'),schedule.howmuch,schedule.start.strftime('%H:%M'),schedule.stop.strftime('%H:%M'))

	else:
		print 'no schedule configured: exiting...'
