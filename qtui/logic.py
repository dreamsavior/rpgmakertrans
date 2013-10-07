'''
Created on 6 Oct 2013

@author: habisain
'''

from coreprotocol import CoreProtocol
from ui import MainWindow, Timer
from PySide import QtGui, QtCore

class QTLogic(CoreProtocol):
    def __init__(self, *args, **kwargs):
        super(QTLogic, self).__init__(*args, **kwargs)
        self.app = QtGui.QApplication([])
        self.window = MainWindow(self.inputcoms)
        self.timer = Timer(100, self.update)
        
    def start(self):
        self.app.exec_()
        
    def stop(self):
        self.outputcoms.send('stop')
        
    def quit(self):
        self.app.exit()
        self.outputcoms.send('shutdown')
        
    def setUI(self, state):
        self.window.toggleUI(state)
    
    def browseGame(self):
        newgameloc = self.window.fileDialog('Choose game', 'RPGMaker Game Files (RPG_RT.EXE)')
        self.outputcoms.send('addGame', newgameloc)
        
    def browsePatch(self):
        newpatchloc = self.window.fileDialog('Choose patch', 'RPGMaker Trans Patches (*.zip RPGMKTRANSPATCH')
        self.outputcoms.send('addPatch', newpatchloc)
        
    def browseTrans(self):
        newtransloc = self.window.dirDialog('Choose translation directory')
        self.outputcoms.send('addTrans', newtransloc)
        
    def addGame(self, tokenName, tokenID, select=False):
        self.window.comboBoxAdd('gameloc', tokenName, tokenID, select)
        
    def addPatch(self, tokenName, tokenID, select=False):
        self.window.comboBoxAdd('patchloc', tokenName, tokenID, select)
        
    def addTrans(self, tokenName, tokenID, select=False):
        self.window.comboBoxAdd('transloc', tokenName, tokenID, select)
        
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
            self.browsePatch()
        elif button == 'go':
            self.outputcoms.send('go', **self.window.getTransParams())
        else:
            print 'Unknown button press %s' % str(button)

def startView(*args, **kwargs):
    x = QTLogic(*args, **kwargs)
    x.start()