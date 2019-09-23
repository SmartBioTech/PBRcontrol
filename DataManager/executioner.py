from threading import Thread
from DBmanager import localdb
from importlib import import_module
from time import sleep


class Checker(Thread):
    """
    Checks the shared queue for commands and forwards them to its actual device.
    """

    def __init__(self, q, q_new_item, device_details, thread_name):
        """
        :param q: queue.Queue() object, commands are put in it
        :param q_new_item: queue.Event() object, is set when new commands are added to it, which triggers the checker
        :param device_details:  dict, check documentation.txt
        :param thread_name: name of the thread, used to identify and keep in tact active threads
        """
        thread_name = thread_name+'-checker'
        super(Checker, self). __init__(name=thread_name)
        self.q = q
        self.q_new_item = q_new_item
        self.device_details = device_details

    def run(self):
        """
        Connect to localdb, import the right module according to device_details, execute commands and log the responses.

        :return: None
        """
        log = localdb.Database()
        log.connect()
        device_type = self.device_details['device_type']

        hw_class = getattr(import_module('HWdevices.'+self.device_details['device_class']+'.'+device_type), device_type)

        interpreter = import_module('DataManager.interpreter' + device_type)

        if device_type == 'PBR':
            arguments = [self.device_details, self.q, self.q_new_item, log, hw_class]
        else:
            arguments = [self.device_details, log, hw_class]

        device = interpreter.DeviceManager(*arguments)

        while True:

            if self.q_new_item.is_set():
                while self.q:

                    cmd = self.q.get()
                    if not cmd:
                        return
                    response = device.execute(*cmd)
                    log.update_log(*response)
                self.q_new_item.clear()
            else:
                self.q_new_item.wait()


