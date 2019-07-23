from flask import Flask, request
from flask_restful import Resource, Api
import mysql.connector as cn


class Database:
    def __init__(self):
        """Establish connection to local database, actions on the database are executed through the use of a cursor
        """
        host = "127.0.0.1"
        user = "PBRcontrol"
        password = ""
        db = "localdb"
        self.con = cn.connect(host=host, user=user, password=password, db=db, autocommit=True)
        self.cur = self.con.cursor()

    def post_command(self, id: int, t: str, args: str):
        """
        Insert a command into table. TODO: rewrite so that the commands are stacked in queue, commands table is redundant

        :id: int, id of the command later to be used by interpreter
        :t: str, time the command was issued
        :args: str, arguments of the command
        """
        query = ("INSERT INTO commands (id, t, args) VALUES ('%d', '%s', '%s')" % (id, t, args))
        self.cur.execute(query)

    def get(self, table):
        """
        Read from a table, delete the line that was read

        :param: table to read from (log/measurement)
        :return: the row that was read
        """
        select = ('SELECT * FROM %s LIMIT 1' % table)
        self.cur.execute(select)
        row = self.cur.fetchone()
        print(row)
        if row != None:
            query = ('DELETE FROM %s LIMIT 1' % table)
            self.cur.execute(query)
        return row


class Command(Resource):
    """
    Has a post method - when data are posted to its corresponding endpoint in HTTP (json format), it is read and
    forwarded to database

    Receives json data encoded into http protocol.
    """
    def __init__(self, db):
        self.db = db

    def post(self):
        cmd = request.get_json()
        self.db.post_command(cmd['id'], (cmd['time']), cmd['args'])


class GetData(Resource):
    """
    Parent class for Log and Measurement, its argument is the local database.
    """
    def __init__(self, db):
        self.db = db
        self.table = None

    def get(self):
        """
         A method used for reading data from the Log table and Measurement table respectively.

        :return: a list of all rows from the desired table
        """
        row = self.db.get(self.table)
        result = []
        while row != None:
            result.append(row)
            row = self.db.get(self.table)
        return result


class Log(GetData):
    def __init__(self, db, table):
        super(Log, self).__init__(db)
        self.table = table


class Measurement(GetData):
    def __init__(self, db, table):
        super(Measurement, self).__init__(db)
        self.table = table


if __name__ == '__main__':
    """
    Initialize the Api, connect to database and add resources with corresponding endpoints
    """
    app = Flask(__name__)
    api = Api(app)

    db = Database()

    api.add_resource(Command, '/command', resource_class_kwargs={'db': db})
    api.add_resource(Log, '/log', resource_class_kwargs={'db': db, 'table': 'log'})
    api.add_resource(Measurement, '/measure', resource_class_kwargs={'db': db, 'table': 'measurement'})

    app.run(debug=False)