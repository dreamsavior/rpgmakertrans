"""
headless
********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2015
:license: GNU Public License version 3

The Headless implementation is a completely blind patching engine, which
communicates progress/errors etc to an interface, and coordinates the
worker processes.

Obviously, the primary use for Headless is paired with an interface.
"""
import collections

from ..workers.patchers import getPatcher, PatchManager, makeTranslator, writeTranslator, doFullPatches
from ..workers.filecopier2 import copyfilesAndTrigger
from collections import defaultdict
from .coreprotocol import CoreProtocol
from ..workers.mtimesmanager import MTimesHandlerManager, loadMTimes, dumpMTimes

class HeadlessConfig:
    """Simple container to contain all config variables"""
    def __init__(self, useBOM=False, socket=None, rebuild=False,
                 dumpScripts=None, translateLabels=False):
        """Current variables in config:
          - useBOM: If the patch should be written with byte order marks
          - socket: Name of socket to use in SocketComms
          - rebuild: If the patch should be rebuilt
          - dumpScripts: If specified, a directory to dump scripts to
          - translateLabels: If True, put labels into patch
        """
        self.useBOM = useBOM
        self.socket = socket
        self.rebuild = rebuild
        self.dumpScripts = dumpScripts
        self.translateLabels = translateLabels

class HeadlessUtils(CoreProtocol):
    """Defines the utility functions that Headless uses to communicate with
    the UI."""

    def __init__(self, *args, **kwargs):
        """Initialise values"""
        super().__init__(*args, **kwargs)
        self.progress = defaultdict(lambda: [0, float('inf')])
        self.progressVal = 0
        self.epsilon = 1e-2
        self.progressCompleteTriggers = {}

    def nonfatalError(self, msg):
        """Sends a nonfatal error message to the controller of headless"""
        self.outputcoms.send('nonfatalError', msg)

    def fatalError(self, msg):
        """Sends a nonfatal error message and kills the patcher"""
        self.outputcoms.send('nonfatalError', msg)
        self.going = False
        self.outputcoms.send('patchingAborted')
        self.terminate(['patcher', 'copier'])
        self.patchManager.shutdown()
        self.mtimesManager.shutdown()

    def setProgressDiv(self, key, div):
        """Set the divisor of a given key on the progress reporter;
        typically a notion of the size of the complete job for the key"""
        # Dreamsavior
        print("Progress", key, div)
        if div != 0:
            self.progress[key][1] = div
        else:
            if key in self.progress:
                del self.progress[key]

    def setProgressCompleteTrigger(self, key, trigger):
        """Emit a local trigger when a progress counter is complete"""
        self.progressCompleteTriggers[key] = trigger

    def setProgress(self, key, progress):
        """Set the progress of a given key"""
        self.progress[key][0] = progress
        self.updateProgress()

    def incProgress(self, key):
        """Increment the progress for a given key"""
        self.progress[key][0] += 1
        self.updateProgress()

    def updateProgress(self):
        """Update the progress value; communicate if necessary"""
        if self.progress:
            newProgressVal = min((x[0] / x[1]
                                  for x in list(self.progress.values())))
        else:
            newProgressVal = 0
        if newProgressVal >= self.progressVal + self.epsilon: 
            self.outputcoms.send('setProgress', newProgressVal)
            self.progressVal = newProgressVal
        for key in self.progress:
            if self.progress[key][0] == self.progress[key][1]:
                if key in self.progressCompleteTriggers:
                    self.trigger(self.progressCompleteTriggers.pop(key))

    def displayMessage(self, message):
        """Display a message on output coms. This will always be displayed."""
        self.outputcoms.send('displayMessage', message)

    def setMessage(self, message):
        """Display a message near progress bar. It may not be displayed."""
        self.outputcoms.send('setMessage', message)

    def resniffInput(self):
        """Send a message to resniff the input path;
        necessary due to the GUI"""
        self.outputcoms.send('resniffInput')

