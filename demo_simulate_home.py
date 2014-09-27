from heating import HeatingStandardSchedule
import numpy as np
import pandas as pd
from simulate_external import simulate_external_temperature
from simulate_home import HomeTemperature
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError


if __name__ == '__main__':

    # Constants for heat transfer:
    k_home_external = 1.0 / 3600.0 / 2.0 # how fast home temperature changes due to external temperature
    k_home_heater = 1.0 / 3600.0 # how fast home temperature changes due to heater temperature
    k_heater_on = 1.0 / 600.0 # how fast heater temperature changes when heating is on
    k_heater_off = 1.0 / 1200.0 # how fast heater temperature changes when heating is off

    T_heating = 50.0 # temperature of the heating system, i.e. of the hot water produced
    T0_home = 20.0 # initial house temperature # initial house temperature at time 0.

    engine = create_engine('sqlite:///21at7.sqlite')
    dataset_external_temperature = pd.read_sql_table('temperature_external', engine)[:100]
    timestamps = dataset_external_temperature['timestamp'].values
    t_step = float(np.diff(timestamps).mean()) / 1.0e9
    external_temperature = dataset_external_temperature['external_temperature'].values
    try:
        pd.io.sql.execute("drop table temperature_home", con=engine)
    except OperationalError:
        print("Table 'temperature_home' does not exist.")
        pass
    
    try:
        pd.io.sql.execute("drop table heating", con=engine)
    except OperationalError:
        print("Table 'heating' does not exist.")
        pass
    
    hss = HeatingStandardSchedule(engine=engine)
    ht = HomeTemperature(T_heating, k_home_external, k_heater_on, k_heater_off, k_home_heater, t_step, engine=engine)
    heating = np.zeros(dataset_external_temperature.shape[0])
    T_home = np.zeros(dataset_external_temperature.shape[0])
    T_heater = np.zeros(dataset_external_temperature.shape[0])
    T_home[0] = T0_home
    T_heater[0] = T0_home
    for idx, (i, ex, ts) in enumerate(dataset_external_temperature.values[:-1]):
        if (idx % 20) == 0: print(idx)
        heating[idx] = hss.heating_action(ts, T_home[idx])
        T_home[idx + 1], T_heater[idx + 1] = ht.home_heater_temperature(T_home[idx], ex, T_heater[idx], heating[idx], ts)

    
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
