from random import random
from HWdevices.abstract.AbstractPBR import AbstractPBR


class PBRtest(AbstractPBR):
    def __init__(self, ID, address):
        super(PBRtest, self).__init__(ID, address)
        self.last_value = 0.45
        self.increasing = False

    def get_temp_settings(self):
        """
        Get information about currently set temperature, maximal and
        minimal allowed temperature.

        :return: The current settings structured in a dictionary.
        """
        return {"temp_set": 25, "temp_min": 10, "temp_max": 35}

    def get_temp(self):
        """
        Get current temperature in Celsius degree.

        :return: The current temperature.
        """
        return 25

    def set_temp(self, temp):
        """
        Set desired temperature in Celsius degree.

        :param temp: The temperature.
        :return: True if was successful, False otherwise.
        """
        return True

    def get_ph(self):
        """
        Get current pH (dimensionless.)

        :param repeats: the number of measurement repeats
        :param wait: waiting time between individual repeats
        :return: The current pH.
        """
        return 7

    def measure_od(self, channel=0):
        """
        Measure current Optical Density (OD, dimensionless).

        :param channel: which channel should be measured
        :param repeats: the number of measurement repeats
        :return: Measured OD
        """
        if random() < 0.01:
            raise Exception("Cannot measure value - some random error.")
        step = 0.002
        sign = 1 if self.increasing else -1
        if random() < 0.05:
            step = random()
            if random() > 0.01:
                return self.last_value + sign * step
        self.last_value += sign * step
        return self.last_value

    def get_pump_params(self, pump):
        """
        Get parameters for given pump.

        :param pump: Given pump
        :return: The current settings structured in a dictionary.
        """
        return {"pump_direction": 1, "pump_on": True, "pump_valves": 10,
                "pump_flow": 0.3, "pump_min": 0, "pump_max": 100}

    def set_pump_params(self, pump, direction, flow):
        """
        Set up the rotation direction and flow for given pump.

        :param pump: Given pump
        :param direction: Rotation direction (1 right, -1 left)
        :param flow: Desired flow rate
        :return:  True if was successful, False otherwise.
        """
        return True

    def set_pump_state(self, pump, on):
        """
        Turns on/off given pump.

        :param pump: ID of a pump
        :param on: True to turn on, False to turn off
        :return: True if was successful, False otherwise.
        """
        self.increasing = not bool(on)
        return True

    def get_light_intensity(self, channel):
        """
        Checks for current (max?) light intensity.

        Items: "intensity": current light intensity (float) in μE,
               "max": maximal intensity (float) in μE,
               "on": True if light is turned on (bool)

        :param channel: Given channel ID
        :return: The current settings structured in a dictionary.
        """
        return {"light_intensity": 500, "light_max": 1000, "light_on": True}

    def set_light_intensity(self, channel, intensity):
        """
        Control LED panel on photobioreactor.

        :param channel: Given channel (0 for red light, 1 for blue light)
        :param intensity: Desired intensity
        :return: True if was successful, False otherwise.
        """
        return True

    def turn_on_light(self, channel, on):
        """
        Turn on/off LED panel on photobioreactor.

        :param channel: Given channel
        :param on: True turns on, False turns off
        :return: True if was successful, False otherwise.
        """
        return True

    def get_pwm_settings(self):
        """
        Checks for current stirring settings.

        Items: "pulse": current stirring in %,
               "min": minimal stirring in %,
               "max": maximal stirring in %,
               "on": True if stirring is turned on (bool)

        :return: The current settings structured in a dictionary.
        """
        return {"pwm_pulse": 1, "pwm_min": 0, "pwm_max": 100, "pwm_on": True}

    def set_pwm(self, value, on):
        """
        Set stirring settings.
        Channel: 0 red and 1 blue according to PBR configuration.

        :param value: desired stirring pulse
        :param on: True turns on, False turns off
        :return: True if was successful, False otherwise.
        """
        return True

    def get_o2(self, raw=True, repeats=5, wait=0):
        """
        Checks for concentration of dissociated O2.

        Items: "pulse": current stirring in %,
               "min": minimal stirring in %,
               "max": maximal stirring in %,
               "on": True if stirring is turned on (bool)

        :param raw: True for raw data, False for data calculated according to temperature calibration
        :param repeats: the number of measurement repeats
        :param wait: waiting time between individual repeats
        :return: The current settings structured in a dictionary.
        """
        return 10

    def get_thermoregulator_settings(self):
        """
        Get current settings of thermoregulator.

        Items: "temp": current temperature in Celsius degrees,
               "min": minimal allowed temperature,
               "max": maximal allowed temperature,
               "on": state of thermoregulator (1 -> on, 0 -> freeze, -1 -> off)

        :return: The current settings structured in a dictionary.
        """
        return {"temp": 25, "temp_min": 0, "temp_max": 100, "temp_on": 1}

    def set_thermoregulator_state(self, on):
        """
        Set state of thermoregulator.

        :param on: 1 -> on, 0 -> freeze, -1 -> off
        :return: True if was successful, False otherwise.
        """
        return True

    def measure_ft(self, channel):
        """
        ???

        :param channel: ???
        :return: ???
        """
        return 13.4

    def get_co2(self, raw=True, repeats=5):
        """
        TBA

        :param raw: True for raw data, False for data ???
        :param repeats: the number of measurement repeats
        :return:
        """
        return 5

    def measure_all(self):
        """
        Measures all basic measurable values.

        :return: dictionary of all measured values
        """
        result = dict()
        result["pwm_setting"] = self.get_pwm_settings()
        result["light_0"] = self.get_light_intensity(0)
        result["light_1"] = self.get_light_intensity(1)
        result["od_0"] = self.measure_od(0)
        result["od_1"] = self.measure_od(1)
        result["ph"] = self.get_ph()
        result["temp"] = self.get_temp()
        result["pump"] = self.get_pump_params(5)
        result["o2"] = self.get_o2()
        result["co2"] = self.get_co2()
        result["ft"] = self.measure_ft(5)

        return result

    def measure_AUX(self, channel):
        """
        Values of AUX auxiliary input voltage.

        :param channel: ???
        :return: ???
        """
        return 10

    def flash_LED(self):
        """
        Triggers a flashing sequence and is used to physically identify the PBR.

        :return: True if was successful, False otherwise
        """
        return "flashLED"

    def get_hardware_address(self):
        """
        Get the MAC address of the PBR.

        :return: the MAC address
        """
        return 21345

    def get_cluster_name(self):
        """
        The name of the bioreactor array / cluster.

        :return: the cluster name
        """
        return "claster 1"
