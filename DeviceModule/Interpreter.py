from DeviceModule.HWdevices.abstract.device import Device
from DeviceModule.DeviceConfiguration import DeviceConfiguration


class Interpreter:
    def __init__(self, physicalDevice: Device, deviceConfig: DeviceConfiguration):
        self.device = physicalDevice
        self.deviceConfig = deviceConfig
        self.commands = {
            1: self.device.get_temp_settings,
            2: self.device.get_temp,
            3: self.device.set_temp,
            4: self.device.get_ph,
            5: self.device.measure_od,
            6: self.device.get_pump_params,
            7: self.device.set_pump_params,
            8: self.device.set_pump_state,
            9: self.device.get_light_intensity,
            10: self.device.set_light_intensity,
            11: self.device.turn_on_light,
            12: self.device.get_pwm_settings,
            13: self.device.set_pwm,
            14: self.device.get_o2,
            15: self.device.get_thermoregulator_settings,
            16: self.device.set_thermoregulator_state,
            17: self.device.measure_ft,
            18: self.device.get_co2,
            19: self.device.measure_all,
            20: self.device.measure_AUX,
            21: self.device.flash_LED,
            22: self.device.get_hardware_address,
            23: self.device.get_cluster_name,
            24: self.deviceConfig.set_max_outliers,
            25: self.deviceConfig.set_od_bounds,
            26: self.deviceConfig.set_tolerance,
            27: self.device.get_flow,
            28: self.device.get_flow_target,
            29: self.device.set_flow_target,
            30: self.device.get_flow_max,
            31: self.device.get_pressure,
            32: self.device.get_co2_air,
            33: self.device.get_small_valves,
            34: self.device.set_small_valves,
            35: self.device.get_valve_info,
            36: self.device.get_valve_flow,
            37: self.device.set_valve_flow,
        }
