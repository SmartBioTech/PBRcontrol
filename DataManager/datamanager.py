from threading import Thread, Event
from DataManager import executioner
import queue

class Manager(Thread):
    '''
    starts the DataManager

    :q: queue object
    :flag: threading.Event() object

    '''
    def __init__(self, device_details, end_program, end_device):
        super(Manager, self).__init__()
        self.q = queue.Queue()
        self.q_new_item = Event()
        self.device_details = device_details
        self.end_program = end_program
        self.end_device = end_device

    def run(self):
        checker = executioner.Checker(self.q, self.q_new_item, self.device_details, self.end_program, self.end_device)
        checker.start()
        checker.join()
