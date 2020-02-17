from importlib import import_module

from DeviceModule.Command import Command
from DeviceModule.HWdevices.abstract.AbstractPBR import AbstractPBR
from DeviceModule.HWdevices.abstract.AbstractGAS import AbstractGAS
from DeviceModule.HWdevices.abstract.AbstractGMS import AbstractGMS
from Response import Response
from DeviceModule.Interpreter import Interpreter
from DeviceModule.DeviceConfiguration import DeviceConfiguration
from TaskModule.TaskManager import DeviceTaskManager
from DeviceModule.HWdevices.abstract.device import Device as PhysicalDevice


class Device:

    def __init__(self, deviceConfig: DeviceConfiguration):
        self.deviceConfig = deviceConfig
        self.physicalDevice: PhysicalDevice = \
            getattr(
                import_module('HWdevices.' + deviceConfig.deviceClass + '.' + deviceConfig.deviceType),
                deviceConfig.deviceType
            )(deviceConfig)

        self.interpreter = Interpreter(self.physicalDevice, self.deviceConfig)
        self.taskManager = DeviceTaskManager(self)
        self.isActive = True

    def disconnect(self) -> None:
        self.isActive = False
        self.physicalDevice.disconnect()

    def test_connection(self) -> bool:

        try:
            if isinstance(self.physicalDevice, AbstractPBR):
                self.physicalDevice.get_temp()

            elif isinstance(self.physicalDevice, AbstractGAS):
                self.physicalDevice.get_co2_air()

            elif isinstance(self.physicalDevice, AbstractGMS):
                self.physicalDevice.get_valve_flow(1)

        except Exception as e:
            return False

        return True

    def execute_command(self, command: Command) -> Response.Response:
        result = self.interpreter.commands[command.command_id](*command.args)
        if command.command_id == 19:
            if isinstance(self.physicalDevice, AbstractGAS):
                response = Response.GASMeasureAllResponse(command, self.deviceConfig, result)
            elif isinstance(self.physicalDevice, AbstractPBR):
                response = Response.PBRMeasureAllResponse(command, self.deviceConfig, result)
            else:
                response = Response.Response(command, self.deviceConfig, result)
        else:
            response = Response.Response(command, self.deviceConfig, result)

        return response


