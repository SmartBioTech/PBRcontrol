from threading import Thread
from datetime import datetime
import time
import mysql.connector as cn
from DataManager import interpreter

class Logger:
    def __init__(self):
        """Establish connection to local database, actions on the database are executed through the use of a cursor
        """
        host = "127.0.0.1"
        user = "PBRcontrol"
        password = ""
        db = "localdb"
        while True:
            try:
                self.con = cn.connect(host=host, user=user, password=password, db=db, autocommit=True)
            except Exception:
                time.sleep(2)
                continue
            break
        self.cur = self.con.cursor()

    def update_log(self, time_issued, command_id, target, response):
        time_executed = datetime.now()
        time_executed = time_executed.strftime("%m/%d/%Y, %H:%M:%S")
        if target[0]=='':
            target[0]='None'
        query = """INSERT INTO log (time_issued, command_id, target, response, time_executed)
                VALUES ('%s', '%s', '%s', '%s', '%s')
                ;""" %((time_issued), str(command_id), str(target[0]), str(response), (time_executed))
        self.cur.execute(query)

class Checker(Thread):
    '''
    checks the shared queue for commands

    :q: queue object
    :flag: threading.Event() object, is set to True when data is added to the queue; if not, the checker will wait
    '''
    def __init__(self, q, flag):
        super(Checker, self). __init__()
        self.q = q
        self.flag = flag

    def run(self):
        log = Logger()
        while True:
            if not self.flag.is_set():
                self.flag.wait()
                while self.q:
                    cmd = self.q.get()
                    response = interpreter.Execute(*cmd)
                    response = response.run()
                    log.update_log(response[0], response[1], response[2], response[3])

                self.flag.clear()