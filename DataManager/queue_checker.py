from threading import Thread

class Checker(Thread):
    '''
    checks the shared queue for commands

    :q: queue object
    '''
    def __init__(self, q):
        super(Checker, self). __init__()
        self.q = q

    def run(self):
        while True:
            if self.q:
                print(self.q.get())
            else:
                sleep(0.5)
