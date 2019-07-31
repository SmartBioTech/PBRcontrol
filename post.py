import requests
import json
import datetime
from time import sleep

def do():
    for i in range (50):
        data = {'id': 2, 'time': (datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")), 'args': ''}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = json.dumps(data)
        (requests.post('http://localhost:5000/command', data = data, headers = headers))


for x in range(3):
    do()
    sleep(0.1)