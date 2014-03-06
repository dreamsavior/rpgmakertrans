'''
Created on 7 Oct 2013

@author: habisain
'''
import os

from ..controllers.coreprotocol import CoreRunner, CoreProtocol
from ..workers.sniffers import sniffAll, sniff
from ..controllers.headless import Headless
from .qtui import startView, errorMsg
from ..version import versionCheck

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
        self.setupPool('gui', processes=1)
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
        self.setupPool('worker', processes=1)
        sniffDataRet = self.submit('worker', sniffAllTrigger, path=os.getcwd(), coms=self.inputcoms)
        self.submit('worker', versionCheck, coms=self.inputcoms)
        self.localWaitUntil('sniffingDone', self.setUpSniffedData, sniffDataRet)
        
    def newVerAvailable(self, version):
        self.outputcoms.send('displayOKKill', 'New Version Available', 'Version %s of RPGMaker Trans is available.\nPlease visit http://habisain.blogspot.co.uk to download it.\nPress OK to close RPGMaker Trans' % str(round(version, 2)))
        
    def setUpSniffedData(self, sniffDataRet):
        sniffData = sniffDataRet.get()
        for item in sniffData:
            if item is False:
                pass
            elif item.maintype == 'GAME':
                self.addGame(item, select=False)
            elif item.maintype == 'PATCH':
                self.addPatch(item, select=False)
            elif item.maintype == 'TRANS':
                self.addTrans(item, select=False)
        self.outputcoms.send('setMessage', 'Ready')
                
    def addItem(self, sniffData, sniffDataTypes, idstore, signalSuffix, select, prefix=None):
        # Take care of stuff where we can't do anything...
        #if sniffData is None: 
        #    sniffData = sniff(path, positives=sniffDataTypes)
        #    for item in sniffData:
        #        self.addItem(path, item, sniffDataTypes, idstore, sendSignal, select, prefix)
        #    return
        #if sniffData is False: return 
        if sniffData.maintype not in sniffDataTypes: return 
        path = sniffData.canonicalpath
        name = os.path.split(path)[1]
        if prefix is not None:
            prefix = prefix % sniffData.subtype
            name = '%s %s' % (prefix, name)
        if path not in idstore:
            tid = idstore.add(path)
            self.outputcoms.send('add%s' % signalSuffix, name, tid, select=select)
        else:
            tid = idstore[path]
            if select:
                self.outputcoms.send('select%s' % signalSuffix, tid) 
    
    def addItemFromPath(self, path, sniffDataTypes, idStore, signalSuffix, select=False, prefix=None):
        sniffData = sniff(path)#, positives=sniffDataTypes)
        for item in sniffData: 
            self.addItem(item, sniffDataTypes, idStore, signalSuffix, select, prefix)
    
    def addGame(self, sniffData, select=False):
        self.addItem(sniffData, ['GAME', 'TRANS'], self.gameDB, 'Game', select, prefix='[%s]')
                
    def addGameFromPath(self, gamepath, select=False):
        self.addItemFromPath(gamepath, ['GAME', 'TRANS'], self.gameDB, 'Game', select, prefix='[%s]')
        
    def addPatch(self, sniffData, select=False):
        self.addItem(sniffData, ['PATCH'], self.patchDB, 'Patch', select, prefix='[%s]')
    
    def addPatchFromPath(self, patchpath, select=False):
        self.addItemFromPath(patchpath, ['PATCH'], self.patchDB, 'Patch', select, prefix='[%s]')
            
    def addTrans(self, sniffData, select=False):
        self.addItem(sniffData, ['TRANS'], self.transDB, 'Trans', select, prefix='[%s]')
    
    def addTransFromPath(self, transpath, select=False):
        self.addItemFromPath(transpath, ['TRANS'], self.transDB, 'Trans', select, prefix='[%s]')
        
    def selectDefaultPatch(self):
        if self.currentState['gameloc'] is None: return
        gamepath = self.gameDB.reverse[self.currentState['gameloc']]
        defaultpatchpath = gamepath + '_patch'
        sniffData = sniff(defaultpatchpath, positives=['PATCH'])
        if self.currentState['create'] is False:
            sniffData = [x for x in sniffData if x.subtype != 'create']
        if len(sniffData) > 0:
            for item in sniffData:
                self.addPatch(item, select=True)
        else:
            defaultzippath = defaultpatchpath + '.zip'
            zipSniff = [x for x in sniff(defaultzippath, positives=['PATCH']) if x.subtype != 'create']
            for item in zipSniff:
                self.addPatch(item, select=True)
        
        
    def changeSelected(self, idtoken, newid):
        self.currentState[idtoken] = newid
        if idtoken == 'gameloc':
            self.selectDefaultPatch()
        elif idtoken == 'patchloc':
            if self.currentState['gameloc'] is not None:
                gamepath = self.gameDB.reverse[self.currentState['gameloc']]
                defaulttranspath = gamepath + '_translated'
                self.addTransFromPath(defaulttranspath, select=True)
        
    def optionChanged(self, option, value):
        self.currentState[option] = value
        if option == 'create':
            self.selectDefaultPatch()
            self.outputcoms.send('setBrowsePatchDirs', value)
        
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
        
    def go(self):
        self.outputcoms.send('resetNonfatalError')
        gamepath = self.gameDB.reverse[self.currentState['gameloc']]
        patchpath = self.patchDB.reverse[self.currentState['patchloc']]
        transpath = self.transDB.reverse[self.currentState['transloc']]
        headless = self.runner.initialise(Headless, outputcoms=self.inputcoms)
        headless.go(gamepath, patchpath, transpath)
        self.currentState['enabled'] = False
        self.outputcoms.send('setMessage', 'Patching game...')
        
    def nonfatalError(self, msg):
        self.outputcoms.send('nonfatalError', msg)
    
    def finalisingPatch(self):
        self.outputcoms.send('setMessage', 'Finalising Patch')
        
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
    