"""
A simple script for ePBR pipes cleaning.

Please use it in the following format:

python3 pump_cleaning.py '["ePBR_01", "ePBR_02"]' 5

"""
from threading import Thread
import sys
import time

from HWdevices.Phenometrics.PBR import PBR

# CONSTANTS

HOST_ADDRESS = '169.254.251.197'
HOST_PORT = 6161
ENCRYPTION_KEY = '29gkymoya3jm6r0b'


ePBRs = eval(sys.argv[-2])
duration = int(sys.argv[-1])

class PipeCleaner(Thread):
    def __init__(self, pbr, steps):
        super(PipeCleaner, self).__init__()
        self.pbr = PBR(pbr, HOST_ADDRESS, HOST_PORT, ENCRYPTION_KEY)
        self.steps = steps

    def run(self):
        for i in range(self.steps):
            self.pbr.set_pump_state(5, True)
            time.sleep(30)

threads = []
print(ePBRs)

for ePBR in ePBRs:
    cleaner = PipeCleaner(ePBR, duration)
    cleaner.start()
    threads.append(cleaner)

for cleaner in threads:
    cleaner.join()