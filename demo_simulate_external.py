import numpy as np
import pandas as pd
from simulate_external import simulate_external_temperature
from sqlalchemy import create_engine
from configuration import engine_string


if __name__ == '__main__':

    np.random.seed(0)

    print("21at7: simulation of the external temperature.")
    print("Defining initial parameters of the simulation.")
    date_start = pd.datetime(2014, 1, 1, 0, 0, 0)
    date_end = pd.datetime(2014, 12, 31, 23, 59, 59)
    frequency = '10min'
    print("Start: %s" % date_start)
    print("End: %s" % date_end)
    print("Frequency: %s" % frequency)

    print("Generating timestamps.")
    timestamps = pd.date_range(start=date_start, end=date_end, freq=frequency)
    
    print("Computing external temperature...")
    external_temperature = simulate_external_temperature(timestamps=timestamps)
    print("Done.")

    print("Creating DataFrame.")
    dataset_external_temperature = pd.DataFrame({'timestamp': timestamps,
                                                 'external_temperature': external_temperature,
                                                 })

    engine = create_engine(engine_string)
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
