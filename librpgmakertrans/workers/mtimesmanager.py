"""
mtimesmanager
*************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

A multiprocess capable handler for the mtimes file, which is used
to try and not redo everything with every single patch.
"""

from ..errorhook import errorWrap
import os.path
import pickle
from ..metamanager import CustomManager, MetaCustomManager
import multiprocessing


class MTimesHandlerManager(CustomManager):
    """Manager for MTimesHandler"""

class MetaMTimesManager(MetaCustomManager):
    """Metaclass for automatic registering of MTimesHandler"""
    customManagerClass = MTimesHandlerManager

class MTimesHandler(object, metaclass=MetaMTimesManager):
    """Provides a nice clean way to track the modification times of
    files being patched. There is a distinction between the current
    mtimes and the ovserved (new) mtimes, which means that should there
    be a high turnover of files, old mtimes won't clutter up the mtimes
    database."""
    def __init__(self, outpath):
        """Initialise an mtimes manager for target directory outpath"""
        self.mtimespath = os.path.join(outpath, 'mtimes')
        self.manager = multiprocessing.Manager()
        self.mtimes = self.manager.dict()
        self.newmtimes = self.manager.dict()

    def loadMTimes(self):
        """Try to load mtimes. If fail, assume no mtimes available"""
        try:
            with open(self.mtimespath, 'rb') as f:
                loadedmtimes = pickle.load(f)
        except:
            loadedmtimes = {}
        self.mtimes.update(loadedmtimes)

    def dumpMTimes(self, translatorMTime):
        """Dump *new* mtimes to output file"""
        localCopy = {}
        localCopy.update(self.newmtimes)
        dumpmtimes = {}
        for key in localCopy:
            dumpmtimes[key] = (self.newmtimes[key], translatorMTime)
        with open(self.mtimespath, 'wb') as f:
            pickle.dump(dumpmtimes, f)

    def getMTimes(self):
        """Return multiprocess capable mtimes dictionary"""
        return self.mtimes

    def getNewMTimes(self):
        """Return multiprocess capable newmtimes dictionary"""
        return self.newmtimes


@errorWrap
def loadMTimes(mtimeshandler, comsout):
    mtimeshandler.loadMTimes()
    comsout.send('trigger', 'mtimesReady')


@errorWrap
def dumpMTimes(mtimeshandler, translatorMTime, comsout):
    mtimeshandler.dumpMTimes(translatorMTime)
    comsout.send('trigger', 'mtimesDumped')
