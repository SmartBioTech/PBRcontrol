from threading import Thread
from time import sleep
from requests import post
import datetime
import json
from DBmanager import localdb

class PeriodicalMeasurement(Thread):

    def execute_cmd(self, time_issued, cmd_id, args, source):
        is_ok = True
        try:
            response = self.commands[cmd_id](*args)
        except Exception as exc:
            response = exc
            is_ok = False
        self.logger.update_log(time_issued, self.node_id, 'None', cmd_id, args, (is_ok,response), source)

    def change_time_period(self, t):

        self.experiment_details['sleep_time'] = t
        return True

    def __init__(self, endpoints, node_id, experiment_details, end_program):
        super(PeriodicalMeasurement, self).__init__(daemon=True)
        self.experiment_details = experiment_details
        self.endpoints = endpoints
        self.node_id = node_id
        self.end_program = end_program
        self.logger = localdb.Database()
        self.logger.connect()

        self.commands = {35 : self.change_time_period}

    def run(self):
        while not self.end_program.is_set() and self.endpoints:
            for device in self.endpoints:
                data = {'time': (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), 'source' : 'internal'}
                if 'GMS' in device:
                    return
                elif 'PBR' in device:
                    data['cmd_id'] = 19
                elif 'GAS' in device:
                    data['cmd_id'] = 28

                headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                data = json.dumps(data)
                post('https://localhost:5000/' + str(self.node_id) + '/' + str(device), data=data, headers=headers, verify=False, auth=('BioArInEO', 'sybila'))

            sleep(int(self.experiment_details.get('sleep_time', 60)))






