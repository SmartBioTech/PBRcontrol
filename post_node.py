import requests
import json
import datetime

data = {'time': (datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")), 'cmd_id': 1, 'args': '[12]'}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
data = json.dumps(data)
(requests.post('http://localhost:5000/1', data=data, headers=headers))
