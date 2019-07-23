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

    def get_flow(self, repeats: int) -> float:
        """
        Actual flow being send from GAS to the PBR.

        :param repeats: the number of measurement repeats
        :return: The current flow in L/min.
        """
        command = Command("get-flow", [repeats])
        return float(self.scheme_manager.execute([command])[0].rstrip())

    def get_flow_target(self) -> float:
        """
        Actual desired flow.

        :return: The desired flow in L/min.
        """
        command = Command("get-flow-target")
        return float(self.scheme_manager.execute([command])[0].rstrip())

    def set_flow_target(self, flow: float) -> bool:
        """
        Set flow we want to achieve.

        :param flow: flow in L/min we want to achieve (max given by get_flow_max)
        :return: True if was successful, False otherwise.
        """
        command = Command("set-flow-target", [flow])
        result = float(self.scheme_manager.execute([command])[0].rstrip())
        return result == 'ok'

    def get_flow_max(self) -> float:
        """
        Maximal allowed flow.

        :return: The maximal flow in L/min
        """
        command = Command("get-flow-max")
        return float(self.scheme_manager.execute([command])[0].rstrip())

    def get_pressure(self, repeats: int = 5, wait: int = 0) -> float:
        """
        Current pressure.

        :param repeats: the number of measurement repeats
        :param wait: waiting time between individual repeats
        :return: Current pressure in ???
        """
        command = Command("get-pressure", [repeats, wait])
        return float(self.scheme_manager.execute([command])[0].rstrip())

    def measure_all(self):
        """
        Measures all basic measurable values.
        """
        commands = [Command("get-co2-air"),
                    Command("get-flow", [5]),
                    Command("get-pressure", [5, 0])]

        results = self.scheme_manager.execute(commands)

        # manage results
