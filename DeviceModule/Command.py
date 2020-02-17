from utils.TimeStamper import TimeString


class Command:

    def __init__(self, command_id: int, args: list, source: str):
        self.args = args
        self.command_id = command_id
        self.time_issued = TimeString.now()
        self.source = source
