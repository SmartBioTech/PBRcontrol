"""
Initialize the Api, connect to database and add resources with corresponding endpoints
"""

from DBmanager import DBapi, localdb
from threading import Thread

class API:

    def __init__(self, user, db):
        self.user = user
        self.db = db

    def run(self):
        db = localdb.DatabaseInit(self.user, self.db)
        api = DBapi.ApiInit()
        db.run()
        Thread(target=api.run())
