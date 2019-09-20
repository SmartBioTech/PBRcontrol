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
        1 : {
            'experiment_details' : {'sleep_time' : 10},
            'devices' : {
                'device_1' : {
                    'node': 1,
                    'type' : 'PBR',
                    'device_id' : 'PBR01',
                    'test' : True,
                    'address' : None,
                    'setup' : {
                        'initial_commands' : [{'time': (datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")),'id': 8, 'args': '[1, True]'}],
                        'lower_outlier_tol' : 2,
                        'upper_outlier_tol' : 3,
                        'max_outliers' : 6,
                        'min_OD' : 0.1,
                        'max_OD' : 0.9,
                        'pump_id' : 1
                            }
                            },
                'device_2' : {
                    'node' : 1,
                    'type' : 'GAS',
                    'device_id' : 'GAS01',
                    'test' : True,
                    'address' : None,
                    'setup' : {
                        'initial_commands' : []
                            }
                            }
                        }
            },
    2 : {
        'experiment_details' : {'sleep_time' : 5},
        'devices' : {
            'device_1' : {
                'node' : 1,
                'type' : 'PBR',
                'device_id': 'PBR01',
                'test' : True,
                'address' : None,
                'setup' : {
                    'initial_commands' : [],
                    'lower_outlier_tol' : 2,
                    'upper_outlier_tol' : 3,
                    'max_outliers' : 6,
                    'min_OD' : 0.1,
                    'max_OD' : 0.9,
                    'pump_id' : 1,
                            }
                        }
                    }
        }
    }

#    my_json=json.dumps(my_dict)
    requests.post('http://localhost:5000/', str(my_dict))


post_json()