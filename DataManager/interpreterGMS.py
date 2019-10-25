from DataManager import base_interpreter


class DeviceManager(base_interpreter.BaseInterpreter):

    def __init__(self, device_details, log, device_class):
        super(DeviceManager, self).__init__(device_details, device_class, log)

        self.commands = {
                36: self.device.get_valve_info,
                37: self.device.get_valve_flow,
                38: self.device.set_valve_flow,
            }

