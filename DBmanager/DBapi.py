from flask import request, Flask
from flask_restful import Resource, Api
import datetime
from DataManager import datamanager
from DBmanager import measurement, localdb
from threading import Event as ThreadEvent
from multiprocessing import Process, Event


class Command(Resource):
    """
    Has a post method - when data are posted to its corresponding endpoint in HTTP (json format), it is read and
    forwarded to database
        print(self.address)

    Receives json data encoded into http protocol.
    """
    def __init__(self, resource_args, endpoint):
        self.my_data_manager = resource_args[endpoint][0]
        self.q = self.my_data_manager.q
        self.q_new_item = self.my_data_manager.q_new_item
        self.address = endpoint.split('/')


    def post(self):
        cmd = (request.get_data())
        cmd = eval(cmd)
        data = (cmd.get('time', (datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))),
                self.address[0],
                self.address[1],
                (cmd.get('cmd_id', False)),
                (cmd.get('args', '[]')),
                 cmd.get('source', '')
                )

        if data[1]:
            self.q.put(data)
            self.q_new_item.set()


class GetData(Resource):
    """
    Parent class for Log and Measurement, its argument is the local database (object).
    """
    def __init__(self, db, table):
        self.db = db
        self.table = table

    def process_time(self, time):
        try:
            processed = "'" + time[:2] + '-' + time[2:4] + '-' + time[4:8] + ' ' + time[8:10] + ':' + time[10:12] + ':' + time[12:14] + "'"
            return processed
        except Exception as e:
            raise Exception(e)

    def get(self):
        """
         A method used for reading data from the Log table and Measurement table respectively.

        :return: a list of all rows from the desired table
        """
        try:
            node_id = request.args.get('node_id')
            time = request.args.get('time')
            if time != None:
                time = self.process_time(time)

            if node_id != None:
                rows = self.db.get_log(node_id, time)
                return rows


            rows = self.db.get_from_time(time)
            return rows
        except Exception as e:
            return str(e)


class Nodes(Resource):

    def __init__(self, resource_args, node_id):
        self.node_args = resource_args[node_id]
        self.endpoints = self.node_args[0]
        self.node_id = self.node_args[1]

        self.experiment_details = self.node_args[2]
        self.my_measurement = self.node_args[3]

    def get(self):
        return self.endpoints

    def post(self):
        data = request.get_data()
        data = eval(data)
        cmd_id = data.get('cmd_id', False)
        args = data.get('args', '[]')
        time_issued = data.get('time_issued')
        source = data.get('source', 'external')
        args = eval(args)
        if cmd_id:
            self.my_measurement.execute_cmd(time_issued, cmd_id, args, source)

class EndDevice(Resource):

    def __init__(self, resource_args,endpoint):
        self.device_id = resource_args[endpoint][3]
        self.end_device = resource_args[endpoint][1]
        self.endpoints= resource_args[endpoint][2]

    def get(self):
        self.end_device.set()
        self.endpoints.remove(self.device_id)

class EndNode(Resource):

    def __init__(self, resource_args, node_id):
        self.node_events = resource_args[node_id][4]
        self.endpoints = resource_args[node_id][0]

    def get(self):
        for event in self.node_events:
            event.set()
        self.endpoints.clear()

class CreateNewResource(Resource):

    def __init__(self, api, end_program, resource_args):
        self.api = api
        self.end_program = end_program
        self.resource_args = resource_args

    def post(self):
        data = request.get_data()
        data = eval(data)

        for node_id in data:
            node_events = []
            endpoints = []

            node = data[node_id]

            devices = node['devices']

            for device in devices:
                device_id = device.get('device_id')
                device['node'] = node_id
                end_device = ThreadEvent()
                node_events.append(end_device)
                my_data_manager = datamanager.Manager(device, self.end_program, end_device)
                my_data_manager.start()
                initial_commands = device.get('setup').get('initial_commands', [])

                for setup_cmd in initial_commands:

                    cmd = (
                        setup_cmd['time'],
                        node_id,
                        device_id,
                       setup_cmd['id'],
                       setup_cmd['args'],
                        'experiment setup'
                           )
                    my_data_manager.q.put(cmd)
                    my_data_manager.q_new_item.set()


                endpoint = str(node_id) + '/' + str(device_id)


                if endpoint not in self.resource_args.keys():

                    self.resource_args[endpoint] = [my_data_manager, end_device, endpoints, device_id]

                    self.api.add_resource(Command, '/' + str(node_id) + '/' + str(device_id),
                                          endpoint = str(node_id) + '/' + str(device_id),
                                          resource_class_kwargs={'resource_args' : self.resource_args,
                                                                 'endpoint' : endpoint
                                                                 }
                                          )

                    self.api.add_resource(EndDevice, '/' + endpoint + '/end',
                                          endpoint=endpoint + '/end',
                                          resource_class_kwargs={'resource_args': self.resource_args,
                                                                 'endpoint' : endpoint
                                                                 }
                                          )
                else:
                    self.resource_args[endpoint] = [my_data_manager, end_device, endpoints, device_id]

                endpoints.append(device_id)

            node_measurement = measurement.PeriodicalMeasurement(endpoints,
                                                                 node_id,
                                                                 node['experiment_details'],
                                                                 self.end_program,
                                                                 )

            if node_id not in self.resource_args.keys():
                self.resource_args[node_id] = [endpoints, node_id, node['experiment_details'], node_measurement, node_events]

                self.api.add_resource(Nodes, '/' + str(node_id),
                                      endpoint = str(node_id),
                                      resource_class_kwargs={
                                          'resource_args': self.resource_args,
                                          'node_id' : node_id}
                                      )

                self.api.add_resource(EndNode, '/' + str(node_id) + '/end', endpoint = str(node_id) + '/end',
                                      resource_class_kwargs={
                                          'resource_args': self.resource_args,
                                          'node_id' : node_id}
                                      )
            else:
                self.resource_args[node_id] = [endpoints, node_id, node['experiment_details'], node_measurement, node_events]

            node_measurement.start()


class EndProgram(Resource):

    def __init__(self, end_program, end_process):
        self.end_program = end_program
        self.end_process = end_process

    def get(self):
        self.end_program.set()
        self.end_process.set()


class ApiInit():
    '''
    Initializes the API
    '''
    def __init__(self, end_program):
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.db = localdb.Database()
        self.db.create_database()
        self.db.connect()
        self.db.create_table()
        self.end_program = end_program
        self.end_process = Event()


    def run_app(self):
        self.app.run(host='0.0.0.0', ssl_context=('cert.pem', 'key.pem'))


    def run(self):
        resource_args = {}
        self.api.add_resource(CreateNewResource, '/',
                              resource_class_kwargs={'api': self.api,
                                                     'end_program' : self.end_program,
                                                     'resource_args' : resource_args}
                              )

        self.api.add_resource(GetData, '/log',
                              resource_class_kwargs={'db': self.db,
                                                     'table': 'log'}
                              )

        self.api.add_resource(EndProgram, '/end',
                              endpoint = '/end',
                              resource_class_kwargs={'end_program' : self.end_program,
                                                     'end_process' : self.end_process}
                              )

        server = Process(target=self.run_app)
        server.start()
        self.end_process.wait()
        server.terminate()

