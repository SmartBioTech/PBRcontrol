'checks whether the the local database and its components exist. If not, it creates them.'

import mysql.connector as cn
import datetime


class Database:

    def __init__(self):
        self.user = "PBRcontrol"
        self.db = "localdb"
        self.host = "127.0.0.1"
        self.password = ""
        self.node_unseen = {}
        self.create_database()  # initialize the database
        self.create_table()     # initialize the table

    def connect(self):
        """
        Establish connection to the database.

        :return: mysql.connector.connect object
        """
        return cn.connect(host=self.host, user=self.user, password=self.password, db=self.db)

    def create_database(self):
        """
        create the database

        :return: None
        """
        con = cn.connect(user=self.user)
        cursor = con.cursor()
        query = ('CREATE DATABASE IF NOT EXISTS %s' % self.db)
        cursor.execute(query)
        con.commit()

        con.commit()

        cursor.close()
        con.close()

    def create_table(self):
        """
        Create the log table

        :return: None
        """
        con = self.connect()
        cursor = con.cursor()
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

        con.commit()
        cursor.close()
        con.close()


    def get_for_system(self, node_id, time):
        """
        Getter - retrieves data from log and remembers which data have been shown in the current session. Already seen
        data will not be loaded in the next get.

        :param node_id: node_id to search for
        :param time: time from which to begin the search
        :return: list of the table's rows
        """
        con = self.connect()
        cursor = con.cursor()
        if node_id not in self.node_unseen:
            self.node_unseen[node_id] = 0
        if time == None:
            select = ('SELECT * FROM log WHERE log_id > %s AND node_id = %s ORDER BY log_id' %(self.node_unseen[node_id], node_id))
        else:
            select = ('SELECT * FROM log WHERE (node_id = %s AND TIMESTAMP(time_issued) >= TIMESTAMP(%s)) ORDER BY log_id' %(node_id, time))

        cursor.execute(select)
        rows = cursor.fetchall()
        cursor.close()
        con.close()

        if rows:
            self.node_unseen[node_id] = rows[-1][0]

        return rows
    '''
    def get_for_user(self, time):
        con = self.connect()
        cursor = con.cursor()
        if time == None:
            select = ('SELECT * FROM log ORDER BY log_id')
        else:
            select = ('SELECT * FROM log WHERE TIMESTAMP(time_issued) > TIMESTAMP(%s) ORDER BY log_id' %(time))
        cursor.execute(select)
        rows = cursor.fetchall()
        cursor.close()
        con.close()

        return rows
    '''

    def update_log(self, time_issued, node_id, device_type, command_id, target_arguments, response, source):
        """
        Is called by executioner - saves data(responses) to the log table.

        :param time_issued: str
        :param node_id: int
        :param device_type: str
        :param command_id: int
        :param target_arguments: lst
        :param response: tuple
        :param source: str

        :return: None
        """
        con = self.connect()
        cursor = con.cursor()
        time_executed = datetime.datetime.utcnow()
        time_executed = time_executed.strftime("%Y-%m-%d %H:%M:%S")

        query = """INSERT INTO log (time_issued, node_id, device_type, command_id, target, response, time_executed, source) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        query_args = (str(time_issued), int(node_id), str(device_type),
                      int(command_id), str(target_arguments), str(response),
                      str(time_executed), str(source))
        cursor.execute(query, query_args)
        con.commit()
        cursor.close()
        con.close()