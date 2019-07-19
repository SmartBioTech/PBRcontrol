import mysql.connector as cn
from time import sleep
import interpreter
import datetime
from threading import Thread


class Command:
    def __init__(self, id, time, args):
        self.id = id
        self.time = time
        self.args = args

class Queue:
    def __init__(self, lst=[]):
        self.lst = lst

    def get(self):
        return self.lst.pop(0)

    def add(self,element):
        self.lst.append(element)

    def notEmpty(self):
        if self.lst:
            return True
        return False



def measure():
    while True:
        print('measuring')
        sleep(60)



def db_change(queue):


    while True:
        mydb = cn.connect(user='PBRcontrol', database='localdb',autocommit=True)
        cur = mydb.cursor(buffered=True)
        cur.execute("SELECT * FROM commands")
        cmd = cur.fetchone()

        if cmd != None:
            cur.execute('DELETE FROM commands LIMIT 1')
            mydb.commit()

            queue.add(cmd)

        sleep(2)


def execute_cmd(queue):
    while True:
        if queue.notEmpty():
            cmd = queue.get()
            print(cmd)
        sleep(2)



if __name__ == '__main__':
    queue = Queue()
    ex_cmd= Thread(target=execute_cmd, args=(queue,)).start()
    check_db = Thread(target=db_change, args=(queue,)).start()
    measurement = Thread(target=measure).start()




