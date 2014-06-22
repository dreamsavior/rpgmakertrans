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
from .fileops import WinOpen


class MTimesHandlerManager(CustomManager):
    pass


class MetaMTimesManager(MetaCustomManager):
    customManagerClass = MTimesHandlerManager


class MTimesHandler(object, metaclass=MetaMTimesManager):

    def __init__(self, outpath):
        self.mtimespath = os.path.join(outpath, 'mtimes')
        self.manager = multiprocessing.Manager()
        self.mtimes = self.manager.dict()
        self.newmtimes = self.manager.dict()

    def loadMTimes(self):
        try:
            with WinOpen(self.mtimespath) as f:
                loadedmtimes = pickle.load(f)
        except:
            loadedmtimes = {}
        self.mtimes.update(loadedmtimes)

    def dumpMTimes(self):
        dumpmtimes = {}
        dumpmtimes.update(self.newmtimes)
        with WinOpen(self.mtimespath, 'wb') as f:
            pickle.dump(dumpmtimes, f)

    def getMTimes(self):
        return self.mtimes

    def getNewMTimes(self):
        return self.newmtimes


@errorWrap
def loadMTimes(mtimeshandler, comsout):
    mtimeshandler.loadMTimes()
    comsout.send('trigger', 'mtimesReady')


@errorWrap
def dumpMTimes(mtimeshandler, comsout):
    mtimeshandler.dumpMTimes()
    comsout.send('trigger', 'mtimesDumped')
