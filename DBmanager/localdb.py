'checks whether the the local database and its components exist. If not, it creates them.'

import mysql.connector as cn
from time import sleep
import datetime

class Database:
    '''
    Initializes the database
    '''

    def __init__(self):
        self.user = "PBRcontrol"
        self.db = "localdb"
        self.host = "127.0.0.1"
        self.password = ""
        self.log_id = 0

    def create_database(self):
        mydb = cn.connect(user=self.user)
        cursor = mydb.cursor()
        query = ('CREATE DATABASE IF NOT EXISTS %s' %self.db)
        cursor.execute(query)
        mydb.commit()

    def create_table(self):

        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS log (log_id int NOT NULL auto_increment,'
            ' time_issued VARCHAR(255),'
            'target_address VARCHAR(255),'
            'command_id INT,'
            'target VARCHAR(255),'
            'response VARCHAR(1000),'
            'time_executed VARCHAR(255),'
            ' source VARCHAR(255), '
            'PRIMARY KEY (log_id))')

        self.con.commit()

    def connect(self):
        while True:
            try:
                self.con = cn.connect(host=self.host, user=self.user, password=self.password, db=self.db, autocommit=True)
                break
            except Exception as e:
                print(e)
                sleep(2)

        self.cursor = self.con.cursor()

    def get_unseen(self):
        """
        Read from a table, delete the line that was read

        :param: table to read from (log/measurement)
        :return: the row that was read
        """
        select = ('SELECT * FROM log WHERE log_id > %s ORDER BY log_id DESC' %(self.log_id))

        self.cursor.execute(select)
        rows = self.cursor.fetchall()
        if rows:
            self.log_id = rows[0][0]
        return rows

    def get_from_time(self, time):
        select = ('SELECT * FROM log WHERE time_issued > %s ORDER BY log_id DESC' %(time))
        self.cursor.execute(select)
        rows = self.cursor.fetchall()
        return rows

    def update_log(self, time_issued, target_address, command_id, target_arguments, response, source):
        time_executed = datetime.datetime.now()
        time_executed = time_executed.strftime("%m-%d-%Y %H:%M:%S")

        query = """INSERT INTO log (time_issued, target_address, command_id, target, response, time_executed, source) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        query_args = (str(time_issued), str(target_address), int(command_id), str(target_arguments), str(response),
                      str(time_executed), str(source))

        self.cursor.execute(query, query_args)

class DatabaseCon:

    def __init__(self):
        """Establish connection to local database, actions on the database are executed through the use of a cursor
        """
        host = "127.0.0.1"
        user = "PBRcontrol"
        password = ""
        db = "localdb"
        self.con = cn.connect(host=host, user=user, password=password, db=db, autocommit=True)
        self.cur = self.con.cursor()
        self.log_id = 0




