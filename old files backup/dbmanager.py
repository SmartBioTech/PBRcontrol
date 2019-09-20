"""
Initialize the Api, connect to database and add resources with corresponding endpoints
"""

from DBmanager import DBapp
from threading import Thread, Event

class API(Thread):
    '''
    runs the proccesses of DBmanager

    :user:  string, credentials to database
    :db:    string, name of the database
    :q:     queue object
    :flag:  threading object, used to notify queue_checker that something was added to queue
    '''
    def __init__(self, app):
        super(API, self).__init__(name='API')
        self.app = app

    def run(self):
        api = DBapp.ApiInit(self)
        api.run()




