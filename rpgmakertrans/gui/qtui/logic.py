"""
logic
*****

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

An implementation of the logic for the UI.
"""


if __name__ == '__main__':
    import sys
    sys.path.append('..')

from PySide import QtGui

from librpgmakertrans.controllers.coreprotocol import CoreProtocol
from librpgmakertrans.errorhook import errorWrap

from .ui import MainWindow, Timer

class QTLogic(CoreProtocol):
    """Implements the logic for the GUI; these are the functions available
    to the GUI controller, should the GUI ever be changed again..."""
    def __init__(self, *args, **kwargs):
        """Initialise the QT Application and setup the Window"""
        super(QTLogic, self).__init__(*args, **kwargs)
        self.app = QtGui.QApplication([])
        self.window = MainWindow(self)
        self.app.setActiveWindow(self.window)
        self.timer = Timer(100, self.update)
        self.browsePatchDirs = False

    def start(self):
        """Start the application main loop"""
        self.app.exec_()

    def stop(self):
        """Override the stop behaviour to request a stop"""
        self.outputcoms.send('stop')

    def quit(self):
        """Immediately quit application"""
        #self.app.exit()
        self.outputcoms.send('terminate')

    def setUI(self, states):
        """Set the elements of the UI to be enabled or not. Valid
        elements are gameloc, transloc, patchloc, options and go."""
        for element, state in list(states.items()):
            self.window.enableElement(element, state)
    
    def setPatchBanner(self, banner):
        self.window.setPatchBanner(banner)
        
    def browseGame(self):
        """Display a browse window for a game"""
        newgameloc = self.window.fileDialog(
            'Choose game',
            'RPGMaker Game Files (RPG_RT.EXE Game.exe)')
        self.outputcoms.send('addGameFromPath', newgameloc, select=True)

    def browsePatch(self):
        """Display a browse window for a patch"""
        newpatchloc = self.window.fileDialog(
            'Choose patch',
            'RPGMaker Trans Patches (*.zip RPGMKTRANSPATCH')
        self.outputcoms.send('addPatchFromPath', newpatchloc, select=True)

    def browsePatchDir(self):
        """Display a browse window for a patch directory"""
        newpatchloc = self.window.dirDialog('Choose patch directory')
        self.outputcoms.send('addPatchFromPath', newpatchloc, select=True)

    def browseTrans(self):
        """Display a browse window for an output directory"""
        newtransloc = self.window.dirDialog('Choose translation directory')
        self.outputcoms.send('addTransFromPath', newtransloc, select=True)

    def changeSelected(self, *args, **kwargs):
        """Change the selected control"""
        self.outputcoms.send('changeSelected', *args, **kwargs)

    def setBrowsePatchDirs(self, state):
        """Set if a patch directory or patch file chooser should be used
        (directory chooser used for creating a patch, where no file exists)"""
        self.browsePatchDirs = state

    def optionChanged(self, *args, **kwargs):
        """Relay for an option changing"""
        self.outputcoms.send('optionChanged', *args, **kwargs)

    def addGame(self, tokenName, tokenID, select=False):
        """Add a game to the game selector box"""
        self.window.comboBoxAdd('gameloc', tokenName, tokenID, select)

    def addPatch(self, tokenName, tokenID, select=False):
        """Add a patch to the patch selector box"""
        self.window.comboBoxAdd('patchloc', tokenName, tokenID, select)

    def addTrans(self, tokenName, tokenID, select=False):
        """Add a target to the translator selector box"""
        self.window.comboBoxAdd('transloc', tokenName, tokenID, select)

    def nonfatalError(self, msg):
        """Display a non fatal error"""
        self.window.nonfatalError(msg)

    def resetNonfatalError(self):
        """Reset non fatal error message display"""
        self.window.resetNonfatalErrors()

    def selectGame(self, tokenID):
        """Select a game in game selector box"""
        self.window.comboBoxSelect('gameloc', tokenID)

    def selectPatch(self, tokenID):
        """Select a patch in patch selector box"""
        self.window.comboBoxSelect('patchloc', tokenID)

    def selectTrans(self, tokenID):
        """Select a target translation destination in
        translation selector box"""
        self.window.comboBoxSelect('transloc', tokenID)

    def removeGame(self, tokenID):
        """Remove a game from the selector box"""
        self.window.comboBoxRemove('gameloc', tokenID)

    def setProgress(self, amount):
        """Set progress to given amount (between 0 and 1)"""
        self.window.setProgress(int(amount * 100))

    def setMessage(self, message):
        """Set progress bar message"""
        self.window.setMessage(message)

    def set_adv_text(self, message):
        self.window.set_adv_message(message)

    def displayOK(self, title, message):
        """Display an OK dialogue box"""
        self.window.displayMessage('OK', title, message)

    def displayOKKill(self, title, message):
        """Display an OK dialogue box, then gracefully shut down"""
        self.window.displayMessage('OK', title, message)
        self.stop()

    def displayError(self, title, message):
        """Display an error dialogue box"""
        self.window.displayMessage('ErrorClass', title, message)

    def yesNoBox(self, title, message, yes=None, no=None):
        """Display a yes/no box, get result, and depending
        on outcome send a message on outputcoms"""
        result = self.window.yesNoBox(title, message)
        if result and yes is not None:
            self.outputcoms.send(yes)
        elif not result and no is not None:
            self.outputcoms.send(no)

    def button(self, button):
        """Perform action when a button is pressed"""
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
            print('Unknown button press %s' % str(button))

@errorWrap
def startView(*args, **kwargs):
    """Start the QTUI main loop"""
    x = QTLogic(*args, **kwargs)
    x.start()

if __name__ == '__main__':
    startView()
