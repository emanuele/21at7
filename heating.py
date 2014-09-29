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
    def __init__(self, min_examples=100, retrain_every=100, window_regression=100, engine=None):
        """
        TODO
        
        window_regression : int
            The window size of the variable used for regression, in
            timesteps
        """
        self.limit = 100
        self.min_examples = min_examples
        self.retrain_every = retrain_every
        self.window_regression = window_regression 
        if engine is None:
            print("In order to instantiate HeatingOptimizedSchedule you need to provide a db (engine).")
            
        self.engine = engine
        self.regs = None


    def create_dataset(self, variable, how_far_in_future, step_within=1, step_between=1, use_future=False):
        """Given the timecourse of a variable, the window-size for
        regression and how many timesteps you want to predict in future,
        this function creates a dataset by stacking overlapping segments
        of the variable in order to create the vectorial description of
        the examples, one per timestep.

        Parameters
        ----------
        variable : iterable of float
            The timecourse of a variable
        how_far_in_future : int
            how many timesteps ahead in future you want to predict.
        step_within : int
            Distance in timesteps between successive values within the
            window of regression
        step_between : int
            Distance in time between successive examples
        """
        if use_future:
            return np.vstack([variable[i : i+self.window_regression+self.how_far_in_future : step_within] for i in range(0, variable.size - self.window_regression - self.how_far_in_future, step_between)])
        else:
            return np.vstack([variable[i : i+self.window_regression : step_within] for i in range(0, variable.size - self.window_regression - self.how_far_in_future, step_between)])


        

    def heating_action(self, my_datetime):
        """Retrieve external and home temperatures from recent past as
        well as recent heating schedule. Then predict and optimize the
        future schedule according to desiderata.
        """
        # If there are enough data in general and enough data from previous training, do training:
        count = pd.read_sql_query("select timestamp ,count(*) from heating where timestamp <= '%s'" % my_datetime, self.engine)['count(*)'].values[0]
        count_from_last_training = 110 # TODO
        if count > self.min_examples and count_from_last_training > self.retrain_every:
            # Training:
            # 1) Retrieve external temperature from recent past:
            temperature_external = pd.read_sql_query("select timestamp, external_temperature from temperature_external where timestamp <= '%s' order by timestamp desc limit %d" % (my_datetime, self.limit), self.engine)
            # 2) Retrieve home temperature from recent past:
            temperature_home = pd.read_sql_query("select timestamp, home_temperature from temperature_home where timestamp <= '%s' order by timestamp desc limit %d" % (my_datetime, self.limit), self.engine)
            # 3) Check that records of 1 and 2 approximately match on timestamps.
            # TODO
            assert(len(temperature_home) == len(temperature_external))
            # 4) Retrieve heating schedule from recent past:
            heating = pd.read_sql_query("select timestamp, heating from heating where timestamp <= '%s' order by timestamp desc limit %d" % (my_datetime, self.limit), self.engine)
            # 5) Check that records of 1 and 2 and 4 approximately match on timestamps.
            # TODO
            assert(len(temperature_home) == len(heating))
            # 6) Build trainset using a concatenation of windowed [external, home, heating]:
            dataset_external = np.hstack([self.create_dataset(temperature_external, how_far_in_future=1),
                                          self.create_dataset(temperature_home, how_far_in_future=1),
                                          self.create_dataset(heating, how_far_in_future=1)])
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
    
