'''
Created on 6 Oct 2013

@author: habisain
'''

if __name__ == '__main__':
    import sys
    sys.path.append('..')

from coreprotocol import CoreProtocol
from ui import MainWindow, Timer
from PySide import QtGui, QtCore

class QTLogic(CoreProtocol):
    def __init__(self, *args, **kwargs):
        super(QTLogic, self).__init__(*args, **kwargs)
        self.app = QtGui.QApplication([])
        self.window = MainWindow(self.inputcoms)
        self.timer = Timer(100, self.update)
        self.browsePatchDirs = False
        
    def start(self):
        self.app.exec_()
        
    def stop(self):
        self.outputcoms.send('stop')
        
    def quit(self):
        self.app.exit()
        self.outputcoms.send('shutdown')
        
    def setUI(self, states):
        for element, state in states.items():
            self.window.enableElement(element, state)
    
    def browseGame(self):
        newgameloc = self.window.fileDialog('Choose game', 'RPGMaker Game Files (RPG_RT.EXE)')
        self.outputcoms.send('addGameFromPath', newgameloc, select=True)
        
    def browsePatch(self):
        newpatchloc = self.window.fileDialog('Choose patch', 'RPGMaker Trans Patches (*.zip RPGMKTRANSPATCH')
        self.outputcoms.send('addPatchFromPath', newpatchloc, select=True)
        
    def browsePatchDir(self):
        newpatchloc = self.window.dirDialog('Choose patch directory')
        self.outputcoms.send('addPatchFromPath', newpatchloc, select=True)
        
    def browseTrans(self):
        newtransloc = self.window.dirDialog('Choose translation directory')
        self.outputcoms.send('addTransFromPath', newtransloc, select=True)
        
    def changeSelected(self, *args, **kwargs):
        self.outputcoms.send('changeSelected', *args, **kwargs)
        
    def setBrowsePatchDirs(self, state):
        self.browsePatchDirs = state
        
    def optionChanged(self, *args, **kwargs):
        self.outputcoms.send('optionChanged', *args, **kwargs)
        
    def addGame(self, tokenName, tokenID, select=False):
        self.window.comboBoxAdd('gameloc', tokenName, tokenID, select)
        
    def addPatch(self, tokenName, tokenID, select=False):
        self.window.comboBoxAdd('patchloc', tokenName, tokenID, select)
        
    def addTrans(self, tokenName, tokenID, select=False):
        self.window.comboBoxAdd('transloc', tokenName, tokenID, select)
        
    def selectGame(self, tokenID):
        self.window.comboBoxSelect('gameloc', tokenID)
        
    def selectPatch(self, tokenID):
        self.window.comboBoxSelect('patchloc', tokenID)
        
    def selectTrans(self, tokenID):
        self.window.comboBoxSelect('transloc', tokenID)
        
    def setProgress(self, amount):
        self.window.setProgress(int(amount * 100))
        
    def setMessage(self, message):
        self.window.setMessage(message)
        
    def displayOK(self, title, message):
        self.window.displayMessage('OK', title, message)
        
    def displayOKKill(self, title, message):
        self.window.displayMessage('OK', title, message)
        self.stop()
        
    def displayError(self, title, message):
        self.window.displayMessage('ErrorClass', title, message)
        
    def yesNoBox(self, title, message, yes=None, no=None):
        result = self.window.yesNoBox(title, message)
        if result and yes is not None:
            self.outputcoms.send(yes)
        elif not result and no is not None:
            self.outputcoms.send(no)

    def button(self, button):
        if button == 'gameloc':
            self.browseGame()
        elif button == 'transloc':
            self.browseTrans()
        elif button == 'patchloc':
            if self.browsePatchDirs:
                self.browsePatchDir()
            else:
                self.browsePatch()
        elif button == 'go':
            self.window.gobutton.setEnabled(False)
            self.outputcoms.send('go')
        else:
            print 'Unknown button press %s' % str(button)

def startView(*args, **kwargs):
    x = QTLogic(*args, **kwargs)
    x.start()
    
if __name__ == '__main__':
    startView()