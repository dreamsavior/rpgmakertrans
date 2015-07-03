"""
qtui
****

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

The implementation of the QT user interface.
"""

import os, itertools
from PySide import QtGui, QtCore, QtSvg
from librpgmakertrans.version import versionString

from .logointernal import LOGOINTERNAL

labelString = ''.join([
    "RPGMaker Trans (C) Habisain 2011-2015\n",
    "Redistributing a game patched by RPGMaker Trans will likely\n", 
    "breach copyright on that game, and so you should not do so\n"
    "without the original authors permission, even for free games."])


class SelectorBlock(QtGui.QGroupBox):
    """A Selector Block in the UI, comprising a combobox, browse button,
    and box"""
    def __init__(self, name, idtoken, qtparent, logic):
        """Setup the selector block"""
        super(SelectorBlock, self).__init__(name, qtparent)
        self.logic = logic
        self.name = name
        self.idtoken = idtoken
        self.idmap = {}
        self.ridmap = {}
        hbox = QtGui.QHBoxLayout()
        self.combobox = QtGui.QComboBox()
        self.combobox.setMinimumWidth(300)
        # self.combobox.setEditable(True)
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
        self.combobox.currentIndexChanged.connect(self.changedIndex)

    def addItem(self, item, idtoken):
        """Add an item to the combobox"""
        self.combobox.addItem(item, idtoken)

    def changedIndex(self, index):
        """Trigger for when the combo box is changed"""
        self.logic.changeSelected(self.idtoken,
                                  self.getCurrentSelectedID())

    def enable(self, state):
        """Set if the block is enabled or not"""
        self.combobox.setEnabled(state)
        self.browseButton.setEnabled(state)

    def selectItem(self, idtoken):
        """Select an item in the combo box"""
        self.combobox.setCurrentIndex(self.combobox.findData(idtoken))

    def removeItem(self, idtoken):
        """Remove an item from the combobox"""
        self.combobox.removeItem(self.combobox.findData(idtoken))

    def getCurrentSelectedID(self):
        """Get the ID of the current selected item"""
        return self.combobox.itemData(self.combobox.currentIndex())

    def browsePressed(self):
        """Trigger for when the browse button is pressed"""
        self.logic.button(self.idtoken)


class PatchOptions(QtGui.QGroupBox):
    """The block containing patch options"""
    def __init__(self, qtparent, logic):
        name = 'Patch Options'
        self.logic = logic
        super(PatchOptions, self).__init__(name, qtparent)
        self.create = QtGui.QCheckBox('Create patch', self)
        self.create.setToolTip('When first starting a translation project,\n'
                               'select this to create the initial patch')
        self.useBOM = QtGui.QCheckBox('Use UTF-8 BOM', self)
        self.useBOM.setToolTip(
            'Some editors will only recognise UTF-8 files\n'
            'with a BOM, although this will break other editors.\n'
            'Enabling this option will cause RPGMaker Trans files\n'
            'to have a UTF-8 BOM.')
        self.rebuild = QtGui.QCheckBox('Rebuild Patch', self)
        self.rebuild.setToolTip(
            'For v3 patches, positions of items in the patch\n'
            'are persistant. Check this box to rebuild the patch,\n'
            'which will rebuild the patch, restoring items to\n'
            'where RPGMaker Trans things they should be.\n'
            'Unused and untranslated items are removed and\n'
            'unused translations are placed in a special file. This\n'
            'is particularly useful if a patch becomes damaged,\n' 
            'a game undergoes major changes, or a patch is\n'
            'upgraded or has new types of translation added.')
        self.widgets = [[self.create, self.useBOM], [self.rebuild]]
        vbox = QtGui.QVBoxLayout()
        for row in self.widgets:
            hbox = QtGui.QHBoxLayout()
            for widget in row:
                hbox.addWidget(widget)
            vbox.addLayout(hbox)
            
        self.setLayout(vbox)
        self.create.toggled.connect(lambda: self.toggle('create',
                                    self.create.isChecked()))
        self.useBOM.toggled.connect(lambda: self.toggle('bom',
                                    self.useBOM.isChecked()))
        self.rebuild.toggled.connect(lambda: self.toggle('rebuild',
                                    self.useBOM.isChecked()))

    def toggle(self, signal, val):
        """Trigger for when an item is toggled (use lambda
        to specify signal)"""
        self.logic.optionChanged(signal, val)

    def enable(self, state):
        """Enable or disable the block"""
        for widget in itertools.chain.from_iterable(self.widgets):
            widget.setEnabled(state)
            
class PatchBanner(QtGui.QGroupBox):
    def __init__(self, qtparent):
        name = 'Patch Banner'
        super().__init__(name, qtparent)
        self.banner = QtGui.QLabel()
        self.banner.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse);
        self.banner.setOpenExternalLinks(True);
        html = '''No patch banner loaded'''
        self.banner.setText(html)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.banner)
        self.setLayout(layout)
        
    def setBanner(self, banner):
        self.banner.setText(banner)



