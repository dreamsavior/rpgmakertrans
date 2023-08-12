"""
cli
***

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2015
:license: GNU Public License version 3

A CLI for RPGMaker Trans.
"""

import sys
import argparse
import shutil
import os
from librpgmakertrans.workers.sniffers import sniff
from librpgmakertrans.controllers.coreprotocol import CoreProtocol, CoreRunner
from librpgmakertrans.controllers.headless import initialiseHeadless, HeadlessConfig
from librpgmakertrans.version import versionString


class CLIMode(CoreProtocol):
    """The CLI Mode. Much simpler than the GUI mode, to be blunt"""
    def __init__(self, cargs, *args, **kwargs):
        """Initialise the CLI mode, with given CLI arguments"""
        super(CLIMode, self).__init__(*args, **kwargs)
        self.quiet = cargs.quiet
        self.needNewLine = False
        self.normalPrint('RPGMaker Trans v%s' % versionString)
        game = self.handleInput(cargs.input, ['GAME', 'TRANS'],
                                'Input path: %s',
                                'ERROR: %s not a compatible game')
        patchPath = cargs.patch if cargs.patch else game.canonicalpath.rstrip(os.sep) + '_patch'
        patch = self.handleInput(patchPath, ['PATCH'], 'Patch path: %s',
                                 'ERROR: %s not a compatible patch')
        outPath = cargs.output if cargs.output else game.canonicalpath.rstrip(os.sep) + '_translated'
        trans = self.handleInput(outPath, ['TRANS'], 'Output path: %s',
                                 'ERROR: %s not a valid target')
        if cargs.dump_scripts:
            self.normalPrint('Dumping Scripts to %s' % cargs.dump_scripts)
        if patch.extraData:
            if 'banner.txt' in patch.extraData:
                self.normalPrint('Patch Banner:\n\n%s' % patch.extraData['banner.txt'])
        self.progressPrint('Starting patcher...')
        self.message = ''
        self.progress = 0
        config = HeadlessConfig(useBOM=cargs.use_bom, socket=cargs.socket,
                                rebuild=cargs.rebuild,
                                dumpScripts=cargs.dump_scripts,
                                translateLabels=cargs.dump_labels)
        initialiseHeadless(self.runner, self.inputcoms, game, patch, trans,
                           config)

    def handleInput(self, path, sniffedTypes, frmtString, errString):
        """Standard template function to sniff a path, output appropiately
        and/or blow up if something is invalid. sniffedTypes gives a list
        of all types to check using sniffers, but only the first main type
        is valid (as GAME has to checked with TRANS.)"""
        sniffedLS = sniff(path, sniffedTypes)
        if not sniffedLS or sniffedLS[0].maintype != sniffedTypes[0]:
            self.errorMsgQuit(errString % path)
        else:
            sniffed = sniffedLS[0]
            dataString = '[%s] %s' % (']['.join(sniffed.subtypes), path)
            self.normalPrint(frmtString % dataString)
            return sniffed

    def setMessage(self, message):
        """Set message to side of progress bar. If it's too long,
        ignore it."""
        message = message.strip()
        if len(message) < 30:
            self.message = message + ' '
        else:
            self.message = ''
        self.printProgress()

    def displayMessage(self, message):
        """Display a message"""
        self.normalPrint(message)

    def errorPrint(self, message):
        """Print to stderr"""
        print(message, file=sys.__stderr__)

    def nonfatalError(self, message):
        """Print a non fatal error message"""
        self.errorPrint(message)

    def errorMsgQuit(self, message):
        """Write an error message to stderr and quit"""
        self.errorPrint(message)
        sys.exit(1)

    def normalPrint(self, string):
        """Print something if we're supposed to print"""
        if not self.quiet:
            if self.needNewLine:
                print()
            self.needNewLine = False
            print(string)

    def progressPrint(self, string):
        """Print something using a progress bar style print"""
        if not self.quiet:
            columns = shutil.get_terminal_size().columns - 2
            print('\r' + string.ljust(columns), end=' ')
            sys.stdout.flush()
            self.needNewLine = True

    def setProgress(self, progress):
        """Set the current progress"""
        self.progress = progress
        self.printProgress()
        
    def patchingAborted(self):
        """Quit"""
        self.errorPrint('Patching aborted')
        sys.exit(1)

    def printProgress(self):
        """Print current progress to screen"""
        if not self.quiet:
            columns = shutil.get_terminal_size().columns - 2
            blocksInBar = columns - 9 - len(self.message)
            hashes = ('#' * int(blocksInBar * self.progress)).ljust(blocksInBar)
            percent = str(int(self.progress * 100)).ljust(3)
            self.progressPrint('%s[%s] %s %%' % (self.message, hashes, percent))

    def headlessFinished(self):
        """Finish patching"""
        self.normalPrint('\nFinished.')
        self.going = False

    def resniffInput(self):
        """On CLI, not required to do anything for this"""

def CLIBackend(runner):
    """Function to run the CLI Backend"""
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Path of input game to patch")
    parser.add_argument("-p", "--patch", help="Path of patch (directory or zip)"
                        "(Defaults to input_directory_patch")
    parser.add_argument("-o", "--output", help="Path to output directory "
                        "(will create) (Defaults to input_directory_translated)")
    parser.add_argument('-q', '--quiet', help='Suppress all output',
                        action='store_true')
    parser.add_argument('-b', '--use-bom', help='Use UTF-8 BOM in Patch'
                        'files', action='store_true')
    parser.add_argument('-r', '--rebuild', help="Rebuild patch against game",
                        action="store_true")
    parser.add_argument('-s', '--socket', type=int, default=27899,
                        help='Socket to use for XP/VX/VX Ace patching'
                        '(default: 27899)')
    parser.add_argument('-l', '--dump-labels', action="store_true",
                        help="Dump labels to patch file")
    parser.add_argument('--dump-scripts', type=str, default=None,
                        help="Dump scripts to given directory")
    
    t = sys.stderr # Hacks to ensure that custom error handling is suppressed
    sys.stderr = sys.__stderr__
    args = parser.parse_args()
    sys.stderr = t
    x = runner.initialise(CLIMode, cargs=args)
    return x

def launchCLI():
    """Launch the CLI"""
    runner = CoreRunner()
    CLIBackend(runner)
    runner.run()
