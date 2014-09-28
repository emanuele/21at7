import numpy as np
import pandas as pd
from simulate_external import simulate_external_temperature
from sqlalchemy import create_engine
from configuration import date_start, date_end, frequency, engine_string


if __name__ == '__main__':

    np.random.seed(0)

    print("21at7: simulation of the external temperature.")
    print("Defining initial parameters of the simulation.")
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
    dataset_external_temperature.to_sql('temperature_external', engine, if_exists='replace', index=False)
    print("Done.")

    plot = True
    if plot:
        print("Plotting.")
        import matplotlib.pyplot as plt
        plt.interactive(True)
        plt.figure()
        plt.plot(timestamps, external_temperature, 'r-', label='external')
        plt.legend()
