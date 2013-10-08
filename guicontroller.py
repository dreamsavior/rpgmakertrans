'''
Created on 7 Oct 2013

@author: habisain
'''
import os

from coreprotocol import CoreRunner, CoreProtocol
from sniffers import sniffAll
import patchers
from qtui import startView

class GUIController(CoreProtocol):
    def __init__(self, runner, *args, **kwargs):
        super(GUIController, self).__init__(*args, **kwargs)
        self.submit('gui', startView, inputcoms=self.outputcoms, outputcoms=self.inputcoms)
        runner.attach(self)
        self.gameDB = {}
        self.patchDB = {}
        self.transDB = {}
        self.headless = None
        self.outputcoms.send('setMessage', 'Loading games, patches...')
        self.outputcoms.send('setUI', False)
        sniffDataRet = self.submit('worker', sniffAllTrigger, path=os.getcwd(), coms=self.inputcoms)
        self.localWaitUntil('sniffingDone', self.setUpSniffedData, sniffDataRet)
        
    def setUpSniffedData(self, sniffDataRet):
        sniffData = sniffDataRet.get()
        for item, path in sniffData:
            if item.maintype == 'GAME':
                self.addGame(path, item)
            elif item.maintype == 'PATCH':
                self.addPatch(path, item)
            elif item.maintype == 'TRANS':
                self.addTrans(path, item)
    
    def addGame(self, gamepath, sniffData=None):
        print 'adding game %s' % gamepath
        
    def addPatch(self, patchpath, sniffData=None):
        print 'adding patch %s' % patchpath
        
    def addTrans(self, transpath, sniffData=None):
        print 'adding trans %s' % transpath
        
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
    