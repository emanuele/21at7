import numpy as np
import pandas as pd
from simulate_external import simulate_external_temperature
from sqlalchemy import create_engine
from configuration import date_start, date_end, time_step, engine_string
from datetime import datetime, timedelta


if __name__ == '__main__':

    np.random.seed(0)

    print("21at7: simulation of the external temperature.")
    print("Defining initial parameters of the simulation.")
    print("Start: %s" % date_start)
    print("End: %s" % date_end)
    print("time_step: %s" % time_step)

    print("Generating timestamps.")
    timestamps = np.array([date_start + i * time_step for i in range(int(round((date_end - date_start).total_seconds() / time_step.total_seconds())))])
    
    print("Computing external temperature...")
    external_temperature = simulate_external_temperature(timestamps=timestamps, time_step=time_step)
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
        plt.show()
