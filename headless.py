from __future__ import division

from patchers import getPatcher, PatchManager
from filecopier2 import copyfiles
import multiprocessing
from collections import defaultdict
from twokpatcher import process2kgame
from coreprotocol import CoreProtocol

class Headless(CoreProtocol):
    def __init__(self):
        super(Headless, self).__init__()
        self.patchManager = PatchManager()
        self.patchManager.start()
        
        self.manager = multiprocessing.Manager()
        self.mtimes = self.manager.dict()
        self.newmtimes = self.manager.dict()
        self.progress = defaultdict(lambda: [0, 1])
        self.progressVal = 0
        self.indir = None
        self.outdir = None
        self.patchpath = None
        
    def reset(self): 
        self.progress = defaultdict(lambda: [0, 1])
        self.progressVal = 0
        self.indir = None
        self.outdir = None
        self.patchpath = None
        for pool in self.pools: pool.join()
        self.pools.clear()
        
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
            self.going = False
        newProgressVal = min((x[0] / x[1] for x in self.progress.values()))
        #print str(round(newProgressVal, 2)) + '\r', 
        # TODO: Send to UI module
                
    def setInDir(self, indir):
        self.indir = indir
        
    def setPatchPath(self, patchpath):
        self.patchpath = patchpath
        
    def setOutDir(self, outdir):
        self.outdir = outdir
        
    def go(self):
        if self.indir and self.outdir and self.patchpath:
            self.patcher = getPatcher(self.patchManager, patchpath, self.coms)
            self.localWaitUntil('patcherReady', self.getTranslator)
            
    def run(self, indir, patchpath, outdir):
        patcher = getPatcher(self.patchManager, patchpath, self.coms)
        translator = patcher.makeTranslator()
        dontcopy = patcher.getAssetNames()
        self.submit('copier', copyfiles, indir=indir, outdir=outdir,
              ignoredirs=[], ignoreexts=['.lmu', '.ldb', '.lsd'], ignorefiles= dontcopy, 
              comsout=self.coms, translator=translator, mtimes=self.mtimes, 
              newmtimes=self.newmtimes, progresssig='copying', dirssig='dirsCopied')
        self.submit('patcher', process2kgame, indir, outdir, translator, 
                mtimes=self.mtimes, newmtimes=self.newmtimes, comsout=self.coms)
        patcher.doFullPatches(outdir, translator, self.mtimes, self.newmtimes)
        super(Headless, self).run()
        patcher.setPath(patchpath + '_2')
        patcher.writeTranslator(translator)
                
    

if __name__ == '__main__':
    indir = '/home/habisain/tr/cr'
    patchpath = '/home/habisain/tr/cr_p'
    outdir = '/home/habisain/tr/cr_t'
    x = Headless()
    x.run(indir, patchpath, outdir)
    