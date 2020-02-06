"""
A simple script for ePBR tubes cleaning.

Please use it in the following format:

python3 pump_cleaning.py '["ePBR_01", "ePBR_02"]' 5

where ePBR_01, ePBR_02, etc. are ID of PBR and 5 is an integer 
declaring how many time should be turbidostat pump turned on for the specified device.

(" and ' can be interchanged)

"""
import sys
import time

from HWdevices.Phenometrics.PBR import PBR

# CONSTANTS

HOST_ADDRESS = '169.254.251.197'
HOST_PORT = 6161
ENCRYPTION_KEY = '29gkymoya3jm6r0b'


devices = eval(sys.argv[-2])
duration = int(sys.argv[-1])

ePBRs = []

for device in devices:
	ePBRs.append(PBR(device, HOST_ADDRESS, HOST_PORT, ENCRYPTION_KEY))
            
for i in range(duration):
	for pbr in ePBRs:
		pbr.set_pump_state(5, True)
		time.sleep(1)
		pbr.set_pump_state(5, False)
		time.sleep(30)

		print("Each pump was turned on already {} times".format(i))

print("Cleaning finished")
