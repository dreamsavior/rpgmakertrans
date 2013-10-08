'''
Created on 7 Oct 2013

@author: habisain
'''

from coreprotocol import CoreRunner, CoreProtocol
from sniffers import sniffAll

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
        sniffData = self.submit('patcher', sniffAllTrigger, os.getcwd())
        self.localWaitUntil('sniffingDone', setUpSniffedData, sniffData)
        
    def setUpSniffedData(self, sniffData):
        print sniffData
        
    def addGame(self, gamepath):
        pass
        
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
    