from HWdevices import GMS_test
from DataManager import base_interpreter


class DeviceManager(base_interpreter.BaseInterpreter):

    def __init__(self, device_details, log):
        self.device_details = device_details
        self.device = GMS_test.GMStest(self.device_details['device_id'], self.device_details['address'])
        self.log = log
        self.commands = {
                31: self.device.get_valve_info,
                22: self.device.get_valve_flow,
                33: self.device.set_valve_flow,
            }
        super(DeviceManager, self).__init__()
