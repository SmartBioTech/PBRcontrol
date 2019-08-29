from flask import request, Flask
from flask_restful import Resource, Api
import mysql.connector as cn
import datetime
import json
from DataManager import datamanager
from DBmanager import measurement


class Database:
    def __init__(self):
        """Establish connection to local database, actions on the database are executed through the use of a cursor
        """
        host = "127.0.0.1"
        user = "PBRcontrol"
        password = ""
        db = "localdb"
        self.con = cn.connect(host=host, user=user, password=password, db=db, autocommit=True)
        self.cur = self.con.cursor()


    def get(self, table):
        """
        Read from a table, delete the line that was read

        :param: table to read from (log/measurement)
        :return: the row that was read
        """
        select = ('SELECT * FROM %s LIMIT 1' % table)
        self.cur.execute(select)
        row = self.cur.fetchone()
        if row != None:
            query = ('DELETE FROM %s LIMIT 1' % table)
            self.cur.execute(query)
        return row


class Command(Resource):
    """
    Has a post method - when data are posted to its corresponding endpoint in HTTP (json format), it is read and
    forwarded to database

    Receives json data encoded into http protocol.
    """
    def __init__(self, data_manager, address):
        self.q = data_manager.q
        self.q_new_item = data_manager.q_new_item
        self.address = address



    def post(self):
        cmd = request.get_json()
        data = (cmd.get('time', (datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))), self.address, (cmd.get('id', False)), (cmd.get('args', '[]')))
        if data[1]:
            self.q.put(data)
            self.q_new_item.set()


class GetData(Resource):
    """
    Parent class for Log and Measurement, its argument is the local database (object).
    """
    def __init__(self, db):
        self.db = db
        self.table = None

    def get(self):
        """
         A method used for reading data from the Log table and Measurement table respectively.

        :return: a list of all rows from the desired table
        """
        row = self.db.get(self.table)
        result = []
        while row != None:
            result.append(row)
            row = self.db.get(self.table)
        return result

class Nodes(Resource):

    def __init__(self, endpoints, node_id, experiment_details, node_measurement):
        self.node_id = node_id
        self.endpoints = endpoints
        self.experiment_details = experiment_details
        self.my_measurement = node_measurement

    def get(self):
        return self.endpoints

    def post(self):
        data = request.json
        cmd_id = data.get('cmd_id', False)
        args = data.get('args', '[]')
        args = eval(args)
        if cmd_id:
            self.my_measurement.execute_cmd(cmd_id, args)


class CreateNewResource(Resource):

    def __init__(self, api):
        self.api = api

    def post(self):
        my_json = request.json
        data=json.loads(my_json)


        for node_id in data:
            endpoints = []
            node = data[node_id]
            experiment_details = node.get('experiment_details')
            devices = node.get('devices')
            for device in devices:
                device_id = devices[device].get('device_id')
                device_details = devices[device]
                my_data_manager = datamanager.Manager(device_details)
                my_data_manager.start()
                setup = device_details.get('setup')
                initial_commands = setup.get('initial_commands', None)
                if initial_commands != None:
                    for setup_cmd in initial_commands:
                        data = (setup_cmd['time'], '/' + str(node_id) + '/' + str(device_id), setup_cmd['id'], setup_cmd['args'])
                        my_data_manager.q.put(data)
                        my_data_manager.q_new_item.set()

                self.api.add_resource(Command, '/' + str(node_id) + '/' + str(device_id), endpoint = str(node_id) + '/' + str(device_id),
                                      resource_class_kwargs={
                                          'data_manager' : my_data_manager,
                                          'address' : '/' + str(node_id) + '/' + str(device_id)
                                      })

                endpoints.append(device_id)
            node_measurement = measurement.PeriodicalMeasurement(endpoints, node_id, experiment_details)

            self.api.add_resource(Nodes, '/' + str(node_id), endpoint = str(node_id),
                              resource_class_kwargs={
                                  'endpoints': endpoints,
                                  'node_id' : node_id,
                                  'experiment_details' : experiment_details,
                                  'node_measurement' : node_measurement
                              })

            node_measurement.start()


class ApiInit:
    '''
    Initializes the API
    '''
        
    def run(self):
        app = Flask(__name__)
        api = Api(app)
        db = Database()

        api.add_resource(CreateNewResource, '/', resource_class_kwargs={'api': api})

        api.add_resource(GetData, '/log', resource_class_kwargs={'db': db, 'table': 'log'})

        app.run(debug=False)