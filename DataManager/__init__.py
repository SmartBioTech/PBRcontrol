from threading import Thread
from DataManager import data_manager

class Manager(Thread):
    '''
    starts the DataManager

    :q: queue object
    :flag: threading.Event() object

    '''
    def __init__(self, q, flag):
        super(Manager, self).__init__()
        self.q = q
        self.flag = flag

    def run(self):
        checker = data_manager.Checker(self.q, self.flag)
        checker.start()
