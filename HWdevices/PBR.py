from math import log10
from HWdevices.abstract.AbstractPBR import AbstractPBR
from HWdevices.scheme.command import Command
from HWdevices.scheme.scheme_manager import SchemeManager


class PBR(AbstractPBR):
    def __init__(self, ID, address):
        super(PBR, self).__init__(ID, address)
        self.scheme_manager = SchemeManager(ID, address)

    def get_temp_settings(self) -> dict:
        """
        Get information about currently set temperature, maximal and
        minimal allowed temperature.

        :return: The current settings structured in a dictionary.
        """
        results = ["set", "min", "max"]
        command = Command("get-thermoregulator-settings")
        values = self.scheme_manager.execute([command])[0].rstrip()[1:-1].split()

        return dict(zip(results, list(map(float, values[1:-1]))))

    def get_temp(self) -> float:
        """
        Get current temperature in Celsius degree.

        :return: The current temperature.
        """
        command = Command("get-current-temperature")
        return float(self.scheme_manager.execute([command])[0])

    def set_temp(self, temp: float) -> bool:
        """
        Set desired temperature in Celsius degree.

        :param temp: The temperature.
        :return: True if was successful, False otherwise.
        """
        command = Command("set-thermoregulator-temp", [temp])
        return self.scheme_manager.execute([command])[0].rstrip() == 'ok'

    def get_ph(self, repeats: int = 5, wait: int = 0) -> float:
        """
        Get current pH (dimensionless.)

        :param repeats: the number of measurement repeats
        :param wait: waiting time between individual repeats
        :return: The current pH.
        """
        command = Command("get-ph", [repeats, wait])
        return float(self.scheme_manager.execute([command])[0])

    def measure_od(self, channel: int = 0, repeats: int = 30) -> float:
        """
        Measure current Optical Density (OD, dimensionless).

        :param channel: which channel should be measured
        :param repeats: the number of measurement repeats
        :return: Measured OD
        """
        command = Command("measure-od", [channel, repeats])
        result = self.scheme_manager.execute([command])[0].rstrip().split()
        return -log10((int(result[1]) - int(result[2][:-1])) / 40000)

    def get_pump_params(self, pump: int) -> dict:
        """
        Get parameters for given pump.

        :param pump: Given pump
        :return: The current settings structured in a dictionary.
        """
        command = Command("get-pump-info", [pump])
        result = self.scheme_manager.execute([command])[0].rstrip()[1:-1].split()
        return {"direction": int(result[1]), "on": self.scheme_manager.from_scheme_bool(result[2]),
                "valves": int(result[3]), "flow": float(result[4]),
                "min": float(result[5]), "max": float(result[6])}

    def set_pump_params(self, pump: int, direction: int, flow: float) -> bool:
        """
        Set up the rotation direction and flow for given pump.

        :param pump: Given pump
        :param direction: Rotation direction (1 right, -1 left)
        :param flow: Desired flow rate
        :return:  True if was successful, False otherwise.
        """
        command = Command("set-pump-params", [pump, direction, flow])
        return self.scheme_manager.execute([command])[0].rstrip() == 'ok'

    def set_pump_state(self, pump: int, on: bool) -> bool:
        """
        Turns on/off given pump.

        :param pump: ID of a pump
        :param on: True to turn on, False to turn off
        :return: True if was successful, False otherwise.
        """
        command = Command("set-pump-state", [pump, self.scheme_manager.to_scheme_bool(on)])
        return self.scheme_manager.execute([command])[0].rstrip() == 'ok'

    def get_light_intensity(self, channel: int) -> dict:
        """
        Checks for current (max?) light intensity.

        Items: "intensity": current light intensity (float) in μE,
               "max": maximal intensity (float) in μE,
               "on": True if light is turned on (bool)

        :param channel: Given channel ID
        :return: The current settings structured in a dictionary.
        """
        command = Command("get-actinic-continual-settings", [channel])
        result = self.scheme_manager.execute([command])[0].rstrip()[1:-1].split()
        return {"intensity": float(result[1]), "max": float(result[2]),
                "on": self.scheme_manager.from_scheme_bool(result[3])}

    def set_light_intensity(self, channel: int, intensity: float) -> bool:
        """
        Control LED panel on photobioreactor.

        :param channel: Given channel (0 for red light, 1 for blue light)
        :param intensity: Desired intensity
        :return: True if was successful, False otherwise.
        """
        command = Command("set-actinic-continual-intensity", [channel, intensity])
        return self.scheme_manager.execute([command])[0].rstrip() == 'ok'

    def turn_on_light(self, channel: int, on: bool) -> bool:
        """
        Turn on/off LED panel on photobioreactor.

        :param channel: Given channel
        :param on: True turns on, False turns off
        :return: True if was successful, False otherwise.
        """
        command = Command("set-actinic-continual-mode", [channel, self.scheme_manager.to_scheme_bool(on)])
        return self.scheme_manager.execute([command])[0].rstrip() == 'ok'

    def get_pwm_settings(self) -> dict:
        """
        Checks for current stirring settings.

        Items: "pulse": current stirring in %,
               "min": minimal stirring in %,
               "max": maximal stirring in %,
               "on": True if stirring is turned on (bool)

        :return: The current settings structured in a dictionary.
        """
        command = Command("get-pwm-settings")
        result = self.scheme_manager.execute([command])[0].rstrip()[1:-1].split()
        return {"pulse": result[1], "min": result[2],
                "max": result[3], "on": self.scheme_manager.from_scheme_bool(result[4])}

    def set_pwm(self, value: int, on: bool) -> bool:
        """
        Set stirring settings.
        Channel: 0 red and 1 blue according to PBR configuration.

        :param value: desired stirring pulse
        :param on: True turns on, False turns off
        :return: True if was successful, False otherwise.
        """
        command = Command("set-pwm", [value, self.scheme_manager.to_scheme_bool(on)])
        return self.scheme_manager.execute([command])[0].rstrip() == 'ok'

    def get_o2(self, raw: bool = True, repeats: int = 5, wait: int = 0) -> float:
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
        command = Command("get-o2/h2", [repeats, wait, self.scheme_manager.to_scheme_bool(raw)])
        return float(self.scheme_manager.execute([command])[0].rstrip())

    def get_thermoregulator_settings(self) -> dict:
        """
        Get current settings of thermoregulator.

        Items: "temp": current temperature in Celsius degrees,
               "min": minimal allowed temperature,
               "max": maximal allowed temperature,
               "on": state of thermoregulator (1 -> on, 0 -> freeze, -1 -> off)

        :return: The current settings structured in a dictionary.
        """
        command = Command("get-thermoregulator-settings")
        result = self.scheme_manager.execute([command])[0].rstrip()[1:-1].split()
        return {"temp": float(result[1]), "min": float(result[2]),
                "max": float(result[3]), "on": int(result[4])}

    def set_thermoregulator_state(self, on: int) -> bool:
        """
        Set state of thermoregulator.

        :param on: 1 -> on, 0 -> freeze, -1 -> off
        :return: True if was successful, False otherwise.
        """
        command = Command("set-thermoregulator-state", [on])
        return self.scheme_manager.execute([command])[0].rstrip() == 'ok'

    def measure_ft(self, channel: int) -> float:
        """
        ???

        :param channel: ???
        :return: ???
        """
        command = Command("measure-ft", [channel])
        return float(self.scheme_manager.execute([command])[0].rstrip())

    def get_co2(self, raw: bool = True, repeats: int = 5) -> float:
        """
        TBA

        :param raw: True for raw data, False for data ???
        :param repeats: the number of measurement repeats
        :return:
        """
        command = Command("get-co2", [repeats, self.scheme_manager.to_scheme_bool(raw)])
        return float(self.scheme_manager.execute([command])[0].rstrip())

    def measure_all(self):
        """
        Measures all basic measurable values.

        channel for measure-ft ???
        need to solve the case when one of the values wasn't measured
        (could destroy whole measurement)
        """
        commands = [Command("get-pwm-settings"),
                    Command("get-actinic-continual-settings", [0]),
                    Command("get-actinic-continual-settings", [1]),
                    Command("measure-od", [0, 30]),
                    Command("measure-od", [0, 30]),
                    Command("get-ph", [5, 0]),
                    Command("get-current-temperature"),
                    Command("get-pump-info", [5]),
                    Command("get-o2/h2", [5, 0, self.scheme_manager.to_scheme_bool(True)]),
                    Command("get-co2", [5, self.scheme_manager.to_scheme_bool(True)]),
                    Command("measure-ft", [channel])]

        results = self.scheme_manager.execute(commands)
        data = {'a': 5 }

        # manage results
