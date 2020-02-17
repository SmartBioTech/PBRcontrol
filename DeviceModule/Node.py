from DeviceModule.Device import Device
from DeviceModule.NodeConfiguration import NodeConfiguration
from TaskModule.TaskManager import NodeTaskManager
from typing import Dict


class Node:

    def __init__(self, nodeConfig: NodeConfiguration):
        self.nodeConfig = nodeConfig
        self.devices: Dict[str, Device] = {}
        self.taskManager = NodeTaskManager(self)

    def add_device(self, device: Device):
        self.devices[device.deviceConfig.deviceType] = device

    def remove_device(self, device_type: str):
        self.devices.pop(device_type)

    def remove_node(self):
        for key, device in self.devices:
            device.disconnect()
