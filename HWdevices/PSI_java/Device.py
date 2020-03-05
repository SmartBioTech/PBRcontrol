import jpype
from HWdevices.PSI_java.jvm import JVMController

# Enable Java imports
import jpype.imports

# Pull in types
from jpype.types import *

from jpype import *


class Device:
    def __init__(self, ID, address, device_config):
        self.ID = ID
        self.address = address
        self.device = self.connect(device_config)

    def connect(self, device_config):
        jvm_controller = JVMController()
        if not jvm_controller.isJVMStarted():
            jpype.addClassPath('HWdevices/PSI_java/lib/jar/bioreactor-commander-0.8.7.jar')
            jvm_controller.startJVM()
        else:
            jpype.attachThreadToJVM()

        CommanderConnector = jpype.JClass("psi.bioreactor.commander.CommanderConnector")
        device = CommanderConnector(device_config, self.address, 115200)

        ServerPluginManager = jpype.JClass("psi.bioreactor.server.plugin.ServerPluginManager")
        ServerPluginManager.getInstance().loadPlugins()
        device.connect(0)

        return device

    def disconnect(self):
        self.device.disconnect()
        jpype.detachThreadFromJVM()

    def __str__(self):
        return self.ID + " @ " + str(self.address)

    def __repr__(self):
        return "Device(" + self.ID + ", " + str(self.address) + ")"
