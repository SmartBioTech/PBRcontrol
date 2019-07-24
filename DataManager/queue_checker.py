from threading import Thread

class Checker(Thread):
    '''
    checks the shared queue for commands

    :q: queue object
    '''
    def __init__(self, q, flag):
        super(Checker, self). __init__()
        self.q = q
        self.flag = flag

    def run(self):
        while True:
            if not self.flag.is_set():
                self.flag.wait()
                while self.q:
                    print(counter, self.q.get())
                self.flag.clear()