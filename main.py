from server import DBapp

if __name__ == '__main__':
    api = DBapp.ApiInit()
    api.run()
    api.end_program.wait()  # wait for the program to finish to avoid unconnected threads and processes
