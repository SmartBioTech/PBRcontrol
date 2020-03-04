from DBmanager import DBapp
from HWdevices.PSI_java.jvm import JVMController

if __name__ == '__main__':
    jvm = JVMController()
    jvm.startJVM()
    api = DBapp.ApiInit()
    api.run()
    api.end_program.wait()  # wait for the program to finish to avoid unconnected threads and processes
