from HWdevices.PSI_java.Device import Device


class PBR(Device):
    def __init__(self, ID, address):
        super(PBR, self).__init__(ID, address, "/home/pi/PBRcontrol/HWdevices/PSI_java/lib/config/device_PBR.config")

    def get_temp_settings(self):
        """
        Get information about currently set temperature, maximal and
        minimal allowed temperature.
        :return: The current settings structured in a dictionary.
        """

        msg = self.device.send("get-tr-settings")
        if msg.isError():
            raise Exception(msg.getError())

        return {
            "temp_set": msg.getDoubleParam(0),
            "temp_min": msg.getDoubleParam(1),
            "temp_max": msg.getDoubleParam(2),
            "state": msg.getBoolParam(3)
        }

    def get_temp(self):
        """
        Get current temperature in Celsius degree.
        :return: The current temperature.
        """
        msg = self.device.send("get-tr-temp")
        if msg.isError():
            raise Exception(msg.getError())

        return msg.getDoubleParam(0)

    def set_temp(self, temp):
        """
        Set desired temperature in Celsius degree.
        :param temp: The temperature.
        :return: True if was successful, False otherwise.
        """
        msg = self.device.send("set-tr-temp", temp)
        return not msg.isError()

    def get_ph(self, repeats, wait):
        """
        Get current pH (dimensionless.)
        :param repeats: the number of measurement repeats
        :param wait: waiting time between individual repeats
        :return: The current pH.
        """
        msg = self.device.send("get-ph", repeats, wait)
        if msg.isError():
            raise Exception(msg.getError())

        return msg.getDoubleParam(0)

    def measure_od(self, channel=0, repeats=1):
        """
        Measure current Optical Density (OD, dimensionless).
        :param channel: which channel should be measured
        :param repeats: the number of measurement repeats
        :return: Measured OD
        """
        msg = self.device.send("measure-od", channel, repeats)
        if msg.isError():
            raise Exception(msg.getError())

        return msg.getDoubleParam(0)

    def get_pump_params(self, pump):
        """
        Get parameters for given pump.
        :param pump: Given pump
        :return: The current settings structured in a dictionary.
        """
        msg = self.device.send("get-pump-info", pump)
        if msg.isError():
            raise Exception(msg.getError())

        return {
            "pump_direction": msg.getIntParam(0),
            "pump_on": msg.getBoolParam(1),
            "pump_valves": msg.getIntParam(2),
            "pump_flow": msg.getDoubleParam(3),
            "pump_min": msg.getDoubleParam(4),
            "pump_max": msg.getDoubleParam(5)
        }

    def set_pump_params(self, pump, direction, flow):
        """
        Set up the rotation direction and flow for given pump.
        :param pump: Given pump
        :param direction: Rotation direction (1 right, -1 left)
        :param flow: Desired flow rate
        :return:  True if was successful, False otherwise.
        """
        msg = self.device.send("set-pump-params", pump, direction, flow)
        return not msg.isError()

    def set_pump_state(self, pump, on):
        """
        Turns on/off given pump.
        :param pump: ID of a pump
        :param on: True to turn on, False to turn off
        :return: True if was successful, False otherwise.
        """
        msg = self.device.send("set-pump-state", pump, on)
        return not msg.isError()

    def get_light_intensity(self, channel):
        """
        Checks for current (max?) light intensity.
        Items: "intensity": current light intensity (float) in μE,
               "max": maximal intensity (float) in μE,
               "on": True if light is turned on (bool)
        :param channel: Given channel ID
        :return: The current settings structured in a dictionary.
        """
        msg = self.device.send("get-actinic-light-settings", channel)
        if msg.isError():
            raise Exception(msg.getError())

        return {
            "light_intensity": msg.getDoubleParam(0),
            "light_max": msg.getDoubleParam(1),
            "light_on": msg.getBoolParam(2)
        }

    def set_light_intensity(self, channel, intensity):
        """
        Control LED panel on photobioreactor.
        :param channel: Given channel (0 for red light, 1 for blue light)
        :param intensity: Desired intensity
        :return: True if was successful, False otherwise.
        """
        msg = self.device.send("set-actinic-light-intensity", channel, intensity)
        return not msg.isError()

    def turn_on_light(self, channel, on):
        """
        Turn on/off LED panel on photobioreactor.
        :param channel: Given channel
        :param on: True turns on, False turns off
        :return: True if was successful, False otherwise.
        """
        msg = self.device.send("set-ext-light-state", channel, on)
        return not msg.isError()

    def get_pwm_settings(self):
        """
        Checks for current stirring settings.
        Items: "pulse": current stirring in %,
               "min": minimal stirring in %,
               "max": maximal stirring in %,
               "on": True if stirring is turned on (bool)
        :return: The current settings structured in a dictionary.
        """
        msg = self.device.send("get-pwm-settings")
        if msg.isError():
            raise Exception(msg.getError())

        return {
            "pwm_pulse": msg.getIntParam(0),
            "pwm_min": msg.getIntParam(1),
            "pwm_max": msg.getIntParam(2),
            "pwm_on": msg.getParam(3),
        }

    def set_pwm(self, value, on):
        """
        Set stirring settings.
        Channel: 0 red and 1 blue according to PBR configuration.
        :param value: desired stirring pulse
        :param on: True turns on, False turns off
        :return: True if was successful, False otherwise.
        """
        msg = self.device.send("set-pwm", value, on)
        return not msg.isError()

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

        msg = self.device.send("get-o2/h2", repeats, wait, raw)
        if msg.isError():
            raise Exception(msg.getError())

        return msg.getDoubleParam(0)

    def get_thermoregulator_settings(self):
        """
        Get current settings of thermoregulator.
        Items: "temp": current temperature in Celsius degrees,
               "min": minimal allowed temperature,
               "max": maximal allowed temperature,
               "on": state of thermoregulator (1 -> on, 0 -> freeze, -1 -> off)
        :return: The current settings structured in a dictionary.
        """
        msg = self.device.send("get-tr-settings")
        return {
            "temp": msg.getDoubleParam(0),
            "temp_min": msg.getDoubleParam(1),
            "temp_max": msg.getDoubleParam(2),
            "temp_on": msg.getIntParam(3),
        }

    def set_thermoregulator_state(self, on):
        """
        Set state of thermoregulator.
        :param on: 1 -> on, 0 -> freeze, -1 -> off
        :return: True if was successful, False otherwise.
        """
        msg = self.device.send("set-tr-state", on)
        return not msg.isError()

    def measure_ft(self, channel):
        """
        ???
        :param channel: ???
        :return: ???
        """
        msg = self.device.send("measure-ft", channel)
        if msg.isError():
            raise Exception(msg.getError())

        return {
            "flash": msg.getIntParam(0),
            "background": msg.getIntParam(1)
        }

    def get_co2(self, raw=True, repeats=5):
        """
        TBA
        :param raw: True for raw data, False for data ???
        :param repeats: the number of measurement repeats
        :return:
        """
        msg = self.device.send("get-co2", repeats, raw)
        if msg.isError():
            raise Exception(msg.getError())

        return msg.getDoubleParam(0)

    def measure_all(self, channel=0, pump=0):
        """
        Measures all basic measurable values.
        :return: dictionary of all measured values
        """
        measure_all_dictionary = dict()
        try:
            measure_all_dictionary["pwm_settings"] = self.get_pwm_settings()
        except Exception:
            measure_all_dictionary["pwm_settings"] = "Cannot get pwm settings"

        try:
            measure_all_dictionary["light_0"] = self.get_light_intensity(0)
        except Exception:
            measure_all_dictionary["light_0"] = "Cannot get light_0"

        try:
            measure_all_dictionary["light_1"] = self.get_light_intensity(1)
        except Exception:
            measure_all_dictionary["light_1"] = "Cannot get light_1"

        try:
            measure_all_dictionary["od_0"] = self.measure_od(0, 30)
        except Exception:
            measure_all_dictionary["od_0"] = "Cannot get od_0"

        try:
            measure_all_dictionary["od_1"] = self.measure_od(1, 30)
        except Exception:
            measure_all_dictionary["od_1"] = "Cannot get od_1"

        try:
            measure_all_dictionary["ph"] = self.get_ph(5, 0),
        except Exception:
            measure_all_dictionary["ph"] = "Cannot get ph"

        try:
            measure_all_dictionary["temp"] = self.get_temp(),
        except Exception:
            measure_all_dictionary["temp"] = "Cannot get temp"

        try:
            measure_all_dictionary["pump"] = self.get_pump_params(pump),
        except Exception:
            measure_all_dictionary["pump"] = "Cannot get pump"

        try:
            measure_all_dictionary["o2"] = self.get_o2()
        except Exception:
            measure_all_dictionary["o2"] = "Cannot get o2"

        try:
            measure_all_dictionary["co2"] = self.get_co2()
        except Exception:
            measure_all_dictionary["co2"] = "Cannot get co2"

        try:
            measure_all_dictionary["ft"] = self.measure_ft(channel)
        except Exception:
            measure_all_dictionary["ft"] = "Cannot measure ft"

        return measure_all_dictionary

    def measure_AUX(self, channel):
        """
        Values of AUX auxiliary input voltage.
        :param channel: ???
        :return: ???
        """
        raise NotImplementedError("The method not implemented")

    def flash_LED(self):
        """
        Triggers a flashing sequence and is used to physically identify the PBR.
        :return: True if was successful, False otherwise
        """
        raise NotImplementedError("The method not implemented")

    def get_hardware_address(self):
        """
        Get the MAC address of the PBR.
        :return: the MAC address
        """
        raise NotImplementedError("The method not implemented")

    def get_cluster_name(self):
        """
        The name of the bioreactor array / cluster.
        :return: the cluster name
        """
        raise NotImplementedError("The method not implemented")