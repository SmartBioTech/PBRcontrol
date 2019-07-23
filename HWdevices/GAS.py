from HWdevices.abstract.AbstractGAS import AbstractGAS
from HWdevices.scheme.command import Command
from HWdevices.scheme.scheme_manager import SchemeManager


class GAS(AbstractGAS):
    def __init__(self, ID, address):
        super(GAS, self).__init__(ID, address)
        self.scheme_manager = SchemeManager(ID, address)

    def get_co2_air(self) -> float:
        """
        Measures CO2 in air.

        :return: measured CO2 in air
        """
        command = Command("get-co2-air")
        return float(self.scheme_manager.execute([command])[0].rstrip())

    def get_small_valves(self) -> str:
        """
        Obtain settings of individual vents of GAS device.

        Represented as one byte, where first 6 bits represent
        vents indexed as in a picture scheme available here:
        https://i.imgur.com/jSeFFaO.jpg

        :return: byte representation of vents settings.
        """
        command = Command("get-small-valves")
        return bin(int(self.scheme_manager.execute([command])[0].rstrip()))[2:]

    def set_small_valves(self, mode: int) -> bool:
        """
        Changes settings of individual vents of GAS device.

        Can be set by one byte (converted to int), where first 6
        bits represent vents indexed as in a picture scheme
        available here: https://i.imgur.com/jSeFFaO.jpg

        Mode 0 - normal mode, output from GMS goes to PBR (255)
        Mode 1 - reset mode, N2 (nitrogen) goes to PBR (239)
        Mode 2 - no gas input to PBR (249)
        Mode 3 - output of PBR goes to input of PBR (246)

        :param mode: chosen mode (0 to 3)
        :return: True if was successful, False otherwise.
        """
        modes = {0: "11111111", 1: "11101111", 2: "11111001", 3: "11110110"}
        command = Command("get-small-valves", [int(modes[mode], 2)])
        result = self.scheme_manager.execute([command])[0].rstrip()
        return result == 'ok'

    def get_flow(self):
        '''
        Actual flow being send from GAS to the PBR.

        Returns:
            float: The current flow in L/min.
        '''
        try:
            return float(self.parent.execute(self, "get-flow", [1])[0].rstrip())
        except Exception:
            return None

    def get_flow_target(self):
        '''
        Actual desired flow.

        Returns:
            float: The desired flow in L/min.
        '''
        try:
            return float(self.parent.execute(self, "get-flow-target")[0].rstrip())
        except Exception:
            return None

    def set_flow_target(self, flow):
        '''
        Set flow we want to achieve.

        Args:
            flow (float): flow in L/min we want to achieve (max given by get_flow_max)
        Returns:
            bool: True if was succesful, False otherwise.
        '''
        try:
            return self.parent.execute(self, "set-flow-target", [flow])[0].rstrip() == 'ok'
        except Exception:
            return None

    def get_flow_max(self):
        '''
        Maximal allowed flow.

        Returns:
            float: The maximal flow in L/min
        '''
        try:
            return float(self.parent.execute(self, "get-flow-max")[0].rstrip())
        except Exception:
            return None

    def get_pressure(self, repeats=5, wait=0):
        '''
        Current pressure.

        Returns:
            float: Current pressure in ???
        '''
        try:
            return float(self.parent.execute(self, "get-pressure", [repeats, wait])[0].rstrip())
        except Exception:
            return None
