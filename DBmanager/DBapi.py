from flask import request, Flask
from flask_restful import Resource, Api
import mysql.connector as cn
import datetime
from DataManager import datamanager
from DBmanager import measurement
from threading import Event as ThreadEvent
from multiprocessing import Process, Event



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
        self.log_id = 0


    def get_unseen(self, table):
        """
        Read from a table, delete the line that was read

        :param: table to read from (log/measurement)
        :return: the row that was read
        """
        select = ('SELECT * FROM %s WHERE log_id > %s ORDER BY log_id DESC' %(table,self.log_id))

        self.cur.execute(select)
        rows = self.cur.fetchall()
        if rows:
            self.log_id = rows[0][0]
        return rows

    def get_from_time(self, table, time):
        select = ('SELECT * FROM %s WHERE time_issued > %s ORDER BY log_id DESC' %(table,time))
        self.cur.execute(select)
        rows = self.cur.fetchall()
        return rows

class Command(Resource):
    """
    Has a post method - when data are posted to its corresponding endpoint in HTTP (json format), it is read and
    forwarded to database

    Receives json data encoded into http protocol.
    """
    def __init__(self, resource_args, endpoint):
        self.my_data_manager = resource_args[endpoint][0]
        self.q = self.my_data_manager.q
        self.q_new_item = self.my_data_manager.q_new_item



    def post(self):
        cmd = (request.get_data())
        cmd = eval(cmd)
        data = (cmd.get('time', (datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))),
                self.endpoint,
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
        time = request.args.get('time')
        if time == None:
            rows = self.db.get_unseen(self.table)

            return rows
        else:
            try:
                time = self.process_time(time)
                rows = self.db.get_from_time(self.table, time)
                return rows
            except Exception as e:
                return e


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
            experiment_details = node.get('experiment_details')
            devices = node.get('devices')

            for device in devices:
                device_id = devices[device].get('device_id')
                device_details = devices[device]
                end_device = ThreadEvent()
                node_events.append(end_device)
                my_data_manager = datamanager.Manager(device_details, self.end_program, end_device)
                my_data_manager.start()
                setup = device_details.get('setup')
                initial_commands = setup.get('initial_commands', None)



                for setup_cmd in initial_commands:

                    cmd = (
                        setup_cmd['time'],
                        '/' + str(node_id) + '/' + str(device_id),
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
                                                                 experiment_details,
                                                                 self.end_program,
                                                                 )

            if node_id not in self.resource_args.keys():
                self.resource_args[node_id] = [endpoints, node_id, experiment_details, node_measurement, node_events]

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
                self.resource_args[node_id] = [endpoints, node_id, experiment_details, node_measurement, node_events]

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
        self.db = Database()
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

