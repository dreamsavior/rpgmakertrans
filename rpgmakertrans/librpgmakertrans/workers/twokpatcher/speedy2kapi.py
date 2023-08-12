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
from ...errorhook import errorWrap

@errorWrap
def process2kgame(inpath, outpath, translator, mtimes, newmtimes, comsout):
    """Generate the required jobs needed for patching a 2k game."""
    jobs = []
    for fn in os.listdir(inpath):
        if os.path.splitext(fn)[1].lower() in ('.lmu', '.ldb'):
            infn = os.path.join(inpath, fn)
            outfn = os.path.join(outpath, fn)
            jobs.append((process2kfile, (infn, outfn, mtimes, newmtimes,
                        translator, comsout)))
    jobsTotal = len(jobs)
    comsout.send('setProgressDiv', 'patching', jobsTotal)
    for fn, args in jobs:
        comsout.send('waitUntil', 'dirsCopied', 'patcher', fn, *args)

@errorWrap
def process2kfile(inFileName, outFileName, mtimes, newmtimes,
                  translator, comsout):
    """Process an individual 2k file"""
    name = os.path.split(inFileName)[1].rpartition('.')[0].upper()
    ret = (os.path.getmtime(inFileName), translator.getMTime())
    needOutput = ((mtimes.get(name,None) != ret) or
                  not os.path.exists(outFileName))
    if needOutput:
        rpgfile = TwoKRPGFile(name, inFileName, translator)
        rpgfile.parse()
        rpgfile.outputfile(outFileName)
    newmtime = os.path.getmtime(inFileName)
    newmtimes[name] = newmtime
    comsout.send('incProgress', 'patching')
    return ret
