from threading import Thread
from DBmanager import localdb


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

        if self.device_details['type'] == 'PBR':
            from DataManager import interpreterPBR as interpreter
            arguments = [self.device_details, self.q, self.q_new_item, log]
        else:
            if self.device_details['type'] == 'GAS':
                from DataManager import interpreterGAS as interpreter
            elif self.device_details['type'] == 'GMS':
                from DataManager import interpreterGMS as interpreter
            arguments = [self.device_details, log]


        device = interpreter.DeviceManager(*arguments)


        while not self.end_program.is_set() or not self.end_device.is_set():

            if self.q_new_item.is_set():
                while self.q:

                    cmd = self.q.get()
                    try:
                        response = device.execute(*cmd)
                    except Exception as e:
                        print(cmd)
                    log.update_log(*response)
                self.q_new_item.clear()
            else:
                self.q_new_item.wait()


