import threading
import datetime
from time import sleep

from HWdevices.Phenometrics.libs.communication import Connection
from HWdevices.abstract.AbstractPBR import AbstractPBR


class PBR(AbstractPBR):
    def __init__(self, ID, host_address, host_port, encryption_key, pump_args):
        super(PBR, self).__init__(ID, host_address)
        self.connection = Connection(host_address, host_port, encryption_key)
        pump_args.append(self)
        self.pump_manager = PhenometricsPumpManager(*pump_args)
        self.pump_manager.start()

    def get_temp_settings(self):
        """
        Get information about currently set temperature, maximal and
        minimal allowed temperature.

        :return: The current settings structured in a dictionary.
        """
        raise NotImplementedError("The method not implemented")

    def get_temp(self):
        """
        Get current temperature in Celsius degree.

        :return: The current temperature.
        """
        success, result = self.connection.send_command(self.ID, 'measureTemperature', [])
        if not success:
            raise Exception(result)
        return float(result)

    def set_temp(self, temp):
        """
        Set desired temperature in Celsius degree.

        :param temp: The temperature.
        :return: True if was successful, False otherwise.
        """
        success, result = self.connection.send_command(self.ID, 'setTemperature', [temp])
        if not success:
            raise Exception(result)
        return float(result) == temp

    def get_ph(self):
        """
        Get current pH (dimensionless.)

        :param repeats: the number of measurement repeats
        :param wait: waiting time between individual repeats
        :return: The current pH.
        """
        success, result = self.connection.send_command(self.ID, 'measurePH', [])
        if not success:
            raise Exception(result)
        return float(result)

    def measure_od(self, channel=0):
        """
        Measure current Optical Density (OD, dimensionless).

        :param channel: which channel should be measured
        :return: Measured OD
        """
        variant = ["measureOD1", "measureOD2"]
        success, result = self.connection.send_command(self.ID, variant[channel], [])
        if not success:
            raise Exception(result)
        return float(result)

    def get_pump_params(self, pump):
        """
        Get parameters for given pump.

        :param pump: Given pump
        :return: The current settings structured in a dictionary.
        """
        raise NotImplementedError("The method not implemented")

    def set_pump_params(self, pump, direction, flow):
        """
        Set up the rotation direction and flow for given pump.

        :param pump: Given pump
        :param direction: Rotation direction (1 right, -1 left)
        :param flow: Desired flow rate
        :return:  True if was successful, False otherwise.
        """
        raise NotImplementedError("The method not implemented")

    def set_pump_state(self, pump, on):
        """
        Turns on/off given pump.

        :param pump: ID of a pump
        :param on: True to turn on, False to turn off
        :return: True if was successful, False otherwise.
        """
        if on:
            self.pump_manager.start_pumping()
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
        raise NotImplementedError("The method not implemented")

    def set_light_intensity(self, channel, intensity):
        """
        Control LED panel on photobioreactor.

        :param channel: Given channel (0 for red light, 1 for blue light)
        :param intensity: Desired intensity
        :return: True if was successful, False otherwise.
        """
        success, result = self.connection.send_command(self.ID, 'setSolarLED', [intensity])
        if not success:
            raise Exception(result)
        return float(result) == float(intensity)

    def turn_on_light(self, channel, on):
        """
        Turn on/off LED panel on photobioreactor.

        :param channel: Given channel
        :param on: True turns on, False turns off
        :return: True if was successful, False otherwise.
        """
        raise NotImplementedError("The method not implemented")

    def get_pwm_settings(self):
        """
        Checks for current stirring settings.

        Items: "pulse": current stirring in %,
               "min": minimal stirring in %,
               "max": maximal stirring in %,
               "on": True if stirring is turned on (bool)

        :return: The current settings structured in a dictionary.
        """
        raise NotImplementedError("The method not implemented")

    def set_pwm(self, value, on):
        """
        Set stirring settings.
        Channel: 0 red and 1 blue according to PBR configuration.

        :param value: desired stirring pulse
        :param on: True turns on, False turns off
        :return: True if was successful, False otherwise.
        """
        success, result = self.connection.send_command(self.ID, 'setStir', [value])
        if not success:
            raise Exception(result)
        return float(result) == float(value)

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
        raise NotImplementedError("The method not implemented")

    def get_thermoregulator_settings(self):
        """
        Get current settings of thermoregulator.

        Items: "temp": current temperature in Celsius degrees,
               "min": minimal allowed temperature,
               "max": maximal allowed temperature,
               "on": state of thermoregulator (1 -> on, 0 -> freeze, -1 -> off)

        :return: The current settings structured in a dictionary.
        """
        raise NotImplementedError("The method not implemented")

    def set_thermoregulator_state(self, on):
        """
        Set state of thermoregulator.

        :param on: 1 -> on, 0 -> freeze, -1 -> off
        :return: True if was successful, False otherwise.
        """
        success, result = self.connection.send_command(self.ID, 'stopTemperatureControl', [])
        if not success:
            raise Exception(result)
        return result == "stopTemperatureControl"

    def measure_ft(self, channel):
        """
        ???

        :param channel: ???
        :return: ???
        """
        raise NotImplementedError("The method not implemented")

    def get_co2(self, raw, repeats):
        """
        TBA

        :param raw: True for raw data, False for data ???
        :param repeats: the number of measurement repeats
        :return:
        """
        raise NotImplementedError("The method not implemented")

    def measure_all(self, ft_channel=5, pump_id=5):
        """
        Measures all basic measurable values.

        :param ft_channel: channel for ft_measure
        :param pump_id: id of particular pump
        :return: dictionary of all measured values
        """
        measure_all_dictionary = dict()
        measure_all_dictionary["pwm_settings"] = False, "pwm settings not available for this device"
        measure_all_dictionary["light_0"] = False, "light_0 not available for this device"
        measure_all_dictionary["light_1"] = False, "light_1 not available for this device"

        try:
            measure_all_dictionary["od_0"] = True, self.measure_od(0)
        except Exception:
            measure_all_dictionary["od_0"] = False, "Cannot get od_0"

        try:
            measure_all_dictionary["od_1"] = True, self.measure_od(1)
        except Exception:
            measure_all_dictionary["od_1"] = False, "Cannot get od_1"

        try:
            measure_all_dictionary["ph"] = True, self.get_ph(),
        except Exception:
            measure_all_dictionary["ph"] = False, "Cannot get ph"

        try:
            measure_all_dictionary["temp"] = True, self.get_temp(),
        except Exception:
            measure_all_dictionary["temp"] = False, "Cannot get temp"

        measure_all_dictionary["pump"] = False, "pump settings not available for this device"
        measure_all_dictionary["o2"] = False, "o2 settings not available for this device"
        measure_all_dictionary["co2"] = False, "co2 settings not available for this device"
        measure_all_dictionary["ft"] = False, "ft settings not available for this device"

        return measure_all_dictionary

    def measure_AUX(self, channel):
        """
        Values of AUX auxiliary input voltage.

        :param channel: ???
        :return: ???
        """
        variant = ["measureAux1", "measureAux2"]
        success, result = self.connection.send_command(self.ID, variant[channel], [])
        if not success:
            raise Exception(result)
        return float(result)

    def flash_LED(self):
        """
        Triggers a flashing sequence and is used to physically identify the PBR.

        !!! random blank spaces complicate things. Is it like that also with "real" PBR?

        :return: True if was successful, False otherwise
        """
        success, result = self.connection.send_command(self.ID, "flashLED", [])
        if not success:
            raise Exception(result)
        return result.lstrip() == "flashLED"

    def get_hardware_address(self):
        """
        Get the MAC address of the PBR.

        :return: the MAC address
        """
        success, result = self.connection.send_command(self.ID, "getHardwareAddress", [])
        if not success:
            raise Exception(result)
        return result.lstrip()

    def get_cluster_name(self):
        """
        The name of the bioreactor array / cluster.

        :return: the cluster name
        """
        success, result = self.connection.send_command(self.ID, "getMatrixName", [])
        if not success:
            raise Exception(result)
        return result.lstrip()

    def disconnect(self):
        pass


