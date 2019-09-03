import requests
import mysql.connector as cn
import datetime
from time import sleep



def initialize_experiment():
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
                'node' : 2,
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

    requests.post('http://localhost:5000/', str(my_dict))

def cmds_PBR():
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
        22: [False, 1]
    }
    return cmds_dict


class Connect:

    def __init__(self):
        """Establish connection to local database, actions on the database are executed through the use of a cursor
        """
        host = "127.0.0.1"
        user = "PBRcontrol"
        password = ""
        db = "localdb"
        self.con = cn.connect(host=host, user=user, password=password, db=db, autocommit=True)
        self.cur = self.con.cursor()

    def get_from_log(self, time, id):
        query = 'SELECT * FROM log WHERE time_issued = %s AND command_id = %s'
        query_args = (time, id)
        self.cur.execute(query, query_args)
        my_result = self.cur.fetchall()
        return my_result


def testPBR():
    initialize_experiment()
    id = 1
    cmds_dict = cmds_PBR()
    db = Connect()
    while id < 23:
        t = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        requests.post('http://localhost:5000/1/PBR01', str({'time': t, 'cmd_id': id, 'args': str(cmds_dict[id])}))
        x = []
        while not x:
            x = db.get_from_log(t, id)
        print(x)
        id+=1



testPBR()