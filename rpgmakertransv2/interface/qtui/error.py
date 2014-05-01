from PySide import QtGui, QtCore
import sys

class ErrorMsg(QtGui.QDialog):
    def __init__(self, clip):
        super(ErrorMsg, self).__init__()
        label = QtGui.QLabel('An error has occurred and RPGMaker Trans has to close.\n'
                             'If you believe this is a bug, please make sure that the\n'
                             'traceback below is attached with any bug report\n')
        self.textArea = QtGui.QPlainTextEdit()
        self.msg = ''
        self.textArea.setReadOnly(True)
        button = QtGui.QPushButton('Copy to clipboard and open Bug Reports page')
        button2 = QtGui.QPushButton('Close RPGMaker Trans')
        vbox = QtGui.QVBoxLayout()
        for x in (label, self.textArea, button, button2):
            vbox.addWidget(x)
         
        self.setLayout(vbox)    
        self.setWindowTitle('RPGMaker Trans Error')
        button.released.connect(lambda: (clip.setText(self.msg), QtGui.QDesktopServices.openUrl('http://habisain.blogspot.co.uk/p/bug-reporting.html')))
        button2.released.connect(lambda: self.done(0))
        
    def setMsg(self, msg):
        self.textArea.setPlainText(msg)
        self.msg = msg
        
def errorMsg(msg):
    app = QtGui.QApplication([])
    clip = app.clipboard()
    dlg = ErrorMsg(clip)
    dlg.setMsg(msg)
    dlg.exec_()
    dlg.destroy()

if __name__ == '__main__':
    test = errorMsg('This is a test in place of an actual traceback.')