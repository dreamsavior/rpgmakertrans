'''
Created on 3 Feb 2013

@author: habisain
'''

from multiprocessing import freeze_support
from rpgmakertransv2.interface.guicontroller import GUIController
from rpgmakertransv2.controllers.coreprotocol import CoreRunner
from rpgmakertransv2.interface.cli import useCLIBackend, CLIBackend
import sys
if __name__ == '__main__':
    freeze_support()
    runner = CoreRunner()
    if useCLIBackend():
        CLIBackend(runner)
    else:
        runner.initialise(GUIController)
    runner.run()
        
