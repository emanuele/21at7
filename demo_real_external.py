import pandas as pd
from configuration import engine_string
from sqlalchemy import create_engine


if __name__ == '__main__':

    # data initially retrieved from http://cdo.ncdc.noaa.gov/qclcd/QCLCD?prior=N
    filename_real = '94728_central_park_2013.csv'
    print("Loading %s" % filename_real)
    dataset_external_temperature = pd.read_csv(filename_real)

    engine = create_engine(engine_string)
    print("Saving DataFrame to the database: %s" % engine)
    dataset_external_temperature.to_sql('temperature_external', engine, if_exists='replace', index=False)
    print("Done.")
