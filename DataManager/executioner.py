from threading import Thread

import jpype

from DBmanager import localdb
from importlib import import_module

from DataManager.base_interpreter import BaseInterpreter
from HWdevices.PSI_java.Device import Device


class Checker(Thread):
    """
    Checks the shared queue for commands and forwards them to its actual device.
    """

    def __init__(self, q, q_new_item, device_details, thread_name, experimental_details, hw_device, log):
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
        self.experimental_details = experimental_details
        self.device: BaseInterpreter = hw_device
        self.log = log
        if isinstance(self.device.device, Device):
            jpype.attachThreadToJVM()

    def run(self):
        """
        Connect to localdb, import the right module according to device_details, execute commands and log the responses.

        :return: None
        """

        while True:     # for as long as the program runs
            if self.q_new_item.is_set():    # if sth was added to queue
                while self.q:   # while there still is something in queue

                    cmd = self.q.get()  # get 1st command in queue
                    if not cmd:     # if the command is False
                        self.device.end()
                        return      # end the loop and exit
                    response = self.device.execute(*cmd)     # execute the command on the device and save the response
                    self.log.update_log(*response)   # upload the response to log
                self.q_new_item.clear()     # when the queue is finally empty again, clear the flag
            else:
                self.q_new_item.wait()  # if flag isn't set (nothing was added to queue), wait for it to be set


