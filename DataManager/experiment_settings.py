from threading import Thread
import time
import datetime

class PeriodicalMeasurement(Thread):
    '''
    provide a measurement (measure_all) every 60 seconds
    :q: shared queue between data_manager and API
    :flag: threading.Event() object, shared between all scripts using the shared queue
    '''
    def __init__(self,q, q_new_item, device_details , devtype):
        super(PeriodicalMeasurement, self).__init__()
        self.q = q
        self.q_new_item = q_new_item
        self.devtype = devtype
        self.device_details = device_details


    def run(self):
        if 'GMS' in self.devtype:
            return
        elif 'PBR' in self.devtype:
            cmd_id = 19
        elif 'GAS' in self.devtype:
            cmd_id = 27

        while True:
            time.sleep(int(self.device_details.get('measurement_interval', 60)))
            cmd = (datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), cmd_id, None)
            self.q.put(cmd)
            self.q_new_item.set()

class Stabilizer:

    def __init__(self, device_details):
        self.min_OD = device_details.get('min_OD')
        self.max_OD = device_details.get('max_OD')
        self.device_details = device_details

