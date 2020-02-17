from time import sleep
from typing import List

from TaskModule.Task import Task
from TaskModule.TaskManager import QueueOfCommands


class PeriodicalTask(Task):
    def __init__(self, commands: list, sleep_secs: int, queues: List[QueueOfCommands]):
        super(PeriodicalTask, self).__init__(queues)
        self.commands = commands
        self.sleep_secs = sleep_secs

    # TODO: add way to end task
    def run(self) -> None:
        while True:
            for command in self.commands:
                self.add_command(command)
            sleep(self.sleep_secs)
