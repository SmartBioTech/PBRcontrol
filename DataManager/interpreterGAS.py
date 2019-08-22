from HWdevices import GAS_test


class InterpreterPBR:

    def __init__(self, device_details):
        self.device_details = device_details
        self.device = GAS_test.GAStest(self.device_details['device_id'], self.device_details['address'])
        self.commands = {
                21: self.device.get_co2_air,
                22: self.device.get_small_valves,
                23: self.device.get_flow,
                24: self.device.get_flow_target,
                25: self.device.set_flow_target,
                26: self.device.get_flow_max,
                27: self.device.get_pressure,
                28: self.device.measure_all,
            }
