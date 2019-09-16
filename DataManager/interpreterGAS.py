from DataManager import base_interpreter


class DeviceManager(base_interpreter.BaseInterpreter):


    def __init__(self, device_details, log, device_class):
        super(DeviceManager, self).__init__(device_details, device_class, log)

        self.commands = {
                23: self.device.get_flow,
                24: self.device.get_flow_target,
                25: self.device.set_flow_target,
                26: self.device.get_flow_max,
                27: self.device.get_pressure,
                28: self.device.measure_all,
                29: self.device.get_co2_air,
                30: self.device.get_small_valves,
                31: self.device.set_small_valves,
            }

