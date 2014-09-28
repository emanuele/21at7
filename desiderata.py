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


if __name__ == '__main__':

    desire = [(6, 45, 8, 0, 22.0),
              (17, 30, 23, 30, 22.0)]
    tmp = dict(zip(('start_hour', 'start_min', 'stop_hour', 'stop_min', 'temperature'), zip(*desire)))
    desire = pd.DataFrame(tmp)
    print(desire)

    from sqlalchemy import create_engine
    from configuration import engine_string
    engine = create_engine(engine_string)    
    desiderata = Desiderata(desire, engine)
    desire = desiderata.get_desiderata()
    print(desire)

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

