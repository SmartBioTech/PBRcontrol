import jpype
from DeviceModule.HWdevices.PSI_java import JVMController

# Enable Java imports
import jpype.imports

# Pull in types


class Device:
    def __init__(self, ID, address, device_config):
        self.ID = ID
        self.address = address
        self.device = self.connect(device_config)

    def connect(self, device_config):
        if not JVMController.isJVMStarted():
            JVMController.startJVM()

        CommanderConnector = jpype.JClass("psi.bioreactor.commander.CommanderConnector")
        device = CommanderConnector(device_config, self.address, 115200)

        ServerPluginManager = jpype.JClass("psi.bioreactor.server.plugin.ServerPluginManager")
        ServerPluginManager.getInstance().loadPlugins()
        device.connect(0)

        return device

    def disconnect(self):
        self.device.disconnect()

    def __str__(self):
        return self.ID + " @ " + str(self.address)

    def __repr__(self):
        return "VirtualDevice(" + self.ID + ", " + str(self.address) + ")"
