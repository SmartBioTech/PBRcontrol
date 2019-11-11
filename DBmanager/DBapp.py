from flask import request, Flask
from flask_restful import Resource, Api
from DataManager import datamanager
from DBmanager import localdb
from multiprocessing import Event
import ssl
from json import load
from pathlib import Path


class SecuredResource(Resource):
    """
    Parent class for all resources, makes sure the incoming request is authorized.
    """
    def __init__(self, api):
        """
        :param api: parent Flask Api
        """
        super(SecuredResource, self).__init__()
        self.username = api.app.config['USERNAME']
        self.password = api.app.config['PASSWORD']

    def check_credentials(self, auth):

        if auth != None and (auth['username'] == self.username and auth['password'] == self.password):
            return False
        return True


class End(SecuredResource):
    """
    End device, node or the whole program
    """
    def __init__(self, api, active_nodes, end_program):
        """
        :param api: parent Flask Api, used for authorization of connecting users
        :param active_nodes: dictionary of all currently active nodes
        :param end_program: Event() object
        """
        super(End, self).__init__(api)
        self.nodes = active_nodes
        self.end_program = end_program

    def get(self):
        if self.check_credentials(request.authorization):   # check if the user is authorized
            return 'Invalid Credentials', 401

        node_id = request.args.get('node_id', False)
        device_type = request.args.get('device_type', False)

        if node_id:     # if node was specified
            node_id = int(node_id)
            if node_id not in self.nodes:   # if node isn't initialized
                return 'Requested node is not initialized', 400     # return error response
            if device_type:     # if device was specified
                if device_type not in self.nodes[node_id].devices:  # if device isn't initialized
                    return 'Device doesnt exist on node' + str(node_id), 400    # return error response
                self.nodes[node_id].end_device(device_type)     # end the device
                return  # return success response
            self.nodes[node_id].end_node()      # end node
            self.nodes.pop(node_id)     # delete the node from the dict of active nodes
            return  # return success response
        else:   # if node wasn't specified
            for node in self.nodes:
                self.nodes[node].end_node()     # end all nodes

            self.end_program.set()      # end program


class AddDevice(SecuredResource):
    """
    Assign device to an existing node
    """
    def __init__(self, api, active_nodes):
        """
        :param api: parent Flask Api, used for authorization of connecting users
        :param active_nodes: dictionary of all currently active nodes
        """
        super(AddDevice, self).__init__(api)
        self.nodes = active_nodes

    def post(self):
        if self.check_credentials(request.authorization):   # check if the user is authorized
            return 'Invalid Credentials', 401
        try:
            node_id = request.args.get('node_id')
            if node_id == None: # if no node is specified
                return 'Node number unspecified', 400   # return an error response number
            node_id = int(node_id)
            if node_id not in self.nodes:   # if node not initialized
                return 'Requested node is not initialized', 400     # return an error response number

            data = request.get_data()
            data = eval(data)

            response = self.nodes[node_id].initiate_device(data)    # True if initialized, False otherwise

            if response:
                return response, 200

            return response, 400
        except Exception as e:
            return str(e), 500


class NodeInitiation(SecuredResource):
    """
    Create node and its devices on POST request. Provide detailed response as to which nodes and devices have been
    successfully created.     
    """
    def __init__(self, api, active_nodes):
        """
        :param api: parent Flask Api, used for authorization of connecting users
        :param active_nodes: dictionary of all currently active nodes
        """
        super(NodeInitiation, self).__init__(api)
        self.api = api
        self.active_nodes = active_nodes

    def post(self):
        
        if self.check_credentials(request.authorization):   # check if the user is Authorized
            return 'Invalid Credentials', 401
        
        try:
            data = request.get_data()
            data = eval(data)
            response = {}
            
            for node_id in data:    # for each node in the request
                data[node_id]['node_id'] = node_id
                
                if node_id in self.active_nodes:    # if the node is already initiated in the system
                    response[node_id] = 0   # inform the user that the node could not be initiated
                    continue    # loop to another node
                    
                else:   # if the request is valid
                    response[node_id] = {}  # create a dict in the response 

                node = datamanager.Node(data[node_id])  # create the node
                self.active_nodes[node_id] = node   # put it into the active_nodes dict
                
                for device in data[node_id]['devices']: # initiate all device
                    initiated = node.initiate_device(device)    # True/False
                    
                    # inform the user whether the device was successfully created
                    response[node_id][device['device_type']] = initiated

                node.measurement.start()  # start the periodical measurement on every device of the node
            return response, 200
        except Exception as e:
            return str(e), 500


