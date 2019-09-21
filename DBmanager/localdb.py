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
        self.node_unseen = {}

    def create_database(self):
        mydb = cn.connect(user=self.user)
        cursor = mydb.cursor()
        query = ('CREATE DATABASE IF NOT EXISTS %s' %self.db)
        cursor.execute(query)
        mydb.commit()

    def create_table(self):
        cursor = self.con.cursor()
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS log (log_id int NOT NULL auto_increment,'
            'time_issued VARCHAR(255),'
            'node_id INT,'
            'device_type VARCHAR(255),'
            'command_id INT,'
            'target VARCHAR(255),'
            'response VARCHAR(1000),'
            'time_executed VARCHAR(255),'
            ' source VARCHAR(255), '
            'PRIMARY KEY (log_id))')

        self.con.commit()
        cursor.close()

    def connect(self):
        while True:
            try:
                self.con = cn.connect(host=self.host, user=self.user, password=self.password, db=self.db, autocommit=True)
                break
            except Exception as e:
                print(e)
                sleep(2)


    def get_log(self, node_id, time):
        """
        Read from a table, delete the line that was read

        :param: table to read from (log/measurement)
        :return: the row that was read
        """
        cursor = self.con.cursor()
        if node_id not in self.node_unseen:
            self.node_unseen[node_id] = 0
        if time == None:
            select = ('SELECT * FROM log WHERE log_id > %s AND node_id = %s ORDER BY log_id' %(self.node_unseen[node_id], node_id))
        else:
            select = ('SELECT * FROM log WHERE (node_id = %s AND TIMESTAMP(time_issued) >= TIMESTAMP(%s)) ORDER BY log_id' %(node_id, time))

        cursor.execute(select)
        rows = cursor.fetchall()
        if rows:
            self.node_unseen[node_id] = rows[-1][0]

        cursor.close()
        return rows

    def get_from_time(self, time):
        cursor = self.con.cursor()
        if time == None:

            select = ('SELECT * FROM log ORDER BY log_id')
        else:
            select = ('SELECT * FROM log WHERE TIMESTAMP(time_issued) > TIMESTAMP(%s) ORDER BY log_id' %(time))
        cursor.execute(select)
        rows = cursor.fetchall()
        cursor.close()

        return rows

    def update_log(self, time_issued, node_id, device_type, command_id, target_arguments, response, source):
        cursor = self.con.cursor()
        time_executed = datetime.datetime.now()
        time_executed = time_executed.strftime("%Y-%m-%d %H:%M:%S")

        query = """INSERT INTO log (time_issued, node_id, device_type, command_id, target, response, time_executed, source) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        query_args = (str(time_issued), int(node_id), str(device_type), int(command_id), str(target_arguments), str(response),
                      str(time_executed), str(source))
        print(query_args)
        cursor.execute(query, query_args)
        cursor.close()


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




