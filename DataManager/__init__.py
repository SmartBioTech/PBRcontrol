from threading import Thread
from DataManager import queue_checker

class Manager(Thread):
    '''
    starts the DataManager

    :q: queue object
    '''
    def __init__(self, q, flag):
        super(Manager, self).__init__()
        self.q = q
        self.flag = flag

    def run(self):
        checker = queue_checker.Checker(self.q, self.flag)
        checker.start()
