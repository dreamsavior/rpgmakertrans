'''
Created on 7 Oct 2013

@author: habisain
'''
import os

from coreprotocol import CoreRunner, CoreProtocol
from sniffers import sniffAll, sniff
from headless import Headless
from qtui import startView, errorMsg

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

class UpdaterDict(dict):
    def __init__(self, updateFunc, *args, **kwargs):
        self.__updateFunc = updateFunc
        super(UpdaterDict, self).__init__(*args, **kwargs)
        
    def __setitem__(self, key, value):
        super(UpdaterDict, self).__setitem__(key, value)
        self.__updateFunc()

class GUIController(CoreProtocol):
    def __init__(self, *args, **kwargs):
        super(GUIController, self).__init__(*args, **kwargs)
        self.submit('gui', startView, inputcoms=self.outputcoms, outputcoms=self.inputcoms)
        self.runner.setErrorHandler(errorMsg)
        self.gameDB = IDStore()
        self.patchDB = IDStore()
        self.transDB = IDStore()
        self.currentState = UpdaterDict(self.enableUI)
        self.currentState.update({'gameloc': None, 'patchloc': None, 'transloc': None, 
                                  'create': False, 'enabled': True})

        self.headless = None
        self.outputcoms.send('setMessage', 'Loading games, patches...')
        sniffDataRet = self.submit('worker', sniffAllTrigger, path=os.getcwd(), coms=self.inputcoms)
        self.localWaitUntil('sniffingDone', self.setUpSniffedData, sniffDataRet)
        
        
    def setUpSniffedData(self, sniffDataRet):
        sniffData = sniffDataRet.get()
        for item in sniffData:
            if item is False:
                pass
            elif item.maintype == 'GAME':
                self.addGame(item.canonicalpath, item, select=False)
            elif item.maintype == 'PATCH':
                self.addPatch(item.canonicalpath, item, select=False)
            elif item.maintype == 'TRANS':
                self.addTrans(item.canonicalpath, item, select=False)
                
    def addItem(self, path, sniffData, sniffDataTypes, idstore, sendSignal, select, prefix=None):
        # Take care of stuff where we can't do anything...
        if sniffData is None: 
            sniffData = sniff(path, positives=sniffDataTypes)
            for item in sniffData:
                self.addItem(path, item, sniffDataTypes, idstore, sendSignal, select, prefix)
            return
        if sniffData is False: return 
        if sniffData.maintype not in sniffDataTypes: return 
        
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
        self.addItem(gamepath, sniffData, ['GAME', 'TRANS'], self.gameDB, 'addGame', select, prefix='[%s]')
        
    def addPatch(self, patchpath, sniffData=None, select=False):
        self.addItem(patchpath, sniffData, ['PATCH'], self.patchDB, 'addPatch', select, prefix='[%s]')
        
    def addTrans(self, transpath, sniffData=None, select=False):
        self.addItem(transpath, sniffData, ['TRANS'], self.transDB, 'addTrans', select, prefix='[%s]')
        
    def changeSelected(self, idtoken, newid):
        self.currentState[idtoken] = newid
        #self.enableUI()
        
    def optionChanged(self, option, value):
        self.currentState[option] = value
        if option == 'create':
            print 'create option detected'
        #self.enableUI()
        
    def enableUI(self):
        state = self.currentState['enabled']
        states = {}
        states['gameloc'] = state
        state &= self.currentState['gameloc'] is not None
        states['patchloc'] = state
        states['options'] = state
        state &= self.currentState['patchloc'] is not None
        states['transloc'] = state
        state &= self.currentState['transloc'] is not None
        states['go'] = state
        self.outputcoms.send('setUI', states)
        
    def go(self, gameid, patchid, transid):
        gamepath = self.gameDB.reverse[gameid]
        patchpath = self.patchDB.reverse[patchid]
        transpath = self.transDB.reverse[transid]
        headless = self.runner.initialise(Headless, outputcoms=self.inputcoms)
        headless.go(gamepath, patchpath, transpath)
        self.currentState['enabled'] = False
        self.outputcoms.send('setMessage', 'Patching game...')
        
    def finishedPatching(self):
        self.currentState['enabled'] = True
        self.currentState['gameloc'] = None
        self.outputcoms.send('setMessage', 'Finished patching')
        #self.enableUI()
        
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
    x = z.initialise(GUIController)
    z.run()
    