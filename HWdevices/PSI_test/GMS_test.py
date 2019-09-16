from HWdevices.abstract.AbstractGMS import AbstractGMS


# Abstract Gas Mixer
class GMStest(AbstractGMS):
    def __init__(self, ID, address):
        super(GMStest, self).__init__(ID, address)
        self.GAS_TYPES = ["CO2", "Air", "N2"]

    def get_valve_flow(self, valve):
        """
        Get value (L/min) of current flow in the given valve.

        :param valve: ID of the valve (0 for CO2, 1 for Air)
        :return: The current settings of the valve flow and actual value, both in (L/min).
        """
        return {"valve_flow_current": 5, "valve_flow_set": 10}

    def set_valve_flow(self, valve, value):
        """
        Set value (L/min) of current flow in the given valve.

        :param valve: ID of the valve (0 for CO2, 1 for Air)
        :param value: desired value for valve flow in (L/min).
        :return: True if was successful, False otherwise.
        """
        return True

    def get_valve_info(self, valve):
        """
        Gives information about the valve

        :param valve: ID of the valve (0 for CO2, 1 for Air)
        :return: A dictionary with gas type and maximal allowed flow.
        """
        return {"valve_max_flow": 10, "valve_gas_type": self.GAS_TYPES[0]}
