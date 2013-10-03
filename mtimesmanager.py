'''
Created on 3 Oct 2013

@author: habisain
'''
from errorhook import errorWrap, ErrorMeta
import os.path
import cPickle
from metamanager import makeMetaManager
import multiprocessing

MTimesHandlerManager, MetaMTimesManager = makeMetaManager('MTimesHandlerManager', ErrorMeta)

class MTimesHandler(object):
    __metaclass__ = MetaMTimesManager
    
    def __init__(self, outpath):
        self.mtimespath = os.path.join(outpath, 'mtimes')
        self.manager = multiprocessing.Manager()
        self.mtimes = self.manager.dict()
        self.newmtimes = self.manager.dict()
    
    def loadMTimes(self):
        try:
            with open(self.mtimespath) as f:
                loadedmtimes = cPickle.load(f)
        except:
            loadedmtimes = {}
        self.mtimes.update(loadedmtimes)
        
    def dumpMTimes(self):
        dumpmtimes = {}
        dumpmtimes.update(self.newmtimes)
        with open(self.mtimespath, 'w') as f:
            cPickle.dump(dumpmtimes, f)
            
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
    

        