class Headless(HeadlessUtils):
    """Headless Class"""

    copyIgnoreDirs = []
    copyIgnoreExts = []

    defaultPatchVersion = None
    minPatcherProcesses = None

    def __init__(self, *args, **kwargs):
        """Initialise Headless; for arguments see CoreProtocol"""
        super().__init__(*args, **kwargs)
        self.patchManager = PatchManager()
        self.patchManager.start(self.errout)
        self.mtimesManager = MTimesHandlerManager()
        self.mtimesManager.start(self.errout)

    def go(self, indir, patchpath, outdir, config):
        """Initiate the patching"""
        self.setupPool('patcher', minProcesses=type(self).minPatcherProcesses)
        self.setupPool('copier', processes=1)
        mtimesManager = self.mtimesManager.MTimesHandler(outdir)
        patcher = getPatcher(self.patchManager, patchpath,
                             config.rebuild,
                             self.inputcoms, self.errout,
                             type(self).defaultPatchVersion)
        self.submit('patcher', loadMTimes, mtimesManager, self.inputcoms)
        translatorRet = self.submit('patcher', makeTranslator, patcher,
                                    self.inputcoms, config)
        self.comboTrigger('startTranslation',
                          ['translatorReady', 'mtimesReady'])
        self.localWaitUntil('startTranslation', self.beginTranslation,
                            patcher, translatorRet, mtimesManager, indir,
                            patchpath, outdir, config)

    def processGame(self, indir, outdir, translator, mtimes, newmtimes,
                    config):
        raise NotImplementedError('Override this method')

    def beginTranslation(self, patcher, translatorRet, mtimesManager,
                         indir, patchpath, outdir, config):
        """Begin the translation phase of patching"""
        translator = translatorRet.get()
        dontcopy = patcher.getAssetNames()
        mtimes = mtimesManager.getMTimes()
        newmtimes = mtimesManager.getNewMTimes()

        self.submit('copier', copyfilesAndTrigger, indir=indir, outdir=outdir,
                    ignoredirs=type(self).copyIgnoreDirs,
                    ignoreexts=type(self).copyIgnoreExts,
                    ignorefiles=dontcopy, comsout=self.inputcoms,
                    translator=translator, mtimes=mtimes,
                    newmtimes=newmtimes, progresssig='copying',
                    dirssig='dirsCopied')
        self.setMessage('Patching game')
        self.setProgressDiv('patching', 1)
        self.localWaitUntil('dirsCopied', self.processGame, indir, outdir,
                            translator, mtimes, newmtimes, config)
        self.waitUntil('dirsCopied', 'copier', doFullPatches, patcher,
                       outdir, translator, mtimes, newmtimes, self.inputcoms)
        self.setProgressCompleteTrigger('patching', 'gamePatchingDone')
        self.comboTrigger('patchingFinished',
                          ['fileCopyDone', 'gamePatchingDone',
                           'fullPatchesDone'])
        self.localWaitUntil('patchingFinished', self.finaliseTranslation,
                            patcher, translator, mtimesManager, indir,
                            patchpath, outdir, config)

    def finaliseTranslation(self, patcher, translator, mtimesManager,
                            indir, patchpath, outdir, config):
        """Finalise the translation; write the patch and get mtimes"""
        print("Finalise translation")
        self.setMessage('Finalising Patch')
        self.setMessage('Send to patcher')

        self.submit('patcher', writeTranslator, patcher, translator,
                    config.useBOM, self.inputcoms)
        self.submit('copier', dumpMTimes, mtimesManager,
                    translator.getMTime(), self.inputcoms)
        self.comboTrigger('finish', ['translatorWritten'])
        print("translatorWritten")
        print("waiting for copier")
        self.comboTrigger('finish', ['mtimesDumped'])
        self.localWaitUntil('finish', self.finish, patcher)
        print("Copier finished")


    def finish(self, patcher):
        """End Headless"""
        self.going = False
        print("Closing patcher and copier")
        self.shutdown(['patcher', 'copier'])
        print("Quiting patcher")
        patcher.quit()
        self.patchManager.shutdown()
        self.mtimesManager.shutdown()


def initialiseHeadless(runner, outputComs, gameSniffed, patchSniffed,
                       transSniffed, useBOM):
    """Initialise a Headless instance on a given runner."""
    headlessClasses = gameSniffed.headlessClass
    if not isinstance(headlessClasses, collections.Iterable):
        headlessClasses = [headlessClasses]
    else:
        headlessClasses = list(headlessClasses)
    __initialiseHeadless(runner, outputComs, gameSniffed, patchSniffed,
                         transSniffed, useBOM, headlessClasses)

def __initialiseHeadless(runner, outputComs, gameSniffed, patchSniffed,
                         transSniffed, config, headlessClasses):
    """A special chaining function; this allows multiple Headless classes
    to execute in sequence before signalling completion to the UI, by a minor
    abuse of the runOnFinished functionality in CoreRunner"""
    if len(headlessClasses) == 1:
        runOnFinished = lambda : outputComs.send('headlessFinished')
    else:
        runOnFinished = lambda : __initialiseHeadless(runner, outputComs,
                                    gameSniffed, patchSniffed, transSniffed,
                                    config, headlessClasses)
    gamePath = gameSniffed.canonicalpath
    patchPath = patchSniffed.canonicalpath
    transPath = transSniffed.canonicalpath
    headless = runner.initialise(headlessClasses.pop(0),
                runOnFinished=runOnFinished, outputcoms=outputComs)
    headless.go(gamePath, patchPath, transPath, config)

