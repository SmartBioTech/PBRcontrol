from DBmanager import dbmanager

if __name__ == '__main__':
    '''
    create the shared queue between DBmanager and DataManager and run them
    '''
    api = dbmanager.API('PBRcontrol', 'localdb')
    api.start()









