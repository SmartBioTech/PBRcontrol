import requests
import datetime
from time import sleep
from flask import Response
#from urllib3 import disable_warnings
import ssl

#disable_warnings()

'''




DONT FORGET TO CLEAR LOG BEFORE TESTING






'''
def initialize_experiment():
    '''
    Initializes an experiment consisting of 2 nodes (PBR+GAS, PBR+GMS)
    '''

    my_dict = {
        1 : {
            'experiment_details' : {'sleep_time' : 120},
            'devices' : [{
                    'device_type' : 'PBR',
                    'device_class' : 'PSI_test',
                    'address' : None,
                    'setup' : {
                        'initial_commands' : [{'time': (datetime.datetime.utcnow().strftime("%Y-%m-%d, %H:%M:%S")),'cmd_id': 8, 'args': '[1, True]'}],
                        'lower_outlier_tol' : 2,
                        'upper_outlier_tol' : 3,
                        'max_outliers' : 6,
                        'min_OD' : 0.1,
                        'max_OD' : 0.9,
                        'pump_id' : 1
                            }
                            },
                {
                    'device_type' : 'GAS',
                    'device_class' : 'PSI_test',
                    'address' : None,
                    'setup' : {
                        'initial_commands' : []
                            }
                            }
            ]
            },
    2 : {
        'experiment_details' : {'sleep_time' : 180},
        'devices' : [{
                'device_type' : 'PBR',
                'device_class' : 'PSI_test',
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
                        },
            {
                'device_type': 'GMS',
                'device_class': 'PSI_test',
                'address': None,
                'setup': {
                    'initial_commands': []
                }
            }
                    ]
        }
    }

    requests.post('https://192.168.17.59:5000/initiate', str(my_dict), verify=False, auth=('BioArInEO', 'sybila'))

def cmds_PBR():
    '''

    :return: dict of commands for PBR
    '''
    cmds_dict = {
        1: [],
        2: [],
        3: [31],
        4: [],
        5: [1],
        6: [3],
        7: [3, 1, 0.3],
        8: [1, False],
        9: [5],
        10: [1, 25],
        11: [1, False],
        12: [],
        13: [12, True],
        14: [],
        15: [],
        16: [1],
        17: [3],
        18: [],
        19: [],
        20: [7],
        21: [False, 16],
        22: [False, 4]
    }
    return cmds_dict

def cmds_GAS():
    '''

    :return: dict of commands for GAS
    '''
    cmds_dict = {
        23: [3],
        24: [],
        25: [0.2],
        26: [],
        27: [],
        28: [],
        29: [],
        30: [],
        31: [2]
    }
    return cmds_dict

def cmds_GMS():
    '''

    :return: list of commands for GMS
    '''
    cmds_dict = {
        32: [1],
        33: [0],
        34: [1, 0.7]
    }
    return cmds_dict


def test_all():
    '''
    Tests all manual commands excluding ending nodes/devices/program and changing time periods
    :return: None
    '''
    initialize_experiment()
    id = 1
    pbr = cmds_PBR()
    gas = cmds_GAS()
    gms = cmds_GMS()
    while id < 23:
        t = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        r = requests.post('https://192.168.17.59:5000/command?node_id=1&device_type=PBR', str([{'time': t, 'cmd_id': id, 'args': str(pbr[id]), 'source' : 'external'}]), verify=False, auth=('BioArInEO', 'sybila'))
        print(r.status_code, r.text)
        id+=1
        sleep(1)

    while id < 32:
        t = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        r=requests.post('https://192.168.17.59:5000/command?node_id=1&device_type=GAS', str([{'time': t, 'cmd_id': id, 'args': str(gas[id]), 'source' : 'external'}]), verify=False, auth=('BioArInEO', 'sybila'))
        print(r.status_code, r.text)
        sleep(1)
        id+=1

    while id < 35:
        t = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        r = requests.post('https://192.168.17.59:5000/command?node_id=2&device_type=GMS', str([{'time': t, 'cmd_id': id, 'args': str(gms[id]), 'source' : 'external'}]), verify=False, auth=('BioArInEO', 'sybila'))
        print(r.status_code, r.text)

        sleep(1)
        id+=1


def change_time(node, time_period):
    '''
    node: string
    time_period: float

    change time period of periodical measurement on node to a specific time_period
    :return: None
    '''
    t = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    requests.post('https://192.168.17.59:5000/command?node_id='+str(node), str({'time': t, 'cmd_id': 35, 'args': str([time_period]), 'source': 'external'}), verify=False, auth=('BioArInEO', 'sybila'))

