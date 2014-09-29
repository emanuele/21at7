"""Simulate the external temperature.
"""

import numpy as np
from datetime import datetime, timedelta
import time


def autocorrelated_noise(n_timepoints, window_size_timepoints=100):
    """Generate 1D autocorrelated noise with flat coefficients of size
    window_size_timepoints and given a burn in of size
    window_size_timepoints.
    """
    tmp = np.random.randn(n_timepoints + window_size_timepoints)
    # SLOW AND MEMORY CONSUMING IMPLEMENTATION:
    # noise = np.empty((n_timepoints + window_size_timepoints, window_size_timepoints))
    # for i in range(window_size_timepoints):
    #     noise[:,i] = np.roll(tmp, i)

    # noise = noise[:n_timepoints,:].mean(1)

    # Decently fast and memory-efficient implementation:
    noise = np.empty(n_timepoints + window_size_timepoints)
    for i in range(n_timepoints):
        noise[i] = tmp[i:i+window_size_timepoints].mean()

    noise = noise[:n_timepoints]

    return noise


def simulate_external_temperature(timestamps, time_step=None, year_min_min=-5.0, year_min_max=14.0, year_max_min=10.0, year_max_max=32.0, date_daily_max_max=datetime(2014,1,1,13,0), date_seasonal_max_max=datetime(2014,8,1,13,0), noise_daily_window=3600 * 6.0, noise_seasonal_window=86400 * 30.0, noise_sigma=1.0):
    """
    This function simulates the external temperature as the sum of a
    seasonal periodict effect, a daily periodic effect and
    autocorrelated noise. Time is expressed in seconds.

    Parameters
    ----------
    timestamps : array of floats
        The timepoints of the simulation
    year_min_min : float
        Minimum temperature of the coldest day of the year
    year_min_max : float
        Maximum temperature of the coldest day of the year
    year_max_min : float
        Minimum temperature of the hottest day of the year
    year_max_max : float
        Minimum temperature of the hottest day of the year
    date_daily_max : datetime
        The time of the day when temperature is max
    date_seasonal_max_max : datetime
        The datetime of the year when temperature is max
    noise_daily_window : float
        window size of the autocorrelated noise for a single day (in secs.)
    noise_seasonal_window : float
        window size of the autocorrelated noise for the yearly variation (in secs.)
    noise_sigma : float
        amplitude of the autocorrelated noise in the simulation
    """
    if time_step is None: time_step = timedelta(seconds = np.mean([dts.seconds for dts in np.diff(timestamps)]))
    t_step_sec = time_step.seconds
    noise_daily = autocorrelated_noise(timestamps.size, window_size_timepoints=max([2, np.int(noise_daily_window / t_step_sec)]))
    noise_seasonal = autocorrelated_noise(timestamps.size, window_size_timepoints=max([2, np.int(noise_seasonal_window / t_step_sec)]))

    tmp = np.array([(ts - date_daily_max_max).total_seconds() for ts in timestamps])
    daily_variation = np.cos(tmp * np.pi * 2.0 / 86400.0) + noise_daily * noise_sigma
    tmp = np.array([(ts - date_seasonal_max_max).total_seconds() for ts in timestamps])
    seasonal_variation = np.cos(tmp * np.pi * 2.0 / 86400.0 / 365.25) + noise_seasonal * noise_sigma
    temperature_min = (seasonal_variation + 1.0) / 2.0 * (year_min_max - year_min_min) + year_min_min
    temperature_max = (seasonal_variation + 1.0) / 2.0 * (year_max_max - year_max_min) + year_max_min
    temperature = (daily_variation + 1.0) / 2.0 * (temperature_max - temperature_min) + temperature_min
    
    return temperature


