from queue import Queue
from threading import Thread, Event
from typing import Dict

from DeviceModule.Command import Command
from DeviceModule.Device import Device


def create_queues(devices: Dict[str, Device]):
    queues = []
    for name, device in devices:
        queues.append(QueueOfCommands(device))

    return queues


class QueueOfCommands(Queue, Thread):
    def __init__(self, device: Device):
        super(QueueOfCommands, self).__init__()
        self.flag = Event()
        self.device = device

    def add_command(self, command: Command):
        self.put(command)
        self.flag.set()

    def run(self):
        while self.device.isActive:
            self.flag.wait()
            while not self.empty():
                self.device.execute_command(self.get())
            self.flag.clear()
