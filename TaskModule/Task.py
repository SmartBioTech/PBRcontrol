from threading import Thread
from typing import List

from DeviceModule.Command import Command
from TaskModule.TaskManager import QueueOfCommands


class Task(Thread):

    def __init__(self, queues: List[QueueOfCommands]):
        super(Task, self).__init__()
        self.queues = queues

    def add_command(self, command: Command):
        for queueOfCommands in self.queues:
            queueOfCommands.add_command(command)