class PhenometricsPumpManager(threading.Thread):
    def __init__(self, pump_state, device_details, log, last_OD, experimental_details, device):
        super(PhenometricsPumpManager, self).__init__(daemon=True)
        self.pump_state = pump_state
        self.device = device
        self.log = log
        self.device_details = device_details
        self.last_OD = last_OD
        self.stored_OD = last_OD
        self.stop_request = threading.Event()
        self.start_pumping_event = threading.Event()
        self.od_changed = threading.Event()
        self.wait_time = experimental_details['sleep_time']

    def run(self):
        self.start_pumping_event.wait()
        while not self.stop_request.isSet():    # if we set this flag but never set start_pumping_event_flag, will the thread truly exit?
            self.start_pumping_event.clear()

            self.device_details['setup']['lower_outlier_tol'] *= \
                self.device_details['setup']['pump_on_outlier_tolerance_factor']

            self.pump_state[0] = True  # is this necessary?

            while self.last_OD > self.device_details["setup"]["min_OD"]:
                self.od_changed.clear()
                self.stored_OD = self.last_OD
                try:
                    # this turns on the pump (works only if the pump goes from 0 to 1)
                    self.device.connection.send_command(self.device.ID, 'setAux2', [1])
                    # sleep 20 seconds, should be enough to accomplish steps 1. and 2.
                    sleep(2)
                    # reset the pump to zero state that is necessary for success of next set of the pump
                    self.device.connection.send_command(self.device.ID, 'setAux2', [0])
                except Exception:
                    continue
                self.od_changed.wait()  # we wait until OD has changed

            self.device_details['setup']['lower_outlier_tol'] /= \
                self.device_details['setup']['pump_on_outlier_tolerance_factor']

            self.start_pumping_event.wait()

    def start_pumping(self):
        self.start_pumping_event.set()

    def log_pump_change(self, state):
        time_issued = (datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        node_id = self.device_details["node_id"]
        device_type = self.device_details["device_type"]
        command_id = 8
        args = [self.device_details['setup']['pump_id'], state]
        self.log.update_log(time_issued, node_id, device_type, command_id, args, (True, True), "internal")

    def exit(self):
        self.stop_request.set()
