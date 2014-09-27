import numpy as np


def home_heater_temperature(T_home, T_external, T_heater, heating_schedule, T_heating, k_home_external, k_heater_on, k_heater_off, k_home_heater, t_step):
    """Simple model of interaction between home's temperature,
    external temperature and heating system. This model is based on
    the Newton's law of cooling:
    http://en.wikipedia.org/wiki/Convective_heat_transfer#Newton.27s_law_of_cooling
    """
    # The external environment drags home's temperature:
    T_home_next_external = T_external + (T_home - T_external) * np.exp(-k_home_external * t_step) # Newton's law of cooling
    
    if heating_schedule == 1: # if heating is turned on then the heater is heated:
        T_heater_next = T_heating + (T_heater - T_heating) * np.exp(-k_heater_on * t_step) # Newton's law of cooling
    else: # if heating is turned off then the heater is cooled according to home's temperature:
        T_heater_next = T_home + (T_heater - T_home) * np.exp(-k_heater_off * t_step) # Newton's law of cooling

    # In any case, home's temperature is dragged by heater's temperature
    T_home_next_heater = T_heater + (T_home - T_heater) * np.exp(-k_home_heater * t_step) # Newton's law of cooling

    # We model the home's temperature at the next step as the average
    # of external environment and heater contributions.
    T_home_next = 0.5 * (T_home_next_external + T_home_next_heater)

    return T_home_next, T_heater_next