class MainWindow(QtGui.QWidget):
    """The main window for the QT UI"""
    def __init__(self, logic):
        """Setup the main window - this is a big function"""
        super(MainWindow, self).__init__()
        vbox = QtGui.QVBoxLayout()
        self.logic = logic
        self.game = SelectorBlock('Game location', 'gameloc',
                                  self, self.logic)
        self.patch = SelectorBlock('Patch location', 'patchloc',
                                   self, self.logic)
        self.trans = SelectorBlock('Translation Location', 'transloc',
                                   self, self.logic)
        self.patchopts = PatchOptions(self, self.logic)
        self.progress = QtGui.QProgressBar()
        self.progress.setMinimum(0)
        self.comms = QtGui.QLabel('Waiting for backend..')
        self.errorLog = QtGui.QPlainTextEdit()
        self.errorLog.setReadOnly(True)
        self.errorLog.hide()
        self.patchBanner = PatchBanner(self)
        self.patchBanner.hide()
        self.gobutton = QtGui.QPushButton('Go!')
        label = QtGui.QLabel(labelString)
        label.setWordWrap(True)
        for x in (self.game, self.patch, self.trans, self.patchopts,
                  self.patchBanner, self.progress, self.comms, self.errorLog,
                  self.gobutton, label):
            vbox.addWidget(x)
        self.setLayout(vbox)
        self.setWindowTitle('RPGMaker Trans v%s' % versionString)
        self.gobutton.released.connect(
            lambda: self.logic.button('go'))
        iconimagefn = os.path.join(os.path.split(__file__)[0],
                                   'rpgtranslogo.svg')
        if os.path.exists(iconimagefn):
            with open(iconimagefn) as f:
                svg = f.read()
        else:
            svg = LOGOINTERNAL
        renderer = QtSvg.QSvgRenderer(QtCore.QXmlStreamReader(svg))
        img = QtGui.QPixmap(256, 256)
        painter = QtGui.QPainter(img)
        renderer.render(painter)
        del painter
        self.setWindowIcon(QtGui.QIcon(img))
        self.enableElements = {
            'gameloc': self.game.enable,
            'transloc': self.trans.enable,
            'patchloc': self.patch.enable,
            'options': self.patchopts.enable,
            'go': self.gobutton.setEnabled}
        self.fixSize()
        self.show()

    def fixSize(self):
        """Fix the size of the Window to be whatever it should be"""
        hint = self.sizeHint()
        height = hint.height()
        width = hint.width()
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)
        self.setMinimumWidth(width)
        self.setMaximumWidth(width)

    def enableElement(self, element, state):
        """Enable an element"""
        self.enableElements[element](state)

    def nonfatalError(self, msg):
        """Display a non-fatal error"""
        self.errorLog.show()
        self.errorLog.appendPlainText(msg)
        self.fixSize()

    def resetNonfatalErrors(self):
        """Reset the non-fatal errors"""
        self.errorLog.setPlainText('')
        self.errorLog.hide()
        self.fixSize()

    def closeEvent(self, event):
        """Override the close event to get confirmation from user if
        patching"""
        self.logic.stop()
        event.ignore()

    def displayMessage(self, style, title, maintext):
        """Display a message to the user"""
        msgBox = QtGui.QMessageBox(self)
        msgBox.setWindowTitle(title)
        msgBox.setText(maintext)
        msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
        if style == 'ErrorClass':
            msgBox.setIcon(QtGui.QMessageBox.Critical)
        elif style == 'OK':
            msgBox.setIcon(QtGui.QMessageBox.Information)
        return msgBox.exec_()

    def yesNoBox(self, title, maintext):
        """Display a modal yes/no box"""
        msgBox = QtGui.QMessageBox(self)
        msgBox.setWindowTitle(title)
        msgBox.setText(maintext)
        msgBox.setIcon(QtGui.QMessageBox.Question)
        msgBox.setStandardButtons(
            QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
        return msgBox.exec_() == QtGui.QMessageBox.Ok

    def getComboControl(self, controlID):
        """From a name, get a selector block"""
        control = None
        for x in self.game, self.trans, self.patch:
            if controlID == x.idtoken:
                control = x
                break
        if control:
            return control
        else:
            raise Exception('Unknown control ID')

    def comboBoxAdd(self, controlID, tokenName, tokenID, select=False):
        """Add something to a selector blocks combobox"""
        control = self.getComboControl(controlID)
        control.addItem(tokenName, tokenID)
        if select:
            control.selectItem(tokenID)

    def comboBoxRemove(self, controlID, tokenID):
        """Remove something from a selector blocks combobox"""
        control = self.getComboControl(controlID)
        control.removeItem(tokenID)

    def comboBoxSelect(self, controlID, tokenID):
        """Select an item in a combo box"""
        control = self.getComboControl(controlID)
        control.selectItem(tokenID)

    def getTransParams(self):
        """Get the parameters for translation from the UI"""
        ret = {'gameid': self.game.getCurrentSelectedID(),
               'patchid': self.patch.getCurrentSelectedID(),
               'transid': self.trans.getCurrentSelectedID(), }
        return ret
    
    def setPatchBanner(self, banner):
        """Set the patch banner"""
        if banner:
            self.patchBanner.setBanner(banner)
            self.patchBanner.show()
        else:
            self.patchBanner.hide()
        self.fixSize()

    def setProgress(self, percent):
        """Set the progress bar, in percent"""
        if percent == -1:
            self.progress.setMaximum(0)
        else:
            self.progress.setMaximum(100)
            self.progress.setValue(percent)

    def setMessage(self, message):
        """Set the message beneath the progress bar"""
        self.comms.setText(message)

    def fileDialog(self, title, wildcard):
        """Return a UTF string of the selected name"""
        return QtGui.QFileDialog.getOpenFileName(parent=self, caption=title,
                                                 filter=wildcard)[0]

    def dirDialog(self, title):
        """Return a UTF string of the selected directory"""
        return QtGui.QFileDialog.getExistingDirectory(
            parent=self,
            caption=title)


class Timer:
    """A very simple timer using QT"""
    def __init__(self, period, connectTo):
        self.timer = QtCore.QTimer()
        self.timer.start(period)
        self.timer.timeout.connect(connectTo)
