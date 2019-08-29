from HWdevices import GMS_test


class DeviceManager:

    def execute(self, time_issued, id, args):
        result = self.commands[id](*(eval(args)))
        return (time_issued, id, args, result)

    def __init__(self, device_details, log):
        self.device_details = device_details
        self.device = GMS_test.GMStest(self.device_details['device_id'], self.device_details['address'])
        self.log = log
        self.commands = {
                31: self.device.get_valve_info,
                22: self.device.get_valve_flow,
                33: self.device.set_valve_flow,
            }
