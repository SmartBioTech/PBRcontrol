"""
Initialize the Api, connect to database and add resources with corresponding endpoints
"""

from DBmanager import DBapi, localdb
from threading import Thread, Event

class API(Thread):
    '''
    runs the proccesses of DBmanager

    :user:  string, credentials to database
    :db:    string, name of the database
    :q:     queue object
    :flag:  threading object, used to notify queue_checker that something was added to queue
    '''
    def __init__(self):
        super(API, self).__init__()
        self.end_program = Event()


    def run(self):
        db = localdb.Database()

        api = DBapi.ApiInit(self.end_program)
        api.run()




