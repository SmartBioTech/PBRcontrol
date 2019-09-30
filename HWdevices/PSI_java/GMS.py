from HWdevices.PSI_java.Device import Device


class GMS(Device):
    def __init__(self, ID, address):
        super(GMS, self).__init__(ID, address, "./lib/config/device_GMS.config")

    def get_valve_flow(self, valve):
        """
        Get value (L/min) of current flow in the given valve.
        :param valve: ID of the valve (0 for CO2, 1 for Air)
        :return: The current settings of the valve flow and actual value, both in (L/min).
        """

        msg = self.device.send("get-valve-flow", valve)
        if msg.isError():
            raise Exception(msg.getError())

        return {
            "actual-flow": msg.getDoubleParam(0),
            "target-flow": msg.getDoubleParam(1),
            "warning": msg.getBoolParam(2)
        }

    def set_valve_flow(self, valve, value):
        """
        Set value (L/min) of current flow in the given valve.
        :param valve: ID of the valve (0 for CO2, 1 for Air)
        :param value: desired value for valve flow in (L/min).
        :return: True if was successful, False otherwise.
        """
        msg = self.device.send("set-valve-flow", valve, value)
        return not msg.isError()

    def get_valve_info(self, valve):
        """
        Gives information about the valve
        :param valve: ID of the valve (0 for CO2, 1 for Air)
        :return: A dictionary with gas type and maximal allowed flow.
        """

        msg = self.device.send("get-valve-info", valve)
        if msg.isError():
            raise Exception(msg.getError())

        return {
            "maximal-flow": msg.getDoubleParam(0),
            "gas-type": msg.getIntParam(1),
            "user-gas-type": msg.getIntParam(2)
        }
