from builtins import staticmethod

import jpype

# Enable Java imports
import jpype.imports

# Pull in types
from jpype.types import *

from jpype import *

from utils.singleton import singleton


@singleton
class JVMController:

    def startJVM(self):
        jpype.addClassPath('HWdevices/PSI_java/lib/jar/bioreactor-commander-0.8.7.jar')
        jpype.startJVM(jvmpath=jpype.getDefaultJVMPath(), convertStrings=False,
                       classpath="HWdevices/PSI_java/lib/jar/bioreactor-commander-0.8.7.jar")

    def shutdownJVM(self):
        jpype.shutdownJVM()

    def isJVMStarted(self):
        return jpype.isJVMStarted()
