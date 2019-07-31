'checks whether the the local database and its components exist. If not, it creates them.'

import mysql.connector as cn

class DatabaseInit:
    '''
    Initializes the database
    '''
    def __init__(self, user, db):
        self.user = user
        self.db = db

    def run(self):
        mydb = cn.connect(user=self.user)
        cursor = mydb.cursor()
        query = ('CREATE DATABASE IF NOT EXISTS %s' %self.db)

        cursor.execute(query)
        mydb = cn.connect(user=self.user, db = self.db)
        cursor = mydb.cursor()

        cursor.execute('CREATE TABLE IF NOT EXISTS log (time_issued VARCHAR(255),command_id INT,target VARCHAR(255),response VARCHAR(255),time_executed VARCHAR(255))')

        cursor.execute('CREATE TABLE IF NOT EXISTS measurement (' #TODO arguments
               't VARCHAR(255),'
               'log INT)')

        mydb.commit()

