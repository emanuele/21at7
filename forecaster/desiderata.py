import numpy as np
import pandas as pd
import datetime


class Desiderata(object):
    def __init__(self, desire=None, engine=None):
        self.engine = engine
        self.desire = None
        if desire is not None:
            self.set_desiderata(desire)


    def set_desiderata(self, desire=None):
        if desire is not None:
            self.desire = desire
        
        if self.engine is not None:
            print("Storing desiderata into %s" % self.engine)
            self.desire.to_sql('desiderata', self.engine, if_exists='replace', index=False)


    def get_desiderata(self):
        if self.engine is not None:
            print("Retrieving desiderata from %s" % self.engine)
            self.desire = pd.read_sql_table('desiderata', self.engine)

        return self.desire


    def create_vector(self, desire, my_datetime, n_steps, time_step, T_warning):
        """Create a vector representation of desire starting form
        my_datetime with n_steps values, one every time_step.

        This function is helpful to convert a desire in a vector for
        the optimization step.
        """
        if type(my_datetime) == type(u''): my_datetime = np.datetime64(my_datetime)
        my_datetime = my_datetime.astype(object) # this transform string into datetime64 first and datetime.datetime then
        time_vector = np.array([my_datetime + i * time_step for i in range(n_steps)])
        desire_vector = np.ones(n_steps) * T_warning
        for row in range(desire.shape[0]):
            desire_start = datetime.time(desire.start_hour[row], desire.start_minute[row])
            desire_stop = datetime.time(desire.stop_hour[row], desire.stop_minute[row])
            for i, tv in enumerate(time_vector):
                tv_time = datetime.time(tv.hour, tv.minute)
                if tv_time >= desire_start and tv_time <= desire_stop:
                    desire_vector[i] = desire.temperature[row]

        return desire_vector



if __name__ == '__main__':

    desire = [(7, 0, 8, 0, 21.0),
              (17, 30, 23, 30, 21.0)]
    tmp = dict(zip(('start_hour', 'start_minute', 'stop_hour', 'stop_minute', 'temperature'), zip(*desire)))
    desire = pd.DataFrame(tmp)
    print(desire)

    from sqlalchemy import create_engine
    from configuration import engine_string
    engine = create_engine(engine_string)    
    desiderata = Desiderata(desire, engine)
    desire = desiderata.get_desiderata()
    print(desire)

    print("")
    print("Testing creation of vectors:")
    n_steps = 24
    time_step = timedelta(minutes=10)
    T_warning = 10.0
    my_datetime = np.datetime64(u'2014-01-02 06:00:00+00:00')
    print(my_datetime)
    print desiderata.create_vector(desire, my_datetime, n_steps, time_step, T_warning)
    my_datetime = np.datetime64(u'2014-01-02 21:00:00+00:00')
    print(my_datetime)
    print desiderata.create_vector(desire, my_datetime, n_steps, time_step, T_warning)

    # Old Attempts
    # # desire: start, stop and temperature:
    # desire = [(datetime.time(6,45,0), datetime.time(8,0,0), 22.0),
    #           (datetime.time(17,30,0), datetime.time(23,30,0), 22.0)]

    # # desire = [(np.datetime64(pd.datetime(1970, 1, 1, start.hour, start.minute, start.second)), np.datetime64(pd.datetime(1970, 1, 1, stop.hour, stop.minute, stop.second)), temperature) for start, stop, temperature in desire]
    # tmp = dict(zip(('start', 'stop', 'temperature'), zip(*desire)))
    # # tmp['start'] = np.array(tmp['start'])
    # # tmp['stop'] = np.array(tmp['stop'])
    # desire = pd.DataFrame(tmp)

    # if pd.__version__ < '0.15':
    #     # Workaround of pandas BUG: https://github.com/pydata/pandas/issues/6932 (Closed in 0.15)
    #     self.desire.start = self.desire.start.apply(time_to_datetime).astype(np.datetime64) # Change datetime.time into pd.datetime
    #     self.desire.stop = self.desire.stop.apply(time_to_datetime).astype(np.datetime64) # Change datetime.time into pd.datetime

    # desire = [(pd.datetime(1, 1, 1, start.hour, start.minute, start.second), pd.datetime(1, 1, 1, stop.hour, stop.minute, stop.second), temperature) for start, stop, temperature in desire]            
    # desire = pd.DataFrame(dict(zip(('start', 'stop', 'temperature'), zip(*desire))))

    # if pd.__version__ < '0.15':
    #     # Workaround of pandas BUG: https://github.com/pydata/pandas/issues/6932 (Closed in 0.15)
    #     self.desire.start = self.desire.start.apply(datetime_to_time) # Change pd.datetime into datetime.time
    #     self.desire.stop = self.desire.stop.apply(datetime_to_time) # Change pd.datetime into datetime.time

    # def time_to_datetime(t, year=1, month=1, day=1):
    #     return np.datetime64(pd.datetime(year, month, day, t.hour, t.minute, t.second, t.microsecond))
    
    # def datetime_to_time(d):
    #     return datetime.time(d)


