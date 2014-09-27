"""Heating schedules.
"""


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
            df.to_sql('heating', self.engine, if_exists='append')

        return self.heating
        


if __name__ == '__main__':

    import numpy as np
    import pandas as pd
    from simulate_external import simulate_external_temperature
    from sqlalchemy import create_engine
    from sqlalchemy.exc import OperationalError
    
    engine = create_engine('sqlite:///21at7.sqlite')
    dataset_external_temperature = pd.read_sql_table('temperature_external', engine)[:100]
    timestamps = dataset_external_temperature['timestamp'].values
    external_temperature = dataset_external_temperature['external_temperature'].values
    try:
        pd.io.sql.execute("drop table heating", con=engine)
    except OperationalError:
        print("Table 'heating' does not exist.")
        pass
    
    hss = HeatingStandardSchedule(engine=engine)
    heating = np.zeros(dataset_external_temperature.shape[0])
    for idx, (i, et, ts) in enumerate(dataset_external_temperature.values):
        if (idx % 20) == 0: print(idx)
        heating[idx] = hss.heating_action(ts, et)
    
    plot = True
    if plot:
        print("Plotting.")
        import matplotlib.pyplot as plt
        plt.interactive(True)
        plt.figure()
        plt.plot(timestamps, external_temperature, 'r-', label='external')
        plt.plot(timestamps, heating * external_temperature.max(), 'k-', label='heating')
        plt.legend()
