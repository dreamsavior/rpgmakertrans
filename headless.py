from __future__ import division

from patchers import getPatcher, PatchManager, makeTranslator, writeTranslator
from filecopier2 import copyfiles
from collections import defaultdict
from twokpatcher import process2kgame
from coreprotocol import CoreProtocol, CoreRunner
from mtimesmanager import MTimesHandlerManager, loadMTimes, dumpMTimes

class Headless(CoreProtocol):
    def __init__(self, *args, **kwargs):
        super(Headless, self).__init__()
        self.patchManager = PatchManager()
        self.patchManager.start()
        self.mtimesManager = MTimesHandlerManager()
        self.mtimesManager.start()
        self.progress = defaultdict(lambda: [0, 1])
        self.progressVal = 0
        
    def setProgressDiv(self, key, div):
        self.progress[key][1] = div
        
    def setProgress(self, key, progress):
        self.progress[key][0] = progress
        self.updateProgress()
            
    def incProgress(self, key):
        self.progress[key][0] += 1
        self.updateProgress()
            
    def updateProgress(self):
        if all((x[0] == x[1] for x in self.progress.values())):
            self.trigger('patchingFinished')
        newProgressVal = min((x[0] / x[1] for x in self.progress.values()))
        #print str(round(newProgressVal, 2)) + '\r', 
        # TODO: Send to UI module
        
    def go(self, indir, patchpath, outdir):
        mtimesManager = self.mtimesManager.MTimesHandler(patchpath)
        patcher = getPatcher(self.patchManager, patchpath, self.coms)
        self.submit('patcher', loadMTimes, mtimesManager, self.coms)
        translatorRet = self.submit('patcher', makeTranslator, patcher, self.coms)
        self.comboTrigger('startTranslation', ['translatorReady', 'mtimesReady'])
        self.localWaitUntil('startTranslation', self.beginTranslation, patcher, 
                            translatorRet, mtimesManager)
        
    def beginTranslation(self, patcher, translatorRet, mtimesManager):
        translator = translatorRet.get()
        dontcopy = patcher.getAssetNames()
        mtimes = mtimesManager.getMTimes()
        newmtimes = mtimesManager.getNewMTimes()

        self.submit('copier', copyfiles, indir=indir, outdir=outdir,
              ignoredirs=[], ignoreexts=['.lmu', '.ldb', '.lsd'], ignorefiles= dontcopy, 
              comsout=self.coms, translator=translator, mtimes=mtimes, 
              newmtimes=newmtimes, progresssig='copying', dirssig='dirsCopied')
        self.submit('patcher', process2kgame, indir, outdir, translator, 
                mtimes=mtimes, newmtimes=newmtimes, comsout=self.coms)
        patcher.doFullPatches(outdir, translator, mtimes, newmtimes) # TODO: Make asyncronous!
        self.localWaitUntil('patchingFinished', self.finaliseTranslation, patcher, 
                            translator, mtimesManager)
        
    def finaliseTranslation(self, patcher, translator, mtimesManager):
        patcher.setPath(patchpath + '_2') # Debug only
        self.submit('patcher', writeTranslator, patcher, translator, self.coms)
        self.submit('copier', dumpMTimes, mtimesManager, self.coms)
        self.comboTrigger('finish', ['translatorWritten', 'mtimesDumped'])
        self.localWaitUntil('finish', self.finish)

        
    def finish(self):
        self.going = False

if __name__ == '__main__':
    indir = '/home/habisain/tr/cr'
    patchpath = '/home/habisain/tr/cr_p'
    outdir = '/home/habisain/tr/cr_t'
    x = Headless()
    z = CoreRunner([x])
    x.go(indir, patchpath, outdir)
    z.run()
    