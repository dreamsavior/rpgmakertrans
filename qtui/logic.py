'''
Created on 6 Oct 2013

@author: habisain
'''
import sys
sys.path.append('..')
from coreprotocol import CoreRunner, CoreProtocol
from ui import MainWindow, Timer
from PySide import QtGui, QtCore

class QTLogic(CoreProtocol):
    def __init__(self, *args, **kwargs):
        super(QTLogic, self).__init__(*args, **kwargs)
        self.app = QtGui.QApplication([])
        self.window = MainWindow(self.coms)
        self.timer = Timer(100, self.update)
        
    def start(self):
        self.app.exec_()
        
    def stop(self):
        self.app.exit()
        
    def setUI(self, state):
        self.window.toggleUI(state)
    
    def browseGame(self):
        newgameloc = self.window.fileDialog('Choose game', 'RPGMaker Game Files (RPG_RT.EXE)')
        self.comsout.send('addGame', newgameloc)
        
    def browsePatch(self):
        newpatchloc = self.window.fileDialog('Choose patch', 'RPGMaker Trans Patches (*.zip RPGMKTRANSPATCH')
        self.comsout.send('addPatch', newpatchloc)
        
    def browseTrans(self):
        newtransloc = self.window.dirDialog('Choose translation directory')
        self.comsout.send('addTrans', newtransloc)
        
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

    def button(self, button):
        if button == 'gameloc':
            self.browseGame()
        elif button == 'transloc':
            self.browseTrans()
        elif button == 'patchloc':
            self.browsePatch()
        elif button == 'go':
            raise Exception('Go not implemented yet')
        else:
            print 'Unknown button press %s' % str(button)
    
if __name__ == '__main__':
    x = QTLogic()
    x.coms.send('setUI', True)
    x.start()
    sys.exit()