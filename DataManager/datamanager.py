from threading import Thread, Event
from DataManager import executioner
import queue
import datetime
from DBmanager import measurement


class Node:

    def __init__(self, data):
        self.devices = {}   # keep a dict of all devices on node
        self.node_id = data['node_id']
        self.experiment_details = data['experiment_details']
        self.measurement = measurement.PeriodicalMeasurement(self.node_id, self.devices, self.experiment_details)
        self.measurement.start()

    def initiate_device(self, device_data):
        device_type = device_data.get('device_type')
        if device_type in self.devices or device_type == None:  # raise exception if device already exists on node
            return False
        device_data['node_id'] = self.node_id
        device = Device(device_data)
        self.devices[device_type] = device
        device.checker.start()

        for cmd in device_data['setup']['initial_commands']: # execute the initial commands
            device.accept_command(cmd)
        return True

    def accept_command(self, cmd):

        processed = (
            cmd.get('time', (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),
            cmd['cmd_id'],
            cmd['args'],
            cmd.get('source', 'internal')
        )

        self.measurement.execute_cmd(*processed)

    def end_node(self):
        for device in self.devices:
            self.devices[device].end()
        self.measurement.end()

    def end_device(self, device):
        self.devices[device].end()
        self.devices.pop(device)


class Device:

    def __init__(self, data):
        self.thread_name = str(data['node_id']) + data['device_type']
        self.data = data
        self.device_type = data['device_type']
        self.q = queue.Queue()
        self.q_new_item = Event()
        self.checker = executioner.Checker(self.q, self.q_new_item, self.data, self.thread_name)

    def accept_command(self, cmd):
        processed = (
            cmd.get('time', (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),
            self.data['node_id'],
            self.device_type,
            cmd['cmd_id'],
            cmd['args'],
            cmd.get('source', 'internal')
        )
        self.q.put(processed)
        self.q_new_item.set()

    def end(self):
        self.q.put(False)
        self.q_new_item.set()


class Manager(Thread):
    '''
    starts the DataManager

    :q: queue object
    :flag: threading.Event() object

    '''
    def __init__(self, device_details, end_device, q, q_new_item):
        self.thread_name = device_details['node_id'] + '-' + str(device_details['device_type'])
        super(Manager, self).__init__(name=self.thread_name)
        self.device_details = device_details
        self.end_device = end_device
        self.q = q
        self.q_new_item = q_new_item

    def run(self):
        checker = executioner.Checker(self.q, self.q_new_item, self.device_details, self.end_device, self.thread_name)
        checker.start()
