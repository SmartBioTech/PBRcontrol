import requests
import json
import datetime

data = {'id': 2, 'time': str(datetime.datetime.now()), 'args': 'A'}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
data = json.dumps(data)

(requests.post('http://localhost:5000/log', data = data, headers = headers))