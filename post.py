import requests
import json
import datetime
from time import sleep

def do():
    for i in range (50):
        data = {'id': 2, 'time': str(datetime.datetime.now()), 'args': 'A'}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = json.dumps(data)
        (requests.post('http://localhost:5000/command', data = data, headers = headers))


for x in range(50):
    do()
    sleep(0.1)