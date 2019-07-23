"""
Initialize the Api, connect to database and add resources with corresponding endpoints
"""

from DBmanager import DBapi, localdb
from threading import Thread

class API(Thread):
    '''
    runs the proccesses of DBmanager
    '''
    def __init__(self, user, db, q):
        super(API, self).__init__()
        self.user = user
        self.db = db
        self.q = q

    def run(self):
        db = localdb.DatabaseInit(self.user, self.db)
        api = DBapi.ApiInit(self.q)
        db.run()
        api.run()
