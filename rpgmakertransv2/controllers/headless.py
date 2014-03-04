"""
headless
========

:author: habisain

The Headless implementation is a completely blind patching engine, which
communicates progress/errors etc to an interface, and coordinates the
worker processes.

Obviously, the primary use for Headless is paired with an interface.
"""

from ..workers.patchers import getPatcher, PatchManager, makeTranslator, writeTranslator, doFullPatches
from ..workers.filecopier2 import copyfilesAndTrigger
from collections import defaultdict
from ..workers.twokpatcher import process2kgame
from .coreprotocol import CoreProtocol
from ..workers.mtimesmanager import MTimesHandlerManager, loadMTimes, dumpMTimes

class Headless(CoreProtocol):
    """Headless Class"""
    def __init__(self, *args, **kwargs):
        """Initialise Headless; for arguments see CoreProtocol"""
        super(Headless, self).__init__(*args, **kwargs)
        self.patchManager = PatchManager()
        self.patchManager.start(self.errout)
        self.mtimesManager = MTimesHandlerManager()
        self.mtimesManager.start(self.errout)
        self.progress = defaultdict(lambda: [0, 1])
        self.progressVal = 0
        
    def setProgressDiv(self, key, div):
        """Set the divisor of a given key on the progress reporter; 
        typically a notion of the size of the complete job for the key"""
        if div != 0:
            self.progress[key][1] = div
        else:
            if key in self.progress:
                del self.progress[key]
        
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
        newProgressVal = min((x[0] / x[1] for x in list(self.progress.values())))
        if newProgressVal != self.progressVal: 
            self.outputcoms.send('setProgress', newProgressVal)
            self.progressVal = newProgressVal
        
    def go(self, indir, patchpath, outdir):
        """Initiate the patching"""
        self.setupPool('patcher')
        self.setupPool('copier', processes=1)
        mtimesManager = self.mtimesManager.MTimesHandler(outdir)
        patcher = getPatcher(self.patchManager, patchpath, self.inputcoms, self.errout)
        self.submit('patcher', loadMTimes, mtimesManager, self.inputcoms)
        translatorRet = self.submit('patcher', makeTranslator, patcher, self.inputcoms)
        self.comboTrigger('startTranslation', ['translatorReady', 'mtimesReady'])
        self.localWaitUntil('startTranslation', self.beginTranslation, patcher, 
                            translatorRet, mtimesManager, indir, patchpath, outdir)
        
    def beginTranslation(self, patcher, translatorRet, mtimesManager, indir, patchpath, outdir):
        """Begin the translation phase of patching"""
        translator = translatorRet.get()
        dontcopy = patcher.getAssetNames()
        mtimes = mtimesManager.getMTimes()
        newmtimes = mtimesManager.getNewMTimes()

        self.submit('copier', copyfilesAndTrigger, indir=indir, outdir=outdir,
              ignoredirs=[], ignoreexts=['.lmu', '.ldb', '.lsd'], ignorefiles= dontcopy, 
              comsout=self.inputcoms, translator=translator, mtimes=mtimes, 
              newmtimes=newmtimes, progresssig='copying', dirssig='dirsCopied')
        self.submit('patcher', process2kgame, indir, outdir, translator, 
                mtimes=mtimes, newmtimes=newmtimes, comsout=self.inputcoms)
        self.waitUntil('dirsCopied', 'copier', doFullPatches, patcher, outdir, translator, mtimes, newmtimes, self.inputcoms)
        self.comboTrigger('patchingFinished', ['fileCopyDone', 'gamePatchingDone', 'fullPatchesDone'])
        self.localWaitUntil('patchingFinished', self.finaliseTranslation, patcher, 
                            translator, mtimesManager, indir, patchpath, outdir)
        
    def finaliseTranslation(self, patcher, translator, mtimesManager, indir, patchpath, outdir):
        """Finalise the translation; write the patch and get mtimes"""
        self.outputcoms.send('finalisingPatch')
        self.submit('patcher', writeTranslator, patcher, translator, self.inputcoms)
        self.submit('copier', dumpMTimes, mtimesManager, self.inputcoms)
        self.comboTrigger('finish', ['translatorWritten', 'mtimesDumped'])
        self.localWaitUntil('finish', self.finish)
        
    def finish(self):
        """End Headless"""
        self.going = False
        self.outputcoms.send('finishedPatching')
        self.shutdown(['patcher', 'copier'])
        del self.patchManager
        del self.mtimesManager
    