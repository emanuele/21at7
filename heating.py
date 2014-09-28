"""Heating schedules.
"""
import pandas as pd

class HeatingStandardSchedule(object):
    """This is the standard (naive) heating schedule most of people
    have at home.
    """
    def __init__(self, T_min=20, T_max=22, off_hours=(23,4), off_months=(6,8), T_warning=10.0, engine=None):
        self.T_min = T_min
        self.T_max = T_max
        self.off_hours = off_hours
        self.off_months = off_months
        self.T_warning = T_warning
        self.heating = 0.0
        self.engine = engine

        
    def heating_action(self, my_datetime, my_temperature):
        self.heating_previous = self.heating
        if my_temperature < self.T_warning: # if it is too cold turn heating on
            self.heating = 1.0
        elif my_datetime.month >= self.off_months[0] and my_datetime.month <= self.off_months[1]: # No heating in Summer (off_months)
            self.heating = 0.0
        elif (my_datetime.hour >= self.off_hours[0] or my_datetime.hour <= self.off_hours[1]): # No heating during the night (off_hours)
            self.heating = 0.0
        else:
            if my_temperature < self.T_min: # If it is too cold, turn heating on
                self.heating = 1.0
            elif my_temperature > self.T_max: # If it is too hot, turn heating off
                self.heating = 0.0
            else: # Otherwise, keep previous schedule:
                self.heating = self.heating_previous

        if self.engine is not None:
            df = pd.DataFrame({'timestamp': [my_datetime],
                               'heating': [self.heating],
                               })
            df.to_sql('heating', self.engine, if_exists='append', index=False)

        return self.heating
        


class HeatingOptimizedSchedule(object):
    """This is the heating schedule based on prediction and
    optimization.
    """
    def __init__(self, engine):
        self.engine = engine
        self.limit = 100
        self.regs = None
        

    def heating_action(self, my_datetime):
        """Retrieve external and home temperatures from recent past as
        well as recent heating schedule. Then predict and optimize the
        future schedule according to desiderata.
        """
        # If there are enough data in general and enough data from previous training, do training:
        count = pd.read_sql_query("select timestamp ,count(*) from heating where timestamp <= '%s'" % my_datetime, engine)['count(*)'].values[0]
        if count > 100 and count_from_last_training > 100:
            # Training:
            # 1) Retrieve external temperature from recent past:
            temperature_external = pd.read_sql_query("select timestamp, external_temperature from temperature_external where timestamp <= '%s' order by timestamp desc limit %d" % (my_datetime, self.limit), self.engine)
            # 2) Retrieve home temperature from recent past:
            temperature_home = pd.read_sql_query("select timestamp, home_temperature from temperature_home where timestamp <= '%s' order by timestamp desc limit %d" % (my_datetime, self.limit), self.engine)
            # 3) Check that records of 1 and 2 approximately match on timestamps.
            # TODO
            # 4) Retrieve heating schedule from recent past:
            heating = pd.read_sql_query("select timestamp, heating from heating where timestamp <= '%s' order by timestamp desc limit %d" % (my_datetime, self.limit), self.engine)
            # 5) Check that records of 1 and 2 and 4 approximately match on timestamps.
            # TODO
            # 6) Build trainset using a concatenation of windowed [external, home, heating]:
            # TODO
            # 7) create home temperature vector to be predicted
            # TODO
            # 8) online training of SGDRegressor for each future timepoint
            # TODO
            # 9) save trained model in db
            # TODO

            # Retrieve last trained regs.
            # Create x of my_datetime.
            # Optimize future heating using regs.
            # Save optimized future heating and predicted home temperature in db
            # return next heating action from the optimized heating.
            
            pass



if __name__ == '__main__':

    my_datetime = pd.datetime(2014,1,2,9,10)
    my_datetime = pd.datetime(2014,1,1,9,10)
    
