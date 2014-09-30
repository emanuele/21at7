"""Heating schedules.
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import SGDRegressor
from scipy.optimize import fmin_powell
from desiderata import Desiderata


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
        


def loss_up(delta):
    """This is the cost of having a positive difference (delta) in
    temperature between the predicted and the desired ones.
    """
    return 10 * delta


def loss_down(delta):
    """This is the cost of having a negative difference (delta) in
    temperature between the predicted and the desired ones.
    """
    return 10 + -100.0 * delta 


def compute_loss(future_schedule, desiderata, regs, x, future_steps):
    """This is the cost of a future heating schedule (future_schedule)
    given what the user desires (desiderata) and the models (regs) to
    predict future home temperature.
    """
    xx = np.concatenate([x, np.array(future_schedule)])
    temperature_home_future = np.array([regs[i].predict(xx).squeeze() for i in range(len(future_steps))])
    delta = temperature_home_future - desiderata
    weight = np.linspace(1.0, 0.3, future_steps)
    loss = (((delta > 0) * loss_up(delta) + (delta < 0) * loss_down(delta)) * weight).sum() + np.sum(future_schedule)
    return loss


def sigmoid(x, center=0.5, slope=10.0):
    """Sigmoid function.
    """
    return 1.0 / (1.0 + np.exp(- slope * (x - center)))


def f(future_schedule, desiderata, regs, x):
    """Wrapper of sigmoid(compute_loss), i.e. the actual function to
    optimize.
    """
    return compute_loss(sigmoid(future_schedule), desiderata, regs, x)


class HeatingOptimizedSchedule(object):
    """This is the heating schedule based on prediction and
    optimization.
    """
    def __init__(self, min_examples=100, retrain_every=100, window_regression=100, future_steps=24, engine=None):
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
        self.future_steps = future_steps
        if engine is None:
            print("In order to instantiate HeatingOptimizedSchedule you need to provide a db (engine).")
            raise Exception
            
        self.engine = engine
        self.regs = [SGDRegressor(fit_intercept=True, penalty='l2', n_iter=100, shuffle=True, random_state=0, verbose=0) for i in range(self.future_steps)]
        self.desiderata = Desiderata(engine=self.engine)


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
            return np.vstack([variable[i : (i + self.window_regression + how_far_in_future) : step_within] for i in range(0, (variable.size - self.window_regression - how_far_in_future), step_between)])
        else:
            return np.vstack([variable[i : (i + self.window_regression) : step_within] for i in range(0, (variable.size - self.window_regression - how_far_in_future), step_between)])


    def create_recent_dataset(self, my_datetime, how_many, how_far_in_future):
        # 1) Retrieve external temperature from recent past:
        temperature_external = pd.read_sql_query("select timestamp, external_temperature from temperature_external where timestamp <= '%s' order by timestamp desc limit %d" % (my_datetime, how_many), self.engine).external_temperature.values
        # 2) Retrieve home temperature from recent past:
        temperature_home = pd.read_sql_query("select timestamp, home_temperature from temperature_home where timestamp <= '%s' order by timestamp desc limit %d" % (my_datetime, how_many), self.engine).home_temperature.values
        # 3) Check that records of 1 and 2 approximately match on timestamps.
        # TODO
        assert(len(temperature_home) == len(temperature_external))
        # 4) Retrieve heating schedule from recent past:
        heating = pd.read_sql_query("select timestamp, heating from heating where timestamp <= '%s' order by timestamp desc limit %d" % (my_datetime, how_many), self.engine).heating.values
        # 5) Check that records of 1 and 2 and 4 approximately match on timestamps.
        # TODO
        assert(len(temperature_home) == len(heating))
        # 6) Build trainset using a concatenation of windowed variables: [external, home, heating]:
        X = np.hstack([self.create_dataset(temperature_external, how_far_in_future = how_far_in_future),
                       self.create_dataset(temperature_home, how_far_in_future = how_far_in_future),
                       self.create_dataset(heating, how_far_in_future = how_far_in_future)])
        return X
        

    def heating_action(self, my_datetime):
        """Retrieve external and home temperatures from recent past as
        well as recent heating schedule. Then predict and optimize the
        future schedule according to desiderata.
        """
        # If there are enough data in general and enough data from previous training, do training:
        count = pd.read_sql_query("select timestamp ,count(*) from temperature_external where timestamp <= '%s'" % my_datetime, self.engine)['count(*)'].values[0]
        if count > self.min_examples:
            if (count % self.retrain_every) == 0: # (Re)train models
                # Training:
                # # 1) Retrieve external temperature from recent past:
                # temperature_external = pd.read_sql_query("select timestamp, external_temperature from temperature_external where timestamp <= '%s' order by timestamp desc limit %d" % (my_datetime, self.limit), self.engine).external_temperature.values
                # # 2) Retrieve home temperature from recent past:
                # temperature_home = pd.read_sql_query("select timestamp, home_temperature from temperature_home where timestamp <= '%s' order by timestamp desc limit %d" % (my_datetime, self.limit), self.engine).home_temperature.values
                # # 3) Check that records of 1 and 2 approximately match on timestamps.
                # # TODO
                # assert(len(temperature_home) == len(temperature_external))
                # # 4) Retrieve heating schedule from recent past:
                # heating = pd.read_sql_query("select timestamp, heating from heating where timestamp <= '%s' order by timestamp desc limit %d" % (my_datetime, self.limit), self.engine).heating.values
                # # 5) Check that records of 1 and 2 and 4 approximately match on timestamps.
                # # TODO
                # assert(len(temperature_home) == len(heating))
                # # 6) Build trainset using a concatenation of windowed variables: [external, home, heating]:
                # X = np.hstack([self.create_dataset(temperature_external, how_far_in_future = self.future_steps),
                #                self.create_dataset(temperature_home, how_far_in_future = self.future_steps),
                #                self.create_dataset(heating, how_far_in_future = self.future_steps)])

                X = self.create_recent_dataset(my_datetime, how_many=self.limit, how_far_in_future=self.future_steps)

                # 7) create home temperature vectors to be predicted
                ys = self.create_dataset(temperature_home, how_far_in_future=0)
                # 8) online training of SGDRegressors for each future timepoint
                for i in range(self.future_steps):
                    self.regs[j].fit(X, ys[:,i])
                    self.regs[j].warm_start = True # This is ESSENTIAL to keep memory of past data in current models
                # 9) save trained model in db
                # TODO

            # Retrieve last trained regs from db:
            # TODO
            for i in range(self.future_steps):
                assert(self.regs[i].coef_ is not None) # check that regs were trained before

            # Retrieve desiderata from db:
            desire = self.desiderata.get_desiderata()
            # Transform desire into the desired form:
            
            # Create x of my_datetime for prediction:
            x = self.create_recent_dataset(my_datetime, how_many=1, how_far_in_future=0)
            # Optimize future heating using regs:
            future_schedule_initial = np.zeros(self.future_steps)
            xopt = fmin_powell(f, x0=future_schedule_initial, args=[desire_vector, self.regs, x], disp=True, full_output=False, maxiter=4, ftol=1.0e-4)
            future_schedule_best = np.round(sigmoid(xopt))
            # Save optimized future heating and predicted home temperature in db:
            # TODO
            # return next heating action from the optimized heating:
            return future_schedule_best[0]
        else:
            print("Not enough data to train models.")
            raise Exception


if __name__ == '__main__':
    my_datetime = pd.datetime(2014,1,2,9,10)
    my_datetime = pd.datetime(2014,1,1,9,10)
    
