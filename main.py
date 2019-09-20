from DBmanager import DBapp

if __name__ == '__main__':
    '''
    create the shared queue between DBmanager and DataManager and run them
    '''
    api = DBapp.ApiInit()
    api.run()
    api.end_program.wait()












