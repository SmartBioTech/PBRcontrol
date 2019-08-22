from threading import Thread
from time import sleep
from requests import post
import datetime

class PeriodicalMeasurement(Thread):

    def execute_cmd(self, cmd_id, args):
        self.commands[cmd_id](*args)

    def change_time_period(self, t):
        self.experiment_details['sleep_time'] = t

    def __init__(self, endpoints, node_id, experiment_details):
        super(PeriodicalMeasurement, self).__init__()
        self.experiment_details = experiment_details
        self.endpoints = endpoints
        self.node_id = node_id

        self.commands = {1 : change_time_period}

    def run(self):
        while True:
            for device in endpoints:
                data = {'time': (datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))}
                if device = 'GMS':
                    return
                elif device == 'PBR':
                    data['id'] = 19
                elif device == 'GAS'
                    data['id'] = 28

                headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                data = json.dumps(data)
                post('http://localhost:5000/' + str(node_id) + '/' + device, data=data, headers=headers)

            sleep(int(self.experiment_details.get('sleep_time', 60)))




