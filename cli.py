'''
Created on 3 Oct 2013

@author: habisain
'''


import sys
import argparse
from coreprotocol import CoreRunner, CoreProtocol
from headless import Headless

VERSION = 2.0
CLI_LENGTH = 79    
    

class CLIMode(CoreProtocol):
    def __init__(self, cargs, runner, *args, **kwargs):
        super(CLIMode, self).__init__(*args, **kwargs)
        # TODO: Need to check if the arguments are actually valid.
        self.quiet = cargs.quiet
        self.normalPrint('RPGMaker Trans v%s'% str(VERSION))
        self.normalPrint('Input path : %s' % cargs.input)
        self.normalPrint('Patch path : %s' % cargs.patch)
        self.normalPrint('Output path: %s' % cargs.output)
        self.progressPrint('Starting patcher...')
        x = Headless(comsout=self.coms)
        runner.attach(x)
        x.go(cargs.input, cargs.patch, cargs.output)
        
    def normalPrint(self, string):
        if not self.quiet:
            print string
            
    def progressPrint(self, string):
        if not self.quiet:
            print string.ljust(CLI_LENGTH) + '\r', 
            sys.stdout.flush()
        
    def setProgress(self, progress):
        hashes = ('#' * int(70 * progress)).ljust(70)
        percent = str(int(progress * 100)).ljust(3)
        self.progressPrint('[%s] %s %%' % (hashes, percent))
    
    def finishedPatching(self):
        self.normalPrint('\nPatching finished')
        self.going = False

longargs = set()
shortargs = set()
for x in sys.argv:
    if x.startswith('--'):
        longargs.add(x)
    elif x.startswith('-'):
        shortargs.add(x)

if '--cli' in longargs or any('c' in x for x in shortargs):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--cli', help='Enable CLI mode', action='store_true')
    parser.add_argument("input", help="Path of input game to patch")
    parser.add_argument("patch", help="Path of patch (directory or zip)")
    parser.add_argument("output", help="Path to output directory (will create missing directories)")
    parser.add_argument('-q','--quiet', help='Suppress all output', action='store_true')
    args = parser.parse_args()
    z = CoreRunner([])
    x = CLIMode(args, z)
    z.attach(x)
    z.run()
