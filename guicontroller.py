'''
Created on 7 Oct 2013

@author: habisain
'''
import os

from coreprotocol import CoreRunner, CoreProtocol
from sniffers import sniffAll, sniff
from headless import Headless
from qtui import startView

class IDStore(dict):
    def __init__(self, reverse=True, *args, **kwargs):
        super(IDStore, self).__init__(*args, **kwargs)
        self.nextid = 0
        self.reversable = reverse
        if self.reversable:
            self.reverse = {}
        
    def __setitem__(self, key, val):
        if self.reversable:
            self.reverse[val] = key
        super(IDStore, self).__setitem__(key, val)
        
    def add(self, item):
        r = self.nextid
        self[item] = r
        self.nextid += 1
        return r

class GUIController(CoreProtocol):
    def __init__(self, runner, *args, **kwargs):
        super(GUIController, self).__init__(*args, **kwargs)
        self.submit('gui', startView, inputcoms=self.outputcoms, outputcoms=self.inputcoms)
        runner.attach(self)
        self.gameDB = IDStore()
        self.patchDB = IDStore()
        self.transDB = IDStore()
        self.headless = None
        self.outputcoms.send('setMessage', 'Loading games, patches...')
        self.outputcoms.send('setUI', False)
        sniffDataRet = self.submit('worker', sniffAllTrigger, path=os.getcwd(), coms=self.inputcoms)
        self.localWaitUntil('sniffingDone', self.setUpSniffedData, sniffDataRet)
        self.runner = runner
        
    def setUpSniffedData(self, sniffDataRet):
        sniffData = sniffDataRet.get()
        for item, path in sniffData:
            if item is False:
                pass
            elif item.maintype == 'GAME':
                self.addGame(path, item)
            elif item.maintype == 'PATCH':
                self.addPatch(path, item)
            elif item.maintype == 'TRANS':
                self.addTrans(path, item)
        self.outputcoms.send('setUI', True)
                
    def addItem(self, path, sniffData, sniffDataType, idstore, sendSignal, select, prefix=None):
        if sniffData is None: sniffData = sniff(path)
        if sniffData is False: return False
        if sniffData.maintype != sniffDataType:
            raise Exception('Bad data item of type %s, expected %s' % (sniffData.maintype, sniffDataType))
        name = os.path.split(path)[1]
        if prefix is not None:
            prefix = prefix % sniffData.subtype
            name = '%s %s' % (prefix, name)
        if path not in idstore:
            tid = idstore.add(path)
        else:
            tid = idstore[path]
        self.outputcoms.send(sendSignal, name, tid, select=select)
    
    def addGame(self, gamepath, sniffData=None, select=False):
        self.addItem(gamepath, sniffData, 'GAME', self.gameDB, 'addGame', select, prefix='[%s]')
        
    def addPatch(self, patchpath, sniffData=None, select=False):
        self.addItem(patchpath, sniffData, 'PATCH', self.patchDB, 'addPatch', select)
        
    def addTrans(self, transpath, sniffData=None, select=False):
        self.addItem(transpath, sniffData, 'TRANS', self.transDB, 'addTrans', select)
        
    def go(self, gameid, patchid, transid):
        gamepath = self.gameDB.reverse[gameid]
        patchpath = self.patchDB.reverse[patchid]
        transpath = self.transDB.reverse[transid]
        headless = Headless(outputcoms=self.inputcoms)
        self.runner.attach(headless)
        headless.go(gamepath, patchpath, transpath)
        print 'translating'
        print 'game: %s' % gamepath
        print 'patch: %s' % patchpath
        print 'trans: %s' % transpath
        
    def setProgress(self, amount):
        self.outputcoms.send('setProgress', amount)
        
    def stop(self):
        if self.headless is None or not self.headless.going:
            self.outputcoms.send('quit')
        else:
            self.outputcoms.send('yesNoBox', 
                                 'Patching in progress', 
                                 'Patching is still in progress.\n'
                                 'Really quit?', yes='reallyStop')
            
    def reallyStop(self):
        self.outputcoms.send('quit')
        
    def shutdown(self):
        self.terminate()
        self.going = False
        
def sniffAllTrigger(path, coms):
    ret = sniffAll(path)
    coms.send('trigger', 'sniffingDone')
    return ret

if __name__ == '__main__':
    z = CoreRunner()
    x = GUIController(runner=z)
    z.run()
    