import requests
import json
import datetime


for i in range (50):
    data = {'id': 2, 'time': str(datetime.datetime.now()), 'args': 'A'}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    data = json.dumps(data)
    (requests.post('http://localhost:5000/command', data = data, headers = headers))