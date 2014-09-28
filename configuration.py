"""Constants and parameters for simulation.
"""

engine_string = 'sqlite:///21at7.sqlite'
# engine_string = 'sqlite:////run/21at7/21at7.sqlite'

# Constants for heat transfer:
k_home_external = 1.0 / 3600.0 / 2.0 # how fast home temperature changes due to external temperature
k_home_heater = 1.0 / 3600.0 # how fast home temperature changes due to heater temperature
k_heater_on = 1.0 / 600.0 # how fast heater temperature changes when heating is on
k_heater_off = 1.0 / 1200.0 # how fast heater temperature changes when heating is off

T_heating = 50.0 # temperature of the heating system, i.e. of the hot water produced
T0_home = 20.0 # initial house temperature # initial house temperature at time 0.
