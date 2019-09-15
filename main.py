from DBmanager import dbmanager
from urllib3 import disable_warnings
from flask import Flask


if __name__ == '__main__':
    '''
    create the shared queue between DBmanager and DataManager and run them
    '''
    app = Flask(__name__)
    disable_warnings()
    api = dbmanager.API(app)
    api.start()
    api.join()












