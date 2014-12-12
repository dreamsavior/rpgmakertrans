"""
cli
***

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

A CLI for RPGMaker Trans. Unfortunately, due to Windows being Windows,
this does not yet work on Windows.
"""


import sys
import argparse
from ..controllers.coreprotocol import CoreRunner, CoreProtocol
from ..controllers.headless import Headless2k
from ..version import version

VERSION = version
CLI_LENGTH = 79


class CLIMode(CoreProtocol):
    """The CLI Mode. Much simpler than the GUI mode, to be blunt"""
    def __init__(self, cargs, *args, **kwargs):
        """Initialise the CLI mode, with given CLI arguments"""
        super(CLIMode, self).__init__(*args, **kwargs)
        # TODO: Need to check if the arguments are actually valid.
        self.quiet = cargs.quiet
        self.normalPrint('RPGMaker Trans v%s' % str(VERSION))
        self.normalPrint('Input path : %s' % cargs.input)
        self.normalPrint('Patch path : %s' % cargs.patch)
        self.normalPrint('Output path: %s' % cargs.output)
        self.progressPrint('Starting patcher...')
        self.headless = self.runner.initialise(Headless2k,
                                               outputcoms=self.inputcoms)
        self.runner.attach(self.headless)
        self.headless.go(cargs.input, cargs.patch, cargs.output, useBOM=False)

    def errorMsgQuit(self, string):
        """Write an error message to stderr"""
        sys.stderr.write(string)
        sys.stderr.flush()
        sys.exit(1)

    def normalPrint(self, string):
        """Print something if we're supposed to print"""
        if not self.quiet:
            print(string)

    def progressPrint(self, string):
        """Print something using a progress bar style print"""
        if not self.quiet:
            print('\r' + string.ljust(CLI_LENGTH), end=' ')
            sys.stdout.flush()

    def setProgress(self, progress):
        """Set the current progress"""
        hashes = ('#' * int(70 * progress)).ljust(70)
        percent = str(int(progress * 100)).ljust(3)
        self.progressPrint('[%s] %s %%' % (hashes, percent))
        
    def finalisingPatch(self):
        self.progressPrint('Finalising Patch..')

    def finishedPatching(self):
        """Finish patching"""
        self.normalPrint('\nPatching finished')
        self.going = False


def useCLIBackend():
    """Function to determine if we should use the CLI backend"""
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
    """Function to run the CLI Backend"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--cli', help='Enable CLI mode', 
                        action='store_true')
    parser.add_argument("input", help="Path of input game to patch")
    parser.add_argument("patch", help="Path of patch (directory or zip)")
    parser.add_argument("output",
                        help="Path to output directory (will create)")
    parser.add_argument('-q', '--quiet', help='Suppress all output',
                        action='store_true')
    t = sys.stderr # Hacks to ensure that custom error handling is suppressed
    sys.stderr = sys.__stderr__
    args = parser.parse_args()
    sys.stderr = t
    x = runner.initialise(CLIMode, cargs=args)
    return x

if __name__ == '__main__':
    if useCLIBackend():
        z = CoreRunner([])
        CLIBackend(z)
        z.run()
