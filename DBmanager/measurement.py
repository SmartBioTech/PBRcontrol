from threading import Thread
from time import sleep
from requests import post
import datetime
import json

class PeriodicalMeasurement(Thread):

    def execute_cmd(self, cmd_id, args):
        self.commands[cmd_id](*args)

    def change_time_period(self, t):

        self.experiment_details['sleep_time'] = t
        print('sleep time changed')

    def __init__(self, endpoints, node_id, experiment_details, end_program):
        super(PeriodicalMeasurement, self).__init__(daemon=True)
        self.experiment_details = experiment_details
        self.endpoints = endpoints
        self.node_id = node_id
        self.end_program = end_program

        self.commands = {34 : self.change_time_period}

    def run(self):
        while not self.end_program.is_set():
            for device in self.endpoints:
                data = {'time': (datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))}
                if 'GMS' in device:
                    return
                elif 'PBR' in device:
                    data['id'] = 19
                elif 'GAS' in device:
                    data['id'] = 28

                headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                data = json.dumps(data)
                post('http://localhost:5000/' + str(self.node_id) + '/' + str(device), data=data, headers=headers)

            sleep(int(self.experiment_details.get('sleep_time', 60)))






