from importlib import import_module

from HWdevices.abstract.AbstractPBR import AbstractPBR
from HWdevices.abstract.AbstractGAS import AbstractGAS
from HWdevices.abstract.AbstractGMS import AbstractGMS
from virtual_devices.DeviceConfiguration import DeviceConfiguration


class Device:

    def __init__(self, deviceConfig: DeviceConfiguration):
        self.deviceConfig = deviceConfig
        self.physicalDevice = \
            getattr(
                import_module('HWdevices.'+ deviceConfig.deviceClass + '.' + deviceConfig.deviceType),
                deviceConfig.deviceType
            )(deviceConfig)

    def test_connection(self):

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
