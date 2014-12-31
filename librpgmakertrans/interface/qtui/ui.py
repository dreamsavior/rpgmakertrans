"""
qtui
****

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

The implementation of the QT user interface.
"""

import os
from PySide import QtGui, QtCore, QtSvg
from ...errorhook import ErrorClass, ErrorMeta
from ...version import version

from .logointernal import LOGOINTERNAL

labelString = ''.join([
    "RPGMaker Trans (C) Habisain 2011-2015\n",
    "Redistributing a game patched by RPGMaker Trans ",
    "will likely breach copyright on that game, and ",
    "so you should not do so without the original ",
    "authors permission, even for free games. "])


class SelectorBlock(ErrorClass, QtGui.QGroupBox):

    def __init__(self, name, idtoken, qtparent, eventComms):
        super(SelectorBlock, self).__init__(name, qtparent)
        self.outputComs = eventComms
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
        self.combobox.addItem(item, idtoken)

    def changedIndex(self, index):
        self.outputComs.send('changeSelected', self.idtoken,
                             self.getCurrentSelectedID())

    def enable(self, state):
        self.combobox.setEnabled(state)
        self.browseButton.setEnabled(state)

    def selectItem(self, idtoken):
        self.combobox.setCurrentIndex(self.combobox.findData(idtoken))

    def getCurrentSelectedID(self):
        return self.combobox.itemData(self.combobox.currentIndex())

    def browsePressed(self):
        self.outputComs.send('button', self.idtoken)


class PatchOptions(ErrorClass, QtGui.QGroupBox):

    def __init__(self, qtparent, outputComs):
        name = 'Patch Options'
        self.outputComs = outputComs
        super(PatchOptions, self).__init__(name, qtparent)
        hbox = QtGui.QHBoxLayout()
        self.create = QtGui.QCheckBox('Create patch', self)
        self.create.setToolTip('When first starting a translation project,\n'
                               'select this to create the initial patch')
        self.useBOM = QtGui.QCheckBox('Use UTF-8 BOM', self)
        self.useBOM.setToolTip(
            'Some editors will only recognise UTF-8 files\n'
            'with a BOM, although this will break other editors.\n'
            'Enabling this option will cause RPGMaker Trans files\n'
            'to have a UTF-8 BOM.')
        self.widgets = [self.create, self.useBOM]
        for x in self.widgets:
            hbox.addWidget(x)
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox)
        self.setLayout(vbox)
        self.create.toggled.connect(lambda: self.toggle('create',
                                    self.create.isChecked()))
        self.useBOM.toggled.connect(lambda: self.toggle('bom',
                                    self.useBOM.isChecked()))

    def toggle(self, signal, val):
        self.outputComs.send('optionChanged', signal, val)

    def enable(self, state):
        for widget in self.widgets:
            widget.setEnabled(state)


class MainWindow(ErrorClass, QtGui.QWidget):

    def __init__(self, eventComms):
        super(MainWindow, self).__init__()
        vbox = QtGui.QVBoxLayout()
        self.outputComs = eventComms
        self.game = SelectorBlock('Game location', 'gameloc',
                                  self, self.outputComs)
        self.patch = SelectorBlock('Patch location', 'patchloc',
                                   self, self.outputComs)
        self.trans = SelectorBlock('Translation Location', 'transloc',
                                   self, self.outputComs)
        self.patchopts = PatchOptions(self, self.outputComs)
        self.progress = QtGui.QProgressBar()
        self.progress.setMinimum(0)
        self.comms = QtGui.QLabel('Waiting for backend..')
        self.errorLog = QtGui.QPlainTextEdit()
        self.errorLog.setReadOnly(True)
        self.errorLog.hide()
        self.gobutton = QtGui.QPushButton('Go!')
        label = QtGui.QLabel(labelString)
        label.setWordWrap(True)
        for x in (self.game, self.patch, self.trans, self.patchopts,
                  self.progress, self.comms, self.errorLog, self.gobutton,
                  label):
            vbox.addWidget(x)
        self.setLayout(vbox)
        self.setWindowTitle('RPGMaker Trans v%s' % str(version))
        self.gobutton.released.connect(
            lambda: self.outputComs.send(
                'button',
                'go'))
        hint = self.sizeHint()
        height = hint.height()
        width = hint.width()
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
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)
        self.setMinimumWidth(width)
        self.setMaximumWidth(width)
        self.enableElements = {
            'gameloc': self.game.enable,
            'transloc': self.trans.enable,
            'patchloc': self.patch.enable,
            'options': self.patchopts.enable,
            'go': self.gobutton.setEnabled}
        self.show()

    def enableElement(self, element, state):
        self.enableElements[element](state)

    def nonfatalError(self, msg):
        self.errorLog.show()
        self.errorLog.appendPlainText(msg)

    def resetNonfatalErrors(self):
        self.errorLog.setPlainText('')
        self.errorLog.hide()

    def closeEvent(self, event):
        self.outputComs.send('stop')
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

    def yesNoBox(self, title, maintext):
        msgBox = QtGui.QMessageBox(self)
        msgBox.setWindowTitle(title)
        msgBox.setText(maintext)
        msgBox.setIcon(QtGui.QMessageBox.Question)
        msgBox.setStandardButtons(
            QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
        return msgBox.exec_() == QtGui.QMessageBox.Ok

    def getComboControl(self, controlID):
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
        control = self.getComboControl(controlID)
        control.addItem(tokenName, tokenID)
        if select:
            control.selectItem(tokenID)

    def comboBoxSelect(self, controlID, tokenID):
        control = self.getComboControl(controlID)
        control.selectItem(tokenID)

    def getTransParams(self):
        ret = {'gameid': self.game.getCurrentSelectedID(),
               'patchid': self.patch.getCurrentSelectedID(),
               'transid': self.trans.getCurrentSelectedID(), }
        return ret

    def setProgress(self, percent):
        if percent == -1:
            self.progress.setMaximum(0)
        else:
            self.progress.setMaximum(100)
            self.progress.setValue(percent)

    def setMessage(self, message):
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


class Timer(object, metaclass=ErrorMeta):

    def __init__(self, period, connectTo):
        self.timer = QtCore.QTimer()
        self.timer.start(period)
        self.timer.timeout.connect(connectTo)
