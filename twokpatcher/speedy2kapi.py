from __future__ import division

import os
from concurrent.futures import ProcessPoolExecutor

from speedy2k import TwoKRPGFile
from errorhook import ErrorClass, errorWrap

class TwoKGame(ErrorClass):
    def __init__(self, inpath, outpath, translator, mtimes, newmtimes, comsout, *args, **kwargs):
        super(TwoKGame, self).__init__(*args, **kwargs)
        self.inpath = inpath
        self.outpath = outpath
        self.translator = translator
        self.mtimes = mtimes
        self.newmtimes = newmtimes
        self.pool = None
        self.comsout = comsout
        self.jobsDone = 0
        self.jobsTotal = 1
    
    def jobs(self):
        jobs = []
        for fn in os.listdir(self.inpath):
            if os.path.splitext(fn)[1].lower() in ('.lmu', '.ldb'):
                infn = os.path.join(self.inpath, fn)
                outfn = os.path.join(self.outpath, fn)
                jobs.append((process2kfile, (infn, outfn, self.mtimes, self.newmtimes, self.translator, 'comsout')))
        self.jobsTotal = len(jobs)
        return jobs
    
    def callback(self, res):
        self.jobsDone += 1
        self.comsout.send('setProgess', 'patching', self.jobsDone / self.jobsTotal)
    
    def run(self):
        if self.pool is not None:
            raise Exception('Trying to run the same TwoKGame Translator twice')
        jobs = self.jobs()
        self.comsout.send('setProgressDiv', 'patching', len(jobs))
        for fn, args in jobs:
            self.comsout.send('waitUntil', 'dirsCopied', 'patcher', fn, *args)
            
#        self.pool = multiprocessing.Pool()
#        for fn, args in jobs:
#            rets[args[0]] = self.pool.apply_async(fn, args, callback=self.callback)
            #apply(fn, args)
#        self.pool.close()
#        self.pool.join()

@errorWrap
def process2kgame(inpath, outpath, translator, mtimes, newmtimes, comsout):
    game = TwoKGame(inpath, outpath, translator, mtimes, newmtimes, comsout)
    game.run()

@errorWrap
def process2kfile(inFileName, outFileName, mtimes, newmtimes, translator, comsout, dbgid=None):
    # Args: inFileName: input file name
    # outFileName: output file name
    # mtimes: the mtimes dictionary    
    name = os.path.split(inFileName)[1].rpartition('.')[0].upper()
    ret = (os.path.getmtime(inFileName), translator.getMTime())
    needOutput = (mtimes.get(name, None) != ret) or not os.path.exists(outFileName)
    if needOutput:
        rpgfile = TwoKRPGFile(name, inFileName, translator)
        rpgfile.parse()
        rpgfile.outputfile(outFileName)
        # TODO: insert new mtime into newmtimes
    comsout.send('incProgress', 'patching')        
    if dbgid:
        return ret, dbgid
    else:
        return ret
