import requests
import json
import datetime
from time import sleep

def do():
    for i in range (1):
        data = {'time': (datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")),'id': 0, 'args': '2'}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = json.dumps(data)
        (requests.post('http://localhost:5000/2/PBR01', data = data, headers = headers))
        sleep(0.5)



def post_json():
    my_dict = {
        2 : {
            'device_1' : {
                'type' : 'PBR',
                'id' : 'PBR01',
                'test' : True,
                'address' : None,
                'setup' : [{'time': (datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")),'id': 0, 'args': '5'}]
            }
        }

    }
    my_json=json.dumps(my_dict)
    print(my_json)
    requests.post('http://localhost:5000/', json = my_json)

def get():
    resp = (requests.get('http://localhost:5000/1'))


post_json()
