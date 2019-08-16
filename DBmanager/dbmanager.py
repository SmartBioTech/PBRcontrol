"""
Initialize the Api, connect to database and add resources with corresponding endpoints
"""

from DBmanager import DBapi, localdb
from threading import Thread

class API(Thread):
    '''
    runs the proccesses of DBmanager

    :user:  string, credentials to database
    :db:    string, name of the database
    :q:     queue object
    :flag:  threading object, used to notify queue_checker that something was added to queue
    '''
    def __init__(self, user, db):
        super(API, self).__init__()
        self.user = user
        self.db = db

    def run(self):
        db = localdb.DatabaseInit(self.user, self.db)
        api = DBapi.ApiInit()
        db.initialize_database()
        api.run()
