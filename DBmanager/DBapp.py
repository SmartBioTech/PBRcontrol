from flask import request, Flask
from flask_restful import Resource, Api
import datetime
from DataManager import datamanager
from DBmanager import measurement, localdb
from threading import Event as ThreadEvent
from multiprocessing import Process, Event
import ssl
from time import sleep

class Secured_Resource(Resource):
    '''
    Parent class for all resources, makes sure the incoming request is authorized.
    '''
    def __init__(self, api):
        super(Secured_Resource, self).__init__()
        self.username = api.app.config['USERNAME']
        self.password = api.app.config['PASSWORD']

    def check_credentials(self, auth):

        if auth == None or (auth['username'] == self.username and auth['password'] == self.password):
            return False
        return True

class End(Secured_Resource):

    def __init__(self, api, active_nodes, end_program):
        super(End, self).__init__(api)
        self.nodes = active_nodes
        self.end_program = end_program

    def get(self):
        if self.check_credentials(request.authorization):
            return 'Invalid Credentials', 401
        node_id = request.args.get('node_id', False)
        device_type = request.args.get('device_type', False)

        if node_id:
            node_id = int(node_id)
            if node_id not in self.nodes:
                return 'Requested node is not initialized', 400
            if device_type:
                if device_type not in self.nodes[node_id].devices:
                    return 'Device doesnt exist on node' + str(node_id), 400
                self.nodes[node_id].end_device(device_type)
                return
            self.nodes[node_id].end_node()
            self.nodes.pop(node_id)
            return
        else:
            for node in self.nodes:
                self.nodes[node].end_node()

            self.end_program.set()

class AddDevice(Secured_Resource):

    def __init__(self, api, active_nodes):
        super(AddDevice, self).__init__(api)
        self.nodes = active_nodes


    def post(self):
        if self.check_credentials(request.authorization):
            return 'Invalid Credentials', 401

        node_id = request.args.get('node_id')
        if node_id == None:
            return 'Node number unspecified', 400
        node_id = int(node_id)
        if node_id not in self.nodes:
            return 'Requested node is not initialized', 400

        data = request.get_data()
        data = eval(data)

        response = self.nodes[node_id].initiate_device(data)

        if response:
            return response, 200

        return response, 400


class NodeInitiation(Secured_Resource):

    def __init__(self, api, active_nodes):
        super(NodeInitiation, self).__init__(api)

        self.api = api
        self.active_nodes = active_nodes

    def post(self):

        if self.check_credentials(request.authorization):
            return 'Invalid Credentials', 401

        data = request.get_data()
        data = eval(data)
        response = {}
        for node_id in data:
            data[node_id]['node_id'] = node_id
            if node_id in self.active_nodes:
                response[node_id] = False
                continue
            else:
                response[node_id] = {}

            node = datamanager.Node(data[node_id])
            self.active_nodes[node_id] = node
            for device in data[node_id]['devices']:
                initiated = node.initiate_device(device)
                response[node_id][device['device_type']] = initiated

        return response, 200


class Command(Secured_Resource):

    def __init__(self, api, active_nodes):
        super(Command, self).__init__(api)
        self.nodes = active_nodes

    def post(self):
        if self.check_credentials(request.authorization):
            return False, 401

        node_id = request.args.get('node_id', False)
        device = request.args.get('device_type', False)

        data = request.get_data()
        data = eval(data)

        if node_id:
            node_id = int(node_id)
            if node_id not in self.nodes:
                return False, 400
            if device:
                if device not in self.nodes[node_id].devices:
                    return False, 400
                for command in data:
                    self.nodes[node_id].devices[device].accept_command(command)
            else:
                for command in data:
                    self.nodes[node_id].accept_command(command)
        else:
            return False, 400
        return True, 200

class GetData(Secured_Resource):
    """
    Retrieves data from database
    """
    def __init__(self, api, db):
        super(GetData, self).__init__(api)
        self.db = db

    def process_time(self, time):
        """
        Processes the input string to a format the database can work with.
        :param time: requested time
        :return: processed time
        """
        if time == None:
            return
        try:
            processed = "'" + time[:4] + '-' \
                        + time[4:6] + '-' + time[6:8] \
                        + ' ' + time[8:10] + ':' \
                        + time[10:12] + ':' \
                        + time[12:14] + "'"
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
            time = self.process_time(time)
            if node_id != None:
                rows = self.db.get_log(node_id, time)
            elif time != None:
                rows = self.db.get_from_time(time)
            else:
                return [], 204
            if rows:
                return rows, 200
            else:
                return [], 204

        except Exception as e:
            return str(e), 500

class ApiInit():
    '''
    Initializes the API and connects to database
    '''
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['USERNAME'] = 'BioArInEO'
        self.app.config['PASSWORD'] = 'sybila'
        self.api = Api(self.app)
        self.db = localdb.Database()
        self.db.create_database()
        self.db.connect()
        self.db.create_table()
        self.end_program = Event()


    def run_app(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain('MyCertificate.crt', 'MyKey.key')
        self.app.run(host='0.0.0.0', ssl_context = context)


    def run(self):
        active_nodes = {}
        server = Process(target=self.run_app)

        self.api.add_resource(NodeInitiation, '/initiate',
                              resource_class_kwargs={'api': self.api,
                                                     'active_nodes': active_nodes}
                              )

        self.api.add_resource(GetData, '/log',
                              resource_class_kwargs={'api': self.api,
                                                     'db': self.db}
                              )

        self.api.add_resource(End, '/end',
                              endpoint = '/end',
                              resource_class_kwargs={
                                  'api': self.api,
                                  'end_program': self.end_program,
                                  'active_nodes': active_nodes}
                              )
        self.api.add_resource(Command, '/command', resource_class_kwargs={'api': self.api,
                                                                          'active_nodes': active_nodes})

        self.api.add_resource(AddDevice, '/add_device', resource_class_kwargs={'api': self.api,
                                                                               'active_nodes': active_nodes})

        server.start()

        self.end_program.wait()
        sleep(1)
        print('ending')

        server.terminate()

