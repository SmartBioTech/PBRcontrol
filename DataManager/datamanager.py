from threading import Thread, Event
from DataManager import executioner
import queue

class Manager(Thread):
    '''
    starts the DataManager

    :q: queue object
    :flag: threading.Event() object

    '''
    def __init__(self, device_details, end_program):
        super(Manager, self).__init__(daemon=True)
        self.q = queue.Queue()
        self.q_new_item = Event()
        self.device_details = device_details
        self.end_program = end_program

    def run(self):
        checker = executioner.Checker(self.q, self.q_new_item, self.device_details, self.end_program)
        checker.start()
        checker.join()
