'''
Created on 3 Feb 2013

@author: habisain
'''

from multiprocessing import freeze_support
from guicontroller import GUIController
from coreprotocol import CoreRunner
from cli import useCLIBackend, CLIBackend

if __name__ == '__main__':
    freeze_support()
    runner = CoreRunner()
    if useCLIBackend():
        CLIBackend(runner)
    else:
        runner.initialise(GUIController)
    runner.run()
        
