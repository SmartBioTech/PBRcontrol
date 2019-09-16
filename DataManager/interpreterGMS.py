from DataManager import base_interpreter


class DeviceManager(base_interpreter.BaseInterpreter):

    def __init__(self, device_details, log, device_class):
        super(DeviceManager, self).__init__(device_details, device_class, log)

        self.commands = {
                32: self.device.get_valve_info,
                33: self.device.get_valve_flow,
                34: self.device.set_valve_flow,
            }

