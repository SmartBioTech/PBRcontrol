from threading import Thread
import DBmanager

if __name__ == '__main__':

    api = DBmanager.API('PBRcontrol', 'localdb')
    Thread(target=api.run())
    


