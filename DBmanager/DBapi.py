from flask import request
from flask_restful import Resource, Api
import datetime
from DataManager import datamanager
from DBmanager import measurement, localdb
from threading import Event as ThreadEvent
from multiprocessing import Process, Event
import ssl
from time import sleep

class Secured_Resource(Resource):

    def __init__(self, api):
        super(Secured_Resource, self).__init__()
        self.username = api.app.config['USERNAME']
        self.password = api.app.config['PASSWORD']

    def check_credentials(self, auth):

        if auth == None or (auth['username'] == self.username and auth['password'] == self.password):
            return False
        return True

class Command(Secured_Resource):
    """
    Has a post method - when data are posted to its corresponding endpoint in HTTP (json format), it is read and
    forwarded to database
        print(self.address)

    Receives json data encoded into http protocol.
    """
    def __init__(self, api, resource_args, endpoint):
        super(Command, self).__init__(api)
        self.my_data_manager = resource_args[endpoint][0]
        self.q = self.my_data_manager.q
        self.q_new_item = self.my_data_manager.q_new_item
        self.address = endpoint.split('/')


    def post(self):

        if self.check_credentials(request.authorization):
            return 'Invalid Credentials', 401
        try:
            cmd = (request.get_data())
            cmd = eval(cmd)
            data = (cmd.get('time', (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),
                    self.address[0],
                    self.address[1],
                    cmd['cmd_id'],
                    (cmd.get('args', '[]')),
                    cmd.get('source', 'external')
                    )


            self.q.put(data)
            self.q_new_item.set()
        except Exception as e:
            return e, 400

        return 'Success', 200


class GetData(Secured_Resource):
    """
    Parent class for Log and Measurement, its argument is the local database (object).
    """
    def __init__(self, api, db, table):
        super(GetData, self).__init__(api)
        self.db = db
        self.table = table

    def process_time(self, time):
        try:
            processed = "'" + time[:4] + '-' + time[4:6] + '-' + time[6:8] + ' ' + time[8:10] + ':' + time[10:12] + ':' + time[12:14] + "'"
            return processed
        except Exception as e:
            raise Exception(e)

    def get(self):
        """
         A method used for reading data from the Log table and Measurement table respectively.

        :return: a list of all rows from the desired table
        """
        if self.check_credentials(request.authorization):
            return 'Invalid Credentials', 401

        try:
            node_id = request.args.get('node_id')
            time = request.args.get('time')
            if time != None:

                time = self.process_time(time)

            if node_id != None:
                rows = self.db.get_log(node_id, time)

            else:

                rows = self.db.get_from_time(time)
            if rows == []:
                return rows, 204
            else:
                return rows, 200
        except Exception as e:
            return str(e), 400


class Nodes(Secured_Resource):

    def __init__(self, api, resource_args, node_id):
        super(Nodes, self).__init__(api)
        self.node_args = resource_args[node_id]
        self.endpoints = self.node_args[0]
        self.node_id = self.node_args[1]

        self.experiment_details = self.node_args[2]
        self.my_measurement = self.node_args[3]

    def get(self):
        if self.check_credentials(request.authorization):
            return 'Invalid Credentials', 401
        if self.endpoints:
            return self.endpoints, 200
        else:
            return self.endpoints, 204


    def post(self):
        if self.check_credentials(request.authorization):
            return 'Invalid Credentials', 401
        try:
            data = request.get_data()
            data = eval(data)
            cmd_id = data.get('cmd_id', False)
            args = data.get('args', '[]')
            time_issued = data.get('time_issued')
            source = data.get('source', 'external')
            args = eval(args)
            if cmd_id:
                self.my_measurement.execute_cmd(time_issued, cmd_id, args, source)
            return 'success', 200
        
        except Exception as e:
            return e, 400

class EndDevice(Secured_Resource):

    def __init__(self, api, resource_args, endpoint):
        super(EndDevice, self).__init__(api)

        self.device_type = resource_args[endpoint][3]
        self.end_device = resource_args[endpoint][1]
        self.endpoints = resource_args[endpoint][2]

    def get(self):
        if self.check_credentials(request.authorization):
            return 'Invalid Credentials', 401

        self.end_device.set()
        self.endpoints.remove(self.device_type)
        return 'device ' + self.device_type +' ended', 200

class EndNode(Secured_Resource):

    def __init__(self, api, resource_args, node_id):
        super(EndNode, self).__init__(api)
        self.node_id = node_id
        self.node_events = resource_args[node_id][4]
        self.endpoints = resource_args[node_id][0]

    def get(self):
        if self.check_credentials(request.authorization):
            return 'Invalid Credentials', 401

        for event in self.node_events:
            event.set()
        self.endpoints.clear()
        return 'node ' + self.node_id + ' ended', 200

class CreateNewResource(Secured_Resource):

    def __init__(self, api, end_program, resource_args):
        super(CreateNewResource, self).__init__(api)

        self.api = api
        self.end_program = end_program
        self.resource_args = resource_args


    def post(self):
        if self.check_credentials(request.authorization):
            return 'Invalid Credentials', 401

        data = request.get_data()
        data = eval(data)

        for node_id in data:
            node_events = []
            endpoints = []

            node = data[node_id]

            devices = node['devices']

            for device in devices:
                device_type = device.get('device_type')
                device['node'] = node_id
                end_device = ThreadEvent()
                node_events.append(end_device)
                my_data_manager = datamanager.Manager(device, self.end_program, end_device)
                my_data_manager.start()
                initial_commands = device.get('setup').get('initial_commands', [])

                for setup_cmd in initial_commands:

                    cmd = (
                        setup_cmd.get('time', (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),
                        node_id,
                        device_type,
                        setup_cmd['id'],
                        setup_cmd['args'],
                        setup_cmd.get('source','internal')
                           )
                    my_data_manager.q.put(cmd)
                    my_data_manager.q_new_item.set()


                endpoint = str(node_id) + '/' + str(device_type)


                if endpoint not in self.resource_args.keys():

                    self.resource_args[endpoint] = [my_data_manager, end_device, endpoints, device_type]

                    self.api.add_resource(Command, '/' + str(node_id) + '/' + str(device_type),
                                          endpoint = str(node_id) + '/' + str(device_type),
                                          resource_class_kwargs={'api': self.api,
                                                                 'resource_args' : self.resource_args,
                                                                 'endpoint' : endpoint
                                                                 }
                                          )

                    self.api.add_resource(EndDevice, '/' + endpoint + '/end',
                                          endpoint=endpoint + '/end',
                                          resource_class_kwargs={'api':self.api,
                                                                 'resource_args': self.resource_args,
                                                                 'endpoint' : endpoint
                                                                 }
                                          )
                else:
                    self.resource_args[endpoint] = [my_data_manager, end_device, endpoints, device_type]

                endpoints.append(device_type)

            node_measurement = measurement.PeriodicalMeasurement(endpoints,
                                                                 node_id,
                                                                 node['experiment_details'],
                                                                 self.end_program,
                                                                 )

            if node_id not in self.resource_args.keys():
                self.resource_args[node_id] = [endpoints, node_id, node['experiment_details'],
                                               node_measurement, node_events]

                self.api.add_resource(Nodes, '/' + str(node_id),
                                      endpoint = str(node_id),
                                      resource_class_kwargs={
                                          'api': self.api,
                                          'resource_args': self.resource_args,
                                          'node_id' : node_id}
                                      )

                self.api.add_resource(EndNode, '/' + str(node_id) + '/end', endpoint = str(node_id) + '/end',
                                      resource_class_kwargs={
                                          'api':self.api,
                                          'resource_args': self.resource_args,
                                          'node_id' : node_id}
                                      )
            else:
                self.resource_args[node_id] = [endpoints, node_id, node['experiment_details'],
                                               node_measurement, node_events]

            node_measurement.start()
            return 'success', 200

class EndProgram(Secured_Resource):

    def __init__(self, api, end_program, end_process):
        super(EndProgram, self).__init__(api)

        self.end_program = end_program
        self.end_process = end_process

    def get(self):
        if self.check_credentials(request.authorization):
            return 'Invalid Credentials', 401
        self.end_program.set()
        self.end_process.set()
        return 'ending PBRcontrol...', 200


class ApiInit():
    '''
    Initializes the API
        app.config['FOR
    '''
    def __init__(self, app, end_program):
        self.app = app
        self.app.config['USERNAME'] = 'BioArInEO'
        self.app.config['PASSWORD'] = 'sybila'
        self.api = Api(self.app)
        self.db = localdb.Database()
        self.db.create_database()
        self.db.connect()
        self.db.create_table()
        self.end_program = end_program
        self.end_process = Event()


    def run_app(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain('MyCertificate.crt', 'MyKey.key')
        self.app.run(host='0.0.0.0', ssl_context = context)


    def run(self):
        resource_args = {}
        self.api.add_resource(CreateNewResource, '/',
                              resource_class_kwargs={'api': self.api,
                                                     'end_program' : self.end_program,
                                                     'resource_args' : resource_args}
                              )

        self.api.add_resource(GetData, '/log',
                              resource_class_kwargs={'db': self.db,
                                                     'table': 'log',
                                                     'api' : self.api}
                              )

        self.api.add_resource(EndProgram, '/end',
                              endpoint = '/end',
                              resource_class_kwargs={'api': self.api,
                                                     'end_program' : self.end_program,
                                                     'end_process' : self.end_process}
                              )

        server = Process(target=self.run_app)
        server.start()
        self.end_process.wait()
        sleep(1)
        server.terminate()

