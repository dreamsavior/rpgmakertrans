"""
speedy2kaapi
************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

The API that RPGMaker Trans uses to perform patching on a 2k game.
"""

import os

from .speedy2k import TwoKRPGFile
from ...errorhook import ErrorMeta, errorWrap


class TwoKGame(object, metaclass=ErrorMeta):

    def __init__(self, inpath, outpath, translator, mtimes, newmtimes,
                 comsout, *args, **kwargs):
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
                jobs.append((process2kfile,
                             (infn, outfn, self.mtimes, self.newmtimes,
                              self.translator, 'outputcoms')))
        self.jobsTotal = len(jobs) - 1
        return jobs

    def callback(self, res):
        self.jobsDone += 1
        self.comsout.send('setProgess', 'patching', 
                          self.jobsDone / self.jobsTotal)

    def run(self):
        jobs = self.jobs()
        self.comsout.send('setProgressDiv', 'patching', self.jobsTotal)
        for fn, args in jobs:
            self.comsout.send('waitUntil', 'dirsCopied', 'patcher', fn, *args)

@errorWrap
def process2kgame(inpath, outpath, translator, mtimes, newmtimes, comsout):
    game = TwoKGame(inpath, outpath, translator, mtimes, newmtimes, comsout)
    game.run()
    comsout.send('trigger', 'gamePatchingDone')


@errorWrap
def process2kfile(inFileName, outFileName, mtimes, newmtimes,
                  translator, comsout, dbgid=None):
    # Args: inFileName: input file name
    # outFileName: output file name
    # mtimes: the mtimes dictionary
    name = os.path.split(inFileName)[1].rpartition('.')[0].upper()
    ret = (os.path.getmtime(inFileName), translator.getMTime())
    needOutput = ((mtimes.get(name,None) != ret) or 
                  not os.path.exists(outFileName))
    if needOutput:
        rpgfile = TwoKRPGFile(name, inFileName, translator)
        rpgfile.parse()
        rpgfile.outputfile(outFileName)
        newmtime = (os.path.getmtime(outFileName), translator.getMTime())
        newmtimes[name] = newmtime
    comsout.send('incProgress', 'patching')
    if dbgid:
        return ret, dbgid
    else:
        return ret