class Command(SecuredResource):
    """
    Receives commands from users on POST request and forwards them to corresponding nodes and devices
    """
    def __init__(self, api, active_nodes):
        """
        :param api: parent Flask Api, used for authorization of connecting users
        :param active_nodes: dictionary of all currently active nodes
        """
        super(Command, self).__init__(api)
        self.nodes = active_nodes

    def post(self):
        if self.check_credentials(request.authorization):   # check if the user is Authorized
            return 0, 401
        try:
            node_id = request.args.get('node_id', False)
            device = request.args.get('device_type', False)

            data = request.get_data()
            data = eval(data)
            if not isinstance(data, list):
                raise Exception('Commands must be ordered in a list')

            if node_id:     
                node_id = int(node_id)
                if node_id not in self.nodes:   # if the requested node is not initiated
                    return 0, 400
                if device:
                    if device not in self.nodes[node_id].devices:  # if the requested device doesn't exist on given node
                        return 0, 400
                    for command in data:   # for each command in the list
                        self.nodes[node_id].devices[device].accept_command(command)  # forward the command to device
                else:   # if no device was specified, the node handles the command
                    for command in data:    # for each command in the list
                        self.nodes[node_id].accept_command(command)   # forward the command to node
            else:
                return 0, 400
            return 1, 200
        except Exception as e:
            return str(e), 500


class GetData(SecuredResource):
    """
    Retrieves data from database
    """
    def __init__(self, api, db):
        """
        :param api: the parent Flask api, used for authorization of Users
        :param db: object allowing us to work with the database
        """
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
         A method used for reading data from the log table

        :return: list of data and corresponding HTTP response code

        """
        if self.check_credentials(request.authorization):   # check if the user has provided the correct credentials
            return 'Invalid Credentials', 401

        try:
            node_id = request.args.get('node_id')  
            time = request.args.get('time')
            time = self.process_time(time)  # process the time intoa valid format
            if node_id != None:     # if node_id was sent
                rows = self.db.get_for_system(node_id, time)    # get data from log for the node_id and (optional) time
            # elif time != None:  # elif time was provided
            # rows = self.db.get_for_user(time)  # get all data from log since given time
            else:
                return 0, 400  # if neither node_id or time was provided, return no data
            return rows, 200

        except Exception as e:  # if an exception has occurred
            return str(e), 500  # return it to the user


class Ping(SecuredResource):

    def __init__(self, api, nodes):
        super(Ping, self).__init__(api)
        self.nodes = nodes

    def get(self):
        if self.check_credentials(request.authorization):   # check if the user has provided the correct credentials
            return 'Invalid Credentials', 401
        response = {}
        for node_id in self.nodes:
            node = self.nodes[node_id]
            response[node.node_id] = []
            for device_type in node.devices:
                device = node.devices[device_type]
                response[node.node_id].append([device.device_class, device.device_type, device.device_id])
        return response, 200


class ApiInit:
    """
    Initializes the API
    """
    def __init__(self):
        self.app = Flask(__name__)
        script_location = Path(__file__).absolute().parent
        with open(str(script_location / 'config.json'), 'r') as config_file:
            config = load(config_file)
            # if no auth is specified in config, no auth will be required
            self.app.config['USERNAME'] = config.get('username', None)
            self.app.config['PASSWORD'] = config.get('password', None)
        self.api = Api(self.app)

        # Initialize the database
        self.db = localdb.Database()
        self.db.connect()

        self.end_program = Event()  # object through which we control when the program ends

    def run_app(self):
        """
        Run the Flask App.

        TODO: Determine on which port to listen

        :return: None, process is stuck on app.run() 
        """
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain('MyCertificate.crt', 'MyKey.key')
        self.app.run(host='0.0.0.0', ssl_context=context)

    def run(self):
        """
        Wrap the app into a process, initiate endpoints and start the server.
        :return: None, function waits for the end_program Event() to be set
        """
        active_nodes = {}   # dictionary of all active_nodes, it is updated whenever new nodes are added/deleted

        self.api.add_resource(Ping, '/ping',
                              resource_class_kwargs={'api': self.api,
                                                     'nodes': active_nodes}
                              )

        self.api.add_resource(NodeInitiation, '/initiate',
                              resource_class_kwargs={'api': self.api,
                                                     'active_nodes': active_nodes}
                              )

        self.api.add_resource(GetData, '/log',
                              resource_class_kwargs={'api': self.api,
                                                     'db': self.db}
                              )

        self.api.add_resource(End, '/end',
                              resource_class_kwargs={
                                  'api': self.api,
                                  'end_program': self.end_program,
                                  'active_nodes': active_nodes}
                              )
        
        self.api.add_resource(Command, '/command', 
                              resource_class_kwargs={'api': self.api,
                                                     'active_nodes': active_nodes})

        self.api.add_resource(AddDevice, '/add_device', resource_class_kwargs={'api': self.api,
                                                                               'active_nodes': active_nodes})

        self.run_app()
