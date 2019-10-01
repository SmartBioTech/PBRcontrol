from threading import Event
from DataManager import executioner
import queue
import datetime
from DBmanager import measurement


class Node:

    def __init__(self, data):
        """
        :param data: check documentation.txt for syntax
        """
        self.devices = {}   # keep a dict of all devices on node
        self.node_id = data['node_id']
        self.experiment_details = data['experiment_details']
        self.measurement = measurement.PeriodicalMeasurement(self.node_id, self.devices, self.experiment_details)

    def initiate_device(self, device_data):
        """
        :param device_data: check documentation.txt for syntax
        :return: True if successfully initialized, False otherwise
        """

        device_type = device_data.get('device_type')
        if device_type in self.devices or device_type == None:  # raise exception if device already exists on node
            return False
        device_data['node_id'] = self.node_id
        device = Device(device_data)
        self.devices[device_type] = device
        device.checker.start()  # start the queue checker

        for cmd in device_data['setup']['initial_commands']: # execute the initial commands
            device.accept_command(cmd)
        return True

    def accept_command(self, cmd):
        """
        Processes the commands that affect all the devices on a certain node (currently used only to change the interval
        of periodical measurements.

        :param cmd: dictionary, check documentation.txt
        :return: None
        """
        processed = (
            cmd.get('time', (datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))),
            cmd['cmd_id'],
            cmd['args'],
            cmd.get('source', 'internal')
        )

        self.measurement.execute_cmd(*processed)    # pass the command

    def end_node(self):
        """
        Ends all devices on the node. End the periodical measurement on the node.
        :return: None
        """
        for device in self.devices:
            self.devices[device].end()
        self.measurement.end()

    def end_device(self, device):
        """
        End a certain device on the node
        :param device: str device_type
        :return: None
        """
        self.devices[device].end()
        self.devices.pop(device)


class Device:

    def __init__(self, data):
        """
        :param data: dictionary, check documentation.txt
        """
        self.thread_name = str(data['node_id']) + data['device_type']
        self.data = data
        self.device_type = data['device_type']
        self.q = queue.Queue()      # Queue object - all commands will be stacking here and waiting for execution
        self.q_new_item = Event()   # Event object - notifies that a new command has been added to queue

        # start the checker of the queue
        self.checker = executioner.Checker(self.q, self.q_new_item, self.data, self.thread_name)

    def accept_command(self, cmd):
        """
        Process the command and add id to the queue of the device.

        :param cmd: dict, check documentation.txt
        :return: None
        """
        processed = [
            cmd.get('time', (datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))),
            self.data['node_id'],
            self.device_type,
            cmd['cmd_id'],
            cmd['args'],
            cmd.get('source', 'internal')
        ]
        if self.device_type == 'PBR' and processed[3] == 19:
            processed[4] = str([self.data['setup']['pump_id']])

        self.q.put(processed)   # put it to queue
        self.q_new_item.set()   # notify checker that a new object has been added to queue

    def end(self):
        """
        Puts False into the queue, which triggers the checker to exit.

        :return: None
        """
        self.q.put(False)
        self.q_new_item.set()

