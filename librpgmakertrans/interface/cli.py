"""
cli
***

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2015
:license: GNU Public License version 3

A CLI for RPGMaker Trans. Unfortunately, due to Windows being Windows,
this does not yet work on Windows.
"""


import sys
import argparse
from ..workers.sniffers import sniff
from ..controllers.coreprotocol import CoreProtocol
from ..controllers.headless import initialiseHeadless
from ..version import versionString

CLI_LENGTH = 79


class CLIMode(CoreProtocol):
    """The CLI Mode. Much simpler than the GUI mode, to be blunt"""
    def __init__(self, cargs, *args, **kwargs):
        """Initialise the CLI mode, with given CLI arguments"""
        super(CLIMode, self).__init__(*args, **kwargs)
        self.quiet = cargs.quiet
        self.normalPrint('RPGMaker Trans v%s' % versionString)
        game = self.handleInput(cargs.input, ['GAME'], 'Input path: %s',
                                'ERROR: %s not a compatible game')
        patch = self.handleInput(cargs.patch, ['PATCH'], 'Patch path: %s',
                                 'ERROR: %s not a compatible patch')
        trans = self.handleInput(cargs.output, ['TRANS'], 'Output path: %s',
                                 'ERROR: %s not a valid target')
        self.progressPrint('Starting patcher...')
        initialiseHeadless(self.runner, self.inputcoms, game, patch, trans,
                           cargs.use_bom)

    def handleInput(self, path, sniffedTypes, frmtString, errString):
        """Standard template function to sniff a path, output appropiately
        and/or blow up if something is invalid"""
        sniffedLS = sniff(path, sniffedTypes)
        if not sniffedLS:
            self.errorMsgQuit(errString % path)
            return
        else:
            sniffed = sniffedLS[0]
            dataString = '[%s] %s' % (']['.join(sniffed.subtypes), path)
            self.normalPrint(frmtString % dataString)
            return sniffed


    def errorMsgQuit(self, string):
        """Write an error message to stderr"""
        sys.stderr.write(string + '\n')
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
        """Trigger for finalising patch"""
        self.progressPrint('Finalising Patch..')

    def finishedPatching(self):
        """Finish patching"""
        self.normalPrint('\nPatching finished')
        self.going = False

def CLIBackend(runner):
    """Function to run the CLI Backend"""
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Path of input game to patch")
    parser.add_argument("patch", help="Path of patch (directory or zip)")
    parser.add_argument("output", help="Path to output directory"
                        " (will create)")
    parser.add_argument('-q', '--quiet', help='Suppress all output',
                        action='store_true')
    parser.add_argument('-b', '--use-bom', help='Use UTF-8 BOM in Patch'
                        'files', action='store_true')
    t = sys.stderr # Hacks to ensure that custom error handling is suppressed
    sys.stderr = sys.__stderr__
    args = parser.parse_args()
    sys.stderr = t
    x = runner.initialise(CLIMode, cargs=args)
    return x
