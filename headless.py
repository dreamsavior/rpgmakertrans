from __future__ import division

from patchers import getPatcher, PatchManager, makeTranslator, writeTranslator, doFullPatches
from filecopier2 import copyfilesAndTrigger
from collections import defaultdict
from twokpatcher import process2kgame
from coreprotocol import CoreProtocol
from mtimesmanager import MTimesHandlerManager, loadMTimes, dumpMTimes

class Headless(CoreProtocol):
    def __init__(self, *args, **kwargs):
        super(Headless, self).__init__(*args, **kwargs)
        self.patchManager = PatchManager()
        self.patchManager.start(self.errout)
        self.mtimesManager = MTimesHandlerManager()
        self.mtimesManager.start(self.errout)
        self.progress = defaultdict(lambda: [0, 1])
        self.progressVal = 0
        
    def setProgressDiv(self, key, div):
        if div != 0:
            self.progress[key][1] = div
        else:
            if key in self.progress:
                del self.progress[key]
        
    def setProgress(self, key, progress):
        self.progress[key][0] = progress
        self.updateProgress()
            
    def incProgress(self, key):
        self.progress[key][0] += 1
        self.updateProgress()
            
    def updateProgress(self):
        newProgressVal = min((x[0] / x[1] for x in self.progress.values()))
        if newProgressVal != self.progressVal: 
            self.outputcoms.send('setProgress', newProgressVal)
            self.progressVal = newProgressVal
        
    def go(self, indir, patchpath, outdir):
        mtimesManager = self.mtimesManager.MTimesHandler(outdir)
        patcher = getPatcher(self.patchManager, patchpath, self.inputcoms, self.errout)
        self.submit('patcher', loadMTimes, mtimesManager, self.inputcoms)
        translatorRet = self.submit('patcher', makeTranslator, patcher, self.inputcoms)
        self.comboTrigger('startTranslation', ['translatorReady', 'mtimesReady'])
        self.localWaitUntil('startTranslation', self.beginTranslation, patcher, 
                            translatorRet, mtimesManager, indir, patchpath, outdir)
        
    def beginTranslation(self, patcher, translatorRet, mtimesManager, indir, patchpath, outdir):
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
        self.submit('patcher', writeTranslator, patcher, translator, self.inputcoms)
        self.submit('copier', dumpMTimes, mtimesManager, self.inputcoms)
        self.comboTrigger('finish', ['translatorWritten', 'mtimesDumped'])
        self.localWaitUntil('finish', self.finish)

        
    def finish(self):
        self.going = False
        self.outputcoms.send('finishedPatching')

    