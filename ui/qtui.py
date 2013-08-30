'''
Created on 3 Feb 2013

@author: habisain
'''

import sys
from PySide import QtGui, QtCore
from errorhook import errorWrap, ErrorClass, ErrorMeta
from sender import Sender

labelString = ''.join([
    "RPGMaker Trans (C) Habisain 2011-2012\n",
    "You may not redistribute games patched by ",
    "RPGMaker Trans without fulfilling a number ",
    "of criteria that 3rd party or fan translations ",
    "are unlikely to meet. "])

class SelectorBlock(ErrorClass, QtGui.QGroupBox):
    def __init__(self, name, idtoken, qtparent, eventComms):
        super(SelectorBlock, self).__init__(name, qtparent)
        self.eventComms = eventComms
        self.name = name
        self.idtoken = idtoken
        self.idmap = {}
        self.ridmap = {}
        hbox = QtGui.QHBoxLayout()
        self.combobox = QtGui.QComboBox()
        self.combobox.setMinimumWidth(300)
        hbox.addWidget(self.combobox)
        self.browseButton = QtGui.QPushButton("Browse...")
        hint = self.browseButton.sizeHint()
        width = hint.width()
        self.browseButton.setMinimumWidth(width)
        self.browseButton.setMaximumWidth(width)
        hbox.addWidget(self.browseButton)
        self.setLayout(hbox)
        hint = self.sizeHint()
        height = hint.height()
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)
        self.browseButton.released.connect(self.browsePressed)
        
    def addItem(self, item, idtoken):
        self.combobox.addItem(item, idtoken)
        
    def enable(self, state):
        self.combobox.setEnabled(state)
        self.browseButton.setEnabled(state)
        
    def selectItem(self, idtoken):
        self.combobox.setCurrentIndex(self.combobox.findData(idtoken))
        
    def getCurrentSelectedID(self):
        return self.combobox.itemData(self.combobox.currentIndex())
        
    def browsePressed(self):
        self.eventComms.send('button', self.idtoken)
        
    
        
class PatchOptions(ErrorClass, QtGui.QGroupBox):
    def __init__(self, qtparent, eventComms):
        name = 'Patch Options'
        self.eventComms = eventComms
        super(PatchOptions, self).__init__(name, qtparent)
        hbox = QtGui.QHBoxLayout()
        self.create = QtGui.QCheckBox('Create patch', self)
        self.create.setToolTip('When first starting a translation project,\n'
                               'select this to create the initial patch')
        self.inplace = QtGui.QCheckBox('Patch in place', self)
        self.inplace.setToolTip('In-place patching is faster, but the\n'
                                'results can\'t be updated with either\n'
                                'new game data or a new translation\n'
                                'If you won\'t want to update the game\n'
                                'or the translation, select this.')
        for x in self.create, self.inplace:
            hbox.addWidget(x)
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox)
        self.setLayout(vbox)
        self.create.toggled.connect(lambda: self.toggle('create', self.create.isChecked()))
        self.inplace.toggled.connect(lambda: self.toggle('inplace', self.inplace.isChecked()))
        
    def toggle(self, signal, val):
        self.eventComms.send('newval', signal, val)
        
    def enable(self, state):
        for widget in self.create, self.inplace:
            widget.setEnabled(state)

