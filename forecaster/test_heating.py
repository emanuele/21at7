import numpy as np
import pandas as pd
from simulate_external import simulate_external_temperature
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from heating import HeatingStandardSchedule


if __name__ == '__main__':

    
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