def get_log():
    e = requests.get('https://192.168.17.59:5000/log?node_id=1',verify=False, auth=('BioArInEO', 'sybila'))
    print(e.status_code)

def add_node(node_number):
    '''
    node_number: int

    adds node with node_number with a PBR and a GAS device
    :return:
    '''
    str_dict = str({node_number: {'experiment_details': {'sleep_time': 5}, 'devices': [{'device_type': 'PBR', 'device_class': 'PSI_test', 'address': None, 'setup': {'initial_commands': [{'cmd_id': 16, 'args': '[1]'}, {'cmd_id': 13, 'args': '[50, True]'}, {'cmd_id': 8, 'args': '[5, False]'}], 'lower_outlier_tol': 2, 'upper_outlier_tol': 3, 'max_outliers': 6, 'min_OD': 0.45, 'max_OD': 0.5, 'pump_id': 5}}, {'device_type': 'GAS', 'device_class': 'PSI_test', 'address': None, 'setup': {'initial_commands': []}}]}})
    x = requests.post("https://192.168.17.59:5000/initiate", str_dict, verify=False, auth=('BioArInEO', 'sybila'))
    print(x.text)

def post_cmd(node, device_type, cmd_id, args):
    '''
    post command to specific device

    :param node: int/str
    :param device_id: str
    :param cmd_id: int
    :param args: list

    '''
    t = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    x = requests.post('https://192.168.17.59:5000/command?node_id=1&device_type=PBR',
                  str([{'time': t, 'cmd_id': cmd_id, 'args': str(args), 'source': 'external'}]), verify=False,
                  auth=('BioArInEO', 'sybila'))
    print(x.text)

def end_node(node):
    requests.get('https://192.168.17.59:5000/end?node_id='+str(node), verify=False, auth=('BioArInEO', 'sybila'))

def end_device(node, device):
    requests.get('https://192.168.17.59:5000/end?node_id='+str(node)+'&device_type='+device, verify=False, auth=('BioArInEO', 'sybila'))

def end_program():
    requests.get('https://192.168.17.59:5000/end', verify=False, auth=('BioArInEO', 'sybila'))


def get_node_endpoints(node):
    '''

    :param node: int
    :return: list of active devices on given node
    '''
    r = requests.get('https://192.168.17.59:5000/' + str(node), verify=False, auth=('BioArInEO', 'sybila'))
    return r.text

def add_device(node, device):
    data = {
                    'device_type' : device,
                    'device_class' : 'PSI_test',
                    'address' : None,
                    'setup' : {
                        'initial_commands' : [{'time': (datetime.datetime.utcnow().strftime("%Y-%m-%d, %H:%M:%S")),'cmd_id': 8, 'args': '[1, True]'}],
                        'lower_outlier_tol' : 2,
                        'upper_outlier_tol' : 3,
                        'max_outliers' : 6,
                        'min_OD' : 0.1,
                        'max_OD' : 0.9,
                        'pump_id' : 1
                            }
                            }
    t = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    requests.post('https://192.168.17.59:5000/add_device?node_id='+str(node),
                  str(data), verify=False,
                  auth=('BioArInEO', 'sybila'))

def repeat_log():
    while True:
        get_log()
        sleep(3)

#repeat_log()
#test_all()
#add_node(2)
#get_log()
#sleep(2)
#change_time(2, 30)
#post_cmd(1, 'PBR', 10, [1, 30])
#end_device(2, 'PBR')
#end_node(1)
#end_program()
#print(get_node_endpoints(2))
#add_device(2, 'PBR')

def real_test():
    my_dict = {
        1: {
            'experiment_details': {'sleep_time': 60},
            'devices': [{
                'device_type': 'PBR',
                'device_class': 'PSI_java',
                'address': '/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_D-if00-port0',
                'setup': {
                    'initial_commands': [],
                    'lower_outlier_tol': 5,
                    'upper_outlier_tol': 5,
                    'max_outliers': 5,
                    'min_OD': 0.48,
                    'max_OD': 0.52,
                    'pump_id': 5
                }
            }]}}

    x = requests.post('https://192.168.17.59:5000/initiate', str(my_dict), verify=False, auth=('BioArInEO', 'sybila'))
    print(x.text)

#real_test()

response = Response(status = 204)

print(response.body)