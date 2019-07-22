import mysql.connector as cn
from time import sleep
from threading import Thread
import queue




def measure(t):
### Add commands to queue every t seconds, will be used for periodical measuring
    while True:
        print('measuring')
        sleep(t)



def db_change(queue):
### Periodically check database and proccess queries one by one if any exist.
### Add received commands to queue in the form of tuple.
### sleep to avoid performance issues
    mydb = cn.connect(user='PBRcontrol', database='localdb', autocommit=True)
    cur = mydb.cursor(buffered=True)
    while True:
        cur.execute("SELECT * FROM commands")
        cmd = cur.fetchone()
        if cmd != None:
            cur.execute('DELETE FROM commands LIMIT 1')
            mydb.commit()

            queue.put(cmd)

        sleep(2)


def execute_cmd(queue):
### check queue of raw commands, call interpreter to translate them and forward to bioreactor
### sleep to avoid performance issues
    while True:
        if  not queue.empty():
            cmd = queue.get()
            print(cmd)
        sleep(2)



if __name__ == '__main__':
    q = queue.Queue()
    ex_cmd= Thread(target=execute_cmd, args=(q,)).start()
    check_db = Thread(target=db_change, args=(q,)).start()
    measurement = Thread(target=measure, args=(60,)).start()




