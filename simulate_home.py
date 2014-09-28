import numpy as np
import pandas as pd


class HomeTemperature(object):
    """Home temperature.
    """
    def __init__(self, T_heating, k_home_external, k_heater_on, k_heater_off, k_home_heater, t_step, engine=None):
        self.T_heating = T_heating
        self.k_home_external = k_home_external
        self.k_heater_on = k_heater_on
        self.k_heater_off = k_heater_off
        self.k_home_heater = k_home_heater
        self.t_step = t_step
        self.engine = engine


    def home_heater_temperature(self, T_home, T_external, T_heater, heating, my_datetime):
        """Simple model of interaction between home's temperature,
        external temperature and heating system. This model is based on
        the Newton's law of cooling:
        http://en.wikipedia.org/wiki/Convective_heat_transfer#Newton.27s_law_of_cooling
        """
        # The external environment drags home's temperature:
        T_home_next_external = T_external + (T_home - T_external) * np.exp(-self.k_home_external * self.t_step) # Newton's law of cooling

        if heating == 1: # if heating is turned on then the heater is heated:
            T_heater_next = self.T_heating + (T_heater - self.T_heating) * np.exp(-self.k_heater_on * self.t_step) # Newton's law of cooling
        else: # if heating is turned off then the heater is cooled according to home's temperature:
            T_heater_next = T_home + (T_heater - T_home) * np.exp(-self.k_heater_off * self.t_step) # Newton's law of cooling

        # In any case, home's temperature is dragged by heater's temperature
        T_home_next_heater = T_heater + (T_home - T_heater) * np.exp(-self.k_home_heater * self.t_step) # Newton's law of cooling

        # We model the home's temperature at the next step as the average
        # of external environment and heater contributions.
        T_home_next = 0.5 * (T_home_next_external + T_home_next_heater)

        if self.engine is not None:
            df = pd.DataFrame({'timestamp': [my_datetime],
                               'home_temperature': [T_home_next],
                               })
            df.to_sql('temperature_home', self.engine, if_exists='append', index=False)

        return T_home_next, T_heater_next