class MainWindow(ErrorClass, QtGui.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        vbox = QtGui.QVBoxLayout()
        self.eventComms = Sender()
        self.game = SelectorBlock('Game location', 'gameloc', self, self.eventComms)
        self.patch = SelectorBlock('Patch location', 'patchloc', self, self.eventComms)
        self.trans = SelectorBlock('Translation Location', 'transloc', self, self.eventComms)
        self.patchopts = PatchOptions(self, self.eventComms)
        self.progress = QtGui.QProgressBar()
        self.progress.setMinimum(0)
        self.comms = QtGui.QLabel('Waiting for backend..')
        self.gobutton = QtGui.QPushButton('Go!')
        label = QtGui.QLabel(labelString)
        label.setWordWrap(True)
        for x in self.game, self.patch, self.trans, self.patchopts, self.progress, self.comms, self.gobutton, label:
            vbox.addWidget(x)
        self.setLayout(vbox)    
        self.setWindowTitle('RPGMaker Trans QTUI Experiment')
        self.gobutton.released.connect(lambda: self.eventComms.append(('button',('go',))))
        hint = self.sizeHint()
        height = hint.height()
        width = hint.width()
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)
        self.setMinimumWidth(width)
        self.setMaximumWidth(width)
        self.show()
        
    def closeEvent(self, event):
        self.eventComms.send('QUIT')
        event.ignore()
        
    def displayMessage(self, style, title, maintext):
        msgBox = QtGui.QMessageBox(self)
        msgBox.setWindowTitle(title)
        msgBox.setText(maintext)
        msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
        if style == 'ErrorClass':
            msgBox.setIcon(QtGui.QMessageBox.Critical)
        elif style == 'OK':
            msgBox.setIcon(QtGui.QMessageBox.Information)
        return msgBox.exec_()
    
    def getComboControl(self, controlID):
        control = None
        for x in self.game, self.trans, self.patch:
            if controlID == x.idtoken:
                control = x
                break
        if control:
            return control
        else:
            raise Exception( 'Unknown control ID')
    
    def comboBoxAdd(self, controlID, tokenName, tokenID, select=False):
        control = self.getComboControl(controlID)
        control.addItem(tokenName, tokenID)   
        if select:
            control.selectItem(tokenID) 
            
    def comboBoxSelect(self, controlID, tokenID):
        control = self.getComboControl(controlID)
        control.selectItem(tokenID)
            
    def getTransParams(self):
        return [x.getCurrentSelectedID() for x in [self.game, self.patch, self.trans]]
    
    def setProgress(self, percent):
        if percent == -1:
            self.progress.setMaximum(0)
        else:
            self.progress.setMaximum(100)
            self.progress.setValue(percent)
            
    def setMessage(self, message):
        self.comms.setText(message)
        
    def toggleUI(self, state):
        
        self.game.enable(state)
        self.patch.enable(state and self.game.getCurrentSelectedID() is not None)
        self.trans.enable(state and self.game.getCurrentSelectedID() is not None)
        self.patchopts.enable(state and self.game.getCurrentSelectedID() is not None)
        self.gobutton.setEnabled(state and self.patch.getCurrentSelectedID() is not None
                                 and self.trans.getCurrentSelectedID() is not None
                                 and self.game.getCurrentSelectedID() is not None)
        self.trans.enable(False)
            
    def fileDialog(self, title, wildcard):
        """Return a UTF string of the selected name"""
        return QtGui.QFileDialog.getOpenFileName(parent=self, caption=title, 
                                          filter=wildcard)[0]
        
    def dirDialog(self, title):
        """Return a UTF string of the selected directory"""
        return QtGui.QFileDialog.getExistingDirectory(parent=self, caption=title)

class Timer(object):
    __metaclass__ = ErrorMeta
    def __init__(self, period, connectTo):
        self.timer = QtCore.QTimer()
        self.timer.start(period)
        self.timer.timeout.connect(connectTo)
        
class WindowLogicQTComms(object):
    __metaclass__ = ErrorMeta
    def __init__(self):
        #super(WindowLogicQTComms, self).__init__()
        #self.comsin, self.comsout = [], []
        self.app = QtGui.QApplication(sys.argv)
        self.window = MainWindow()
        
    def start(self):
        self.app.exec_()
        
    def stop(self):
        self.app.exit()
        
    def __iter__(self):
        comms = self.window.eventComms.get()
        while comms:
            yield comms.pop()
        
    def __getattr__(self, key):
        if hasattr(self.window, key):
            setattr(self, key, getattr(self.window, key))
        return super(WindowLogicQTComms, self).__getattribute__(key)
        
