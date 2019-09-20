from threading import Thread, Event
import time
from DBmanager import localdb
import datetime


class PeriodicalMeasurement(Thread):

    def execute_cmd(self, time_issued, cmd_id, args, source):
        is_ok = True
        try:
            args = eval(args)
            response = self.commands[cmd_id](*args)
        except Exception as exc:
            response = exc
            is_ok = False
        self.logger.update_log(time_issued, self.node_id, 'None', cmd_id, args, (is_ok,response), source)

    def change_time_period(self, t):

        self.experiment_details['sleep_time'] = t
        return True

    def __init__(self, node_id, devices, experiment_details):
        super(PeriodicalMeasurement, self).__init__(name=(str(node_id)+'-measurement'))
        self.experiment_details = experiment_details
        self.end_measurement = Event()
        self.devices = devices
        self.node_id = node_id
        self.logger = localdb.Database()
        self.logger.connect()

        self.codes = {'PBR': 19,
                      'GAS': 28}

        self.commands = {35 : self.change_time_period}

    def run(self):

        next_time = time.time() + self.experiment_details['sleep_time']
        while not self.end_measurement.is_set():
            time.sleep(max(0, next_time - time.time()))
            delay = self.experiment_details['sleep_time']
            self.measure()
            next_time += (time.time() - next_time) // delay * delay + delay

    def measure(self):
        for device_key in self.devices:
            device = self.devices[device_key]
            if device == 'GMS':
                continue
            cmd = {'time': (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                   'source' : 'internal',
                   'args' : '[]',
                   'cmd_id': self.codes[device.device_type]}

            device.accept_command(cmd)


    def end(self):
        self.end_measurement.set()






