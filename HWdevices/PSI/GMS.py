from HWdevices.abstract.AbstractGMS import AbstractGMS
from HWdevices.PSI.scheme.command import Command
from HWdevices.PSI.scheme.scheme_manager import SchemeManager


# Gas Mixer
class GMS(AbstractGMS):
    def __init__(self, ID, address):
        super(GMS, self).__init__(ID, address)
        self.scheme_manager = SchemeManager(ID, address)
        self.GAS_TYPES = ["CO2", "Air", "N2"]

    def get_valve_flow(self, valve: int) -> dict:
        """
        Get value (L/min) of current flow in the given valve.

        :param valve: ID of the valve (0 for CO2, 1 for Air)
        :return: The current settings of the valve flow and actual value, both in (L/min).
        """
        values = ["current", "set"]
        command = Command("get-valve-flow", [valve])
        results = self.scheme_manager.execute([command])[0].rstrip()[1:-1].split()
        return dict(zip(values, list(map(float, results[1:-1]))))

    def set_valve_flow(self, valve: int, value: float) -> bool:
        """
        Set value (L/min) of current flow in the given valve.

        :param valve: ID of the valve (0 for CO2, 1 for Air)
        :param value: desired value for valve flow in (L/min).
        :return: True if was successful, False otherwise.
        """
        command = Command("set-valve-tflow", [valve, value])
        result = self.scheme_manager.execute([command])[0].rstrip()
        return result == 'ok'

    def get_valve_info(self, valve: int) -> dict:
        """
        Gives information about the valve

        :param valve: ID of the valve (0 for CO2, 1 for Air)
        :return: A dictionary with gas type and maximal allowed flow.
        """
        values = ["max_flow", "gas_type"]
        command = Command("get-valve-info", [valve])
        results = self.scheme_manager.execute([command])[0].rstrip()[1:-1].split()
        return dict(zip(values, [float(results[1]), self.GAS_TYPES[int(results[3])]]))
