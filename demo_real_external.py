import pandas as pd
from configuration import engine_string
from sqlalchemy import create_engine
from configuration import date_start, date_end, time_step, engine_string
from scipy import interpolate


if __name__ == '__main__':

    # data initially retrieved from http://cdo.ncdc.noaa.gov/qclcd/QCLCD?prior=N
    filename_real = '94728_central_park_2013.csv'
    print("Loading %s" % filename_real)
    dataset_external_temperature = pd.read_csv(filename_real)

    print("")
    print("Resampling temperature data at specified time_step.")
    print("date_start: %s" % date_start)
    print("date_end: %s" % date_end)
    print("time_step: %s" % time_step)
    print("Converting timestamps to seconds.")
    timestamp_sec = np.array([(ts - date_start).total_seconds() for ts in timestamp])
    print("Creating new timestamps at the desired frequency.")
    timestamp_desired = np.array([date_start + i * time_step for i in range(int(round((date_end - date_start).total_seconds() / time_step.total_seconds())))])
    timestamp_desired_sec = np.array([(ts - date_start).total_seconds() for ts in timestamp_desired])
    print("Using interpolation to get temperatures at desired timesteps.")
    f = interpolate.interp1d(timestamp_sec, temperature, kind='linear')
    temperature_desired = f(timestamp_desired_sec)

    print("Creating DataFrame.")
    dataset_external_temperature = pd.DataFrame({'timestamp': timestamp_desired,
                                                 'external_temperature': temperature_desired,
                                                 })

    engine = create_engine(engine_string)
    print("Saving DataFrame to the database: %s" % engine)
    dataset_external_temperature.to_sql('temperature_external', engine, if_exists='replace', index=False)
    print("Done.")
