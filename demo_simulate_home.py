from heating import HeatingStandardSchedule
import numpy as np
import pandas as pd
from simulate_external import simulate_external_temperature
from simulate_home import HomeTemperature
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError


if __name__ == '__main__':

    from configuration import *

    print("21at7: simulation of home temperature given external temperature and heating schedule.")
    engine = create_engine(engine_string)
    print("Loading external temperatures from %s" % engine)
    limit = 100
    print("Limiting the records to the first %d." % limit)
    dataset_external_temperature = pd.read_sql_table('temperature_external', engine)[:limit]
    timestamps = dataset_external_temperature['timestamp'].values
    t_step = float(np.diff(timestamps).mean()) / 1.0e9 # differences between timestamps are originally in nanoseconds, but we want seconds
    external_temperature = dataset_external_temperature['external_temperature'].values

    try:
        print("Dropping previously existing table temperature_external.")
        pd.io.sql.execute("drop table temperature_home", con=engine)
    except OperationalError:
        print("Table 'temperature_home' does not exist.")
        pass
    
    try:
        print("Dropping previously existing table heating.")
        pd.io.sql.execute("drop table heating", con=engine)
    except OperationalError:
        print("Table 'heating' does not exist.")
        pass

    print("Starting the simulation.")
    hss = HeatingStandardSchedule(engine=engine)
    ht = HomeTemperature(T_heating, k_home_external, k_heater_on, k_heater_off, k_home_heater, t_step, engine=engine)
    heating = np.zeros(dataset_external_temperature.shape[0])
    T_home = np.zeros(dataset_external_temperature.shape[0])
    T_heater = np.zeros(dataset_external_temperature.shape[0])
    T_home[0] = T0_home
    T_heater[0] = T0_home
    for idx, (i, ex, ts) in enumerate(dataset_external_temperature.values[:-1]):
        if (idx % 20) == 0: print(ts)
        heating[idx] = hss.heating_action(ts, T_home[idx])
        T_home[idx + 1], T_heater[idx + 1] = ht.home_heater_temperature(T_home[idx], ex, T_heater[idx], heating[idx], ts)

    print("End of the simulation.")
    
    plot = True
    if plot:
        print("Plotting.")
        import matplotlib.pyplot as plt
        plt.interactive(True)
        plt.figure()
        plt.plot(timestamps, heating * T_heating, 'k-', label='heating')
        plt.plot(timestamps, external_temperature, 'r-', label='external')
        plt.plot(timestamps, T_heater, 'g-', label='heater')
        plt.plot(timestamps, T_home, 'b-', label='home')
        plt.legend()