class WindowLogic(object):
    __metaclass__ = ErrorMeta
    def __init__(self, wndComms, sendin, sendout):
        self.sendin, self.sendout = sendin, sendout
        self.wndComms = wndComms                
        self.timer = Timer(100, self.updateGUI)
        self.actions = {'addGame': lambda x,y,z: self.wndComms.comboBoxAdd('gameloc', x,y,z),
                        'addPatch': lambda x,y,z: self.wndComms.comboBoxAdd('patchloc', x,y,z),
                        'addTrans': lambda x,y,z: self.wndComms.comboBoxAdd('transloc', x,y,z),
                        'setProgress': lambda x: self.wndComms.setProgress(x),
                        'setMessage': lambda x: self.wndComms.setMessage(x),
                        'displayOK': lambda x, y: self.wndComms.displayMessage('OK', x, y),
                        'displayError': lambda x, y: self.wndComms.displayMessage('ErrorClass', x, y),
                        'displayOKKill': self.displayOKKill,
                        'selectGame': lambda x: self.wndComms.comboBoxSelect('gameloc', x),
                        'selectPatch': lambda x: self.wndComms.comboBoxSelect('patchloc', x),
                        'selectTrans': lambda x: self.wndComms.comboBoxSelect('transloc', x),
                        'toggleUI': lambda x: self.wndComms.toggleUI(x),
                        }
        self.uiactions = {'button': self.buttonPressed}
        self.wndComms.start()
        
    def start(self):
        self.wndComms.start()
        
    def updateGUI(self):
        events = self.sendin.get()
        while events:
            acttype, actargs, actkwargs = events.pop(0)
            if acttype in self.actions:
                self.actions[acttype](*actargs, **actkwargs)
            else:
                self.logger.warning('warning, unknown action %s with args %s %s' % (str(acttype), str(actargs), str(actkwargs)))
        for msg, args, kwargs in self.wndComms:
            if msg == 'QUIT':
                self.close()
            elif msg in self. uiactions:
                self.uiactions[msg](*args, **kwargs)
            else:
                print msg, args, kwargs
        #self.wndComms.setProgress(self.progressAmount)
    
    def buttonPressed(self, button):
        if button == 'go':
            gameid, patchid, transid = self.wndComms.getTransParams()
            self.sendout.send('doPatch', gameid, patchid, transid)
        elif button == 'gameloc':
            newgame = self.selectGame()
            if newgame:
                self.sendout.send('addGame', newgame)
        elif button == 'patchloc':
            newpatch = self.selectPatch()
            if newpatch:
                self.sendout.send('addPatch', newpatch)
        elif button == 'transloc':
            transdir = self.selectTransDir()
            if transdir:
                self.sendout.send('addTrans', newpatch) 
        else:
            print 'unknown button %s' % button

    # TODO: These wildcards are QT dependent. Make it not so.
    def selectGame(self):
        return self.wndComms.fileDialog('Choose game', 'RPGMaker Game Files (RPG_RT.EXE)')
    
    def selectPatch(self):
        return self.wndComms.fileDialog('Choose patch', 'RPGMaker Trans Patches (*.zip RPGMKTRANSPATCH')
    
    def selectTransDir(self):
        return self.wndComms.dirDialog('Choose translation directory')
    
    def close(self):
        self.wndComms.stop()
        self.sendout.send('KILL')
        
    def displayOK(self, title, message):
        self.wndComms.displayMessage('OK', title, message)
    
    def displayOKKill(self, title, message):
        self.wndComms.displayMessage('OK', title, message)
        self.close()
#        sys.exit(0)
        
    def displayError(self, title, message):
        self.wndComms.displayMessage('ErrorClass', title, message)

@errorWrap
def startView(comsin, comsout):
    control = WindowLogic(WindowLogicQTComms(), comsin, comsout)
    control.start()

    
def main():
    outcmds = []
    ex = WindowLogic(WindowLogicQTComms(),
                     [['addGame', ['TestGame', 0, False]],
                      ['addGame', ['TestGame2', 1, True]],
                      ['addPatch', ['TestPatch', 0, False]],
                      ['addTrans', ['TestTrans', 0, False]],
                      ['setProgress', [20]],
                      ['setMessage', ['Testing 1 2 3']],
                      #['displayOK', ['Nonsense', 'Ying tong iddle']],
                      ['selectGame', [0]],
                      ['toggleUI', [True]],
                     ],
                     outcmds,)
    ex.start()
    print outcmds
    #sys.exit(app.exec_())


if __name__ == '__main__':
    main()
