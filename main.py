import DBmanager
import DataManager
import queue

if __name__ == '__main__':
    '''
    create the shared queue between DBmanager and DataManager and run them
    '''
    q = queue.Queue()
    api = DBmanager.API('PBRcontrol', 'localdb', q)
    data_m = DataManager.Manager(q, api.flag)
    api.start()
    data_m.start()







