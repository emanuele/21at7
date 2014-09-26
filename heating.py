"""Heating schedules.
"""


class HeatingStandardSchedule(object):
    """This is the standard (naive) heating schedule most of people
    have at home.
    """
    def __init__(self, T_min=20, T_max=22, off_hours=(23,4), off_months=(6,8), T_warning=10.0):
        self.T_min = T_min
        self.T_max = T_max
        self.off_hours = off_hours
        self.off_months = off_months
        self.T_warning = T_warning
        self.heating = 0.0

        
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

        return self.heating
        


if __name__ == '__main__':

    import numpy as np
    import pandas as pd
    from simulate_external import simulate_external_temperature

    
    print("Defining initial parameters of the simulation.")
    timezone = 'Europe/Rome'
    date_start = pd.Timestamp(pd.datetime(2014, 1, 1, 0, 0, 0), tz=timezone)
    date_end = pd.Timestamp(pd.datetime(2014, 12, 31, 23, 59, 59), tz=timezone)
    frequency = '10min'
    print("Timezone: %s" % timezone)
    print("Start: %s" % date_start)
    print("End: %s" % date_end)
    print("Frequency: %s" % frequency)

    print("Generating timestamps.")
    timestamps = pd.date_range(start=date_start, end=date_end, freq=frequency, tz=timezone)

    print("Computing external temperature...")
    external_temperature = simulate_external_temperature(timestamps=timestamps)
    print("Done.")

    # from sqlalchemy import create_engine
    # engine = create_engine('sqlite:///21at7.sqlite')    
    # dataset_external_temperature = pd.read_sql_table('temperature_external', engine)
    # timestamps = dataset_external_temperature.timestamp.values
    # external_temperature = dataset_external_temperature.external_temperature.values

    hss = HeatingStandardSchedule()
    heating = np.array([hss.heating_action(ts, et) for (ts, et) in zip(timestamps, external_temperature)])
    

    plot = True
    if plot:
        print("Plotting.")
        import matplotlib.pyplot as plt
        plt.interactive(True)
        plt.figure()
        plt.plot(timestamps, external_temperature, 'r-', label='external')
        plt.plot(timestamps, heating * external_temperature.max(), 'k-', label='heating')
        plt.legend()
