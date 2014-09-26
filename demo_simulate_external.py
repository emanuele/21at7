import numpy as np
import pandas as pd
from simulate_external import simulate_external_temperature
from sqlalchemy import create_engine


if __name__ == '__main__':

    np.random.seed(0)

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

    print("Creating DataFrame.")
    dataset_external_temperature = pd.DataFrame({'timestamp': timestamps,
                                                 'external_temperature': external_temperature,
                                                 })

    engine = create_engine('sqlite:///21at7.sqlite')
    print("Saving DataFrame to the database: %s" % engine)
    dataset_external_temperature.to_sql('temperature_external', engine, if_exists='replace')
    print("Done.")

    plot = True
    if plot:
        print("Plotting.")
        import matplotlib.pyplot as plt
        plt.interactive(True)
        plt.figure()
        plt.plot(timestamps, external_temperature, 'r-', label='external')
        plt.legend()
