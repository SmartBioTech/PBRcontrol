from threading import Thread
import datetime
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
                print('db connected')
                break
            except Exception:
                time.sleep(2)

        self.cur = self.con.cursor()

    def update_log(self, time_issued, command_id, target, response):
        time_executed = datetime.datetime.now()
        time_executed = time_executed.strftime("%m/%d/%Y, %H:%M:%S")

        query = """INSERT INTO log (time_issued, command_id, target, response, time_executed) VALUES (%s, %s, %s, %s, %s)"""
        query_args = (str(time_issued), int(command_id), str(target), str(response), str(time_executed))


        self.cur.execute(query, query_args)


        print('log updated')


class Checker(Thread):
    '''
    checks the shared queue for commands

    :q: queue object
    :flag: threading.Event() object, is set to True when data is added to the queue; if not, the checker will wait
    '''
    def __init__(self, q, q_new_item, device_details):
        super(Checker, self). __init__()
        self.q = q
        self.q_new_item = q_new_item
        self.device_details = device_details

    def run(self):
        log = Logger()
        device = interpreter.Interpreter(self.device_details, self.q, self.q_new_item)


        print('checker running')
        while True:
            if self.q_new_item.is_set():
                print('flag detected')
                while self.q:
                    cmd = self.q.get()
                    print('this is cmd: ', cmd)
                    response = device.execute(*cmd)
                    print('response: ', response)
                    log.update_log(*response)
                self.q_new_item.clear()
            else:
                self.q_new_item.wait()


