from threading import Thread
from DataManager import queue_checker

class Manager(Thread):
    '''
    starts the DataManager

    :q: queue object
    '''
    def __init__(self, q):
        super(Manager, self).__init__()
        self.q = q

    def run(self):
        checker = queue_checker.Checker(self.q)
        checker.start()
