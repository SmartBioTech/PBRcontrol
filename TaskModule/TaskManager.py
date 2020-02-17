from typing import List

from DeviceModule.Command import Command
from DeviceModule.Device import Device
from DeviceModule.Node import Node
from TaskModule.PeriodicalTask import PeriodicalTask
from DeviceModule.QueueOfCommands import QueueOfCommands, create_queues
from TaskModule.Task import Task


def task_types() -> dict:
    return {
        "PERIODICAL TASK": PeriodicalTask
    }


def create_task(self, args: list, tag: str) -> Task:
    return task_types()[tag](*args, self.queues)


class TaskManager:

    def __init__(self, queues: List[QueueOfCommands]):
        self.tasks = []
        self.queues = queues

    def task(self, task: Task) -> None:
        task.start()

    def append_task(self, task: Task) -> None:
        self.tasks.append(task)

    def post_command(self, command: Command):
        for queue in self.queues:
            queue.add_command(command)


class DeviceTaskManager(TaskManager):

    def __init__(self, device: Device):
        super(DeviceTaskManager, self).__init__([QueueOfCommands(device)])
        self.device = device

    def task(self, task: Task) -> None:
        self.append_task(task)
        task.start()


class NodeTaskManager(TaskManager):

    def __init__(self, node: Node):
        super(NodeTaskManager, self).__init__(*(create_queues(node.devices)))
        self.node = node

    def task(self, task: Task) -> None:
        for key, device in self.node.devices:
            task = device.taskManager.task(task)
            self.append_task(task)
