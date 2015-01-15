import sys,datetime,getopt,traceback

from config import mainDB,lacrosse_serial,ciseco_serial
from models import SessionMaker,Schedule,Zone
from scheduler import Scheduler


if __name__ == '__main__':
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
		zones=session.query(Zone)
		if zones.count()==0:
			zone1 = Zone(desc='inside')
			session.add(zone1)
			zones=session.query(Zone)
		zone1=zones.first()
		print 'zone:',zone1

		schedules=session.query(Schedule).filter_by(what='temp',date=None)
		if schedules.count()==0:
			session.add(Schedule(zone_id=zone1.id,day=7,what='temp',howmuch=21.0,start=datetime.time(8,00),stop=datetime.time(13,00)))
			session.add(Schedule(zone_id=zone1.id,day=2,what='temp',howmuch=21.0,start=datetime.time(7,00),stop=datetime.time(8,00)))
			session.add(Schedule(zone_id=zone1.id,day=2,what='temp',howmuch=21.0,start=datetime.time(12,00),stop=datetime.time(14,30)))
			session.add(Schedule(zone_id=zone1.id,day=2,what='temp',howmuch=21.0,start=datetime.time(16,15),stop=datetime.time(22,00)))
			session.commit()
			print 'created default weekly schedule'
		schedules=session.query(Schedule).filter_by(what='temp',day=None)
		if schedules.count()==0:
			session.add(Schedule(zone_id=zone1.id,date=datetime.date(2015,01,15),what='temp',howmuch=21.0,start=datetime.time(00,00),stop=datetime.time(02,00)))
			session.add(Schedule(zone_id=zone1.id,date=datetime.date(2015,01,16),what='temp',howmuch=21.0,start=datetime.time(14,00),stop=datetime.time(19,00)))
			session.commit()
			print 'created default specific dates schedule'
	except:
		e = sys.exc_info()[0]
		print 'schedules query error: %s'%e
		traceback.print_exc()
	finally:
		schedules=session.query(Schedule).filter_by(what='temp')

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

		sched=Scheduler(mainDB,debug=True)
		temp=sched.desired(zone1.id)
		if temp:
			print 'desired temperature in "%s": %.1f'%(zone1.desc,temp)
		else:
			print 'unknown desired temperature... will fall back to minimum!'

	else:
		print 'no schedule configured: exiting...'

	try:
		session.close()
	except:
		schedules=None
		log(self,'db (schedule) session close error')
