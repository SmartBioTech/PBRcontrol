from threading import Thread, Event
import time
from DBmanager import localdb
import datetime


class PeriodicalMeasurement(Thread):

    def execute_cmd(self, time_issued, cmd_id, args, source):
        """
        Execute command which affects the measurement and or all devices on the node it runs on

        :param time_issued: str
        :param cmd_id: int
        :param args: list
        :param source: str

        :return: None
        """
        is_ok = True
        try:
            args = eval(args)
            response = self.commands[cmd_id](*args)
        except Exception as exc:
            response = exc
            is_ok = False

        # save the response to log
        self.logger.update_log(time_issued, self.node_id, 'None', cmd_id, args, (is_ok,response), source)

    def change_time_period(self, t):
        """
        Command used to change thee interval of measurements

        :param t: float
        :return: True if ok -> if not ok, error must occur
        """

        self.experiment_details['sleep_time'] = t
        return True

    def __init__(self, node_id, devices, experiment_details):
        """
        :param node_id: int
        :param devices: list of devices on the node
        :param experiment_details: dict
        """
        super(PeriodicalMeasurement, self).__init__(name=(str(node_id)+'-measurement'))
        self.experiment_details = experiment_details
        self.end_measurement = Event()
        self.devices = devices
        self.node_id = node_id
        self.logger = localdb.Database()
        self.pump_id = pump_id

        self.codes = {'PBR': 19,
                      'GAS': 28}

        self.commands = {35: self.change_time_period}

    def run(self):
        """
        Every t seconds perform measurement

        :return: None
        """
        next_time = time.time() + self.experiment_details['sleep_time']
        while not self.end_measurement.is_set():    # while the end signal wasn't sent
            time.sleep(max(0, next_time - time.time()))
            delay = self.experiment_details['sleep_time']
            self.measure()
            next_time += (time.time() - next_time) // delay * delay + delay

    def measure(self):
        """
        Forward the measure all command to all devices on the node

        :return:  None
        """
        for device_key in self.devices:
            device = self.devices[device_key]
            if device == 'GMS':
                continue
            cmd = {'time': (datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")),
                   'source' : 'internal',
                   'args' : '[]',
                   'cmd_id': self.codes[device.device_type]}

            device.accept_command(cmd)

    def end(self):
        """
        Set a flag to end measurement

        :return: None
        """
        self.end_measurement.set()






