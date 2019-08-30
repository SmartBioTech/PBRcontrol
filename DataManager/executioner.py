from threading import Thread
import datetime
import mysql.connector as cn
from time import sleep

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
                break
            except Exception:
                sleep(2)

        self.cur = self.con.cursor()

    def update_log(self, time_issued, target_address, command_id, target_arguments, response):
        time_executed = datetime.datetime.now()
        time_executed = time_executed.strftime("%m/%d/%Y, %H:%M:%S")

        query = """INSERT INTO log (time_issued, target_address, command_id, target, response, time_executed) VALUES (%s, %s, %s, %s, %s, %s)"""
        query_args = (str(time_issued), str(target_address), int(command_id), str(target_arguments), str(response), str(time_executed))


        self.cur.execute(query, query_args)




class Checker(Thread):
    '''
    checks the shared queue for commands

    :q: queue object
    :flag: threading.Event() object, is set to True when data is added to the queue; if not, the checker will wait
    '''
    def __init__(self, q, q_new_item, device_details, end_program):
        super(Checker, self). __init__()
        self.q = q
        self.q_new_item = q_new_item
        self.device_details = device_details
        self.end_program = end_program

    def run(self):
        log = Logger()

        if self.device_details['type'] == 'PBR':
            from DataManager import interpreterPBR as interpreter
            arguments = [self.device_details, self.q, self.q_new_item, log]
        else:
            if self.device_details['type'] == 'GAS':
                from DataManager import interpreterGAS as interpreter
            elif self.device_details['type'] == 'GMS':
                from DataManager import interpreterGMS as interpreter
            arguments = [self.device_details, log]
        device = interpreter.DeviceManager(*arguments)


        while not self.end_program.is_set():

            if self.q_new_item.is_set():
                while self.q:
                    cmd = self.q.get()
                    response = device.execute(*cmd)
                    log.update_log(*response)
                self.q_new_item.clear()
            else:
                self.q_new_item.wait()


