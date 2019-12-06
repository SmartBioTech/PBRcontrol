from commandInterpreter import base_interpreter


class DeviceManager(base_interpreter.BaseInterpreter):


    def __init__(self, device_details, log, device_class):
        super(DeviceManager, self).__init__(device_details, device_class, log)

        self.commands = {
                27: self.device.get_flow,
                28: self.device.get_flow_target,
                29: self.device.set_flow_target,
                30: self.device.get_flow_max,
                31: self.device.get_pressure,
                32: self.device.measure_all,
                33: self.device.get_co2_air,
                34: self.device.get_small_valves,
                35: self.device.set_small_valves,
            }

