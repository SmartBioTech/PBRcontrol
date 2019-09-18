from threading import Thread
from DBmanager import localdb
from importlib import import_module


class Checker(Thread):
    '''
    checks the shared queue for commands

    :q: queue object
    :flag: threading.Event() object, is set to True when data is added to the queue; if not, the checker will wait
    '''
    def __init__(self, q, q_new_item, device_details, end_program, end_device):
        super(Checker, self). __init__()
        self.q = q
        self.q_new_item = q_new_item
        self.device_details = device_details
        self.end_program = end_program
        self.end_device = end_device

    def run(self):
        log = localdb.Database()
        log.connect()
        device_type = self.device_details['device_type']

        hw_class = getattr(import_module('HWdevices.'+self.device_details['device_class']+'.'+device_type), device_type)

        interpreter = import_module('DataManager.interpreter' + device_type)

        if device_type == 'PBR':
            arguments = [self.device_details, self.q, self.q_new_item, log, hw_class]
        else:
            arguments = [self.device_details, log, hw_class]

        device = interpreter.DeviceManager(*arguments)


        while not self.end_program.is_set() or not self.end_device.is_set():

            if self.q_new_item.is_set():
                while self.q:

                    cmd = self.q.get()
                    response = device.execute(*cmd[1])
                    log.update_log(*response)
                self.q_new_item.clear()
            else:
                self.q_new_item.wait()


