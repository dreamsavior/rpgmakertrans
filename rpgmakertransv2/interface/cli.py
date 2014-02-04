'''
Created on 3 Oct 2013

@author: habisain
'''


import sys
import argparse
from ..controllers.coreprotocol import CoreRunner, CoreProtocol
from ..controllers.headless import Headless

VERSION = 2.0
CLI_LENGTH = 79    
    

class CLIMode(CoreProtocol):
    def __init__(self, cargs, *args, **kwargs):
        super(CLIMode, self).__init__(*args, **kwargs)
        # TODO: Need to check if the arguments are actually valid.
        self.quiet = cargs.quiet
        self.normalPrint('RPGMaker Trans v%s'% str(VERSION))
        self.normalPrint('Input path : %s' % cargs.input)
        self.normalPrint('Patch path : %s' % cargs.patch)
        self.normalPrint('Output path: %s' % cargs.output)
        self.progressPrint('Starting patcher...')
        self.headless = self.runner.initialise(Headless, outputcoms=self.inputcoms)
        self.runner.attach(self.headless)
        self.headless.go(cargs.input, cargs.patch, cargs.output)
        
    def errorMsgQuit(self, string):
        sys.stderr.write(string)
        sys.stderr.flush()
        sys.exit(1)
        
    def normalPrint(self, string):
        if not self.quiet:
            print(string)
            
    def progressPrint(self, string):
        if not self.quiet:
            print(string.ljust(CLI_LENGTH) + '\r', end=' ') 
            sys.stdout.flush()
        
    def setProgress(self, progress):
        hashes = ('#' * int(70 * progress)).ljust(70)
        percent = str(int(progress * 100)).ljust(3)
        self.progressPrint('[%s] %s %%' % (hashes, percent))
    
    def finishedPatching(self):
        self.normalPrint('\nPatching finished')
        self.going = False

def useCLIBackend():
    longargs = set()
    shortargs = set()
    for x in sys.argv:
        if x.startswith('--'):
            longargs.add(x)
        elif x.startswith('-'):
            shortargs.add(x)
    
    if '--cli' in longargs or any('c' in x for x in shortargs):
        return True
    else:
        return False
        
def CLIBackend(runner):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--cli', help='Enable CLI mode', action='store_true')
    parser.add_argument("input", help="Path of input game to patch")
    parser.add_argument("patch", help="Path of patch (directory or zip)")
    parser.add_argument("output", help="Path to output directory (will create missing directories)")
    parser.add_argument('-q','--quiet', help='Suppress all output', action='store_true')
    t = sys.stderr
    sys.stderr = sys.__stderr__
    args = parser.parse_args()
    sys.stderr = t
    x = runner.initialise(CLIMode, args)
    return x

if __name__ == '__main__':
    if useCLIBackend():
        z = CoreRunner([])
        CLIBackend(z)
        z.run()