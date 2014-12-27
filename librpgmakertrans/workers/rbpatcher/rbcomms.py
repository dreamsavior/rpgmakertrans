"""
rbcomms
*******

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

SocketCommsRB is the communicator to the child Ruby processes, which
happens over sockets. It is given a list of files to process, and
sorts things out from there.
"""
import asyncio
import os
import subprocess
from collections import OrderedDict

from ...controllers.socketcomms import SocketComms
from librpgmakertrans.errorhook import errorWrap

if os.name == 'posix':
    RUBYPATH = 'ruby'
else:
    raise Exception('Unsupported Platform')

class RBCommsError(Exception): pass

class RBComms(SocketComms):
    def __init__(self, translator, filesToProcess, rpgversion, inputComs,
                 outputComs, subprocesses, debugRb = True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inputComs = inputComs
        self.outputComs = outputComs
        self.translator = translator
        self.scripts = []
        self.translatedScripts = {}
        self.scriptWaiting = any(x.endswith('Scripts.rvdata') for x in filesToProcess)
        self.scriptsAreTranslated = not self.scriptWaiting
        self.scriptsRebuilding = False
        self.filesToProcess = OrderedDict(filesToProcess)
        self.rpgversion = rpgversion
        self.codeHandlers.update({1: self.translate,
                                  2: self.translateScript,
                                  3: self.getTaskParams,
                                  4: self.loadVersion,
                                  5: self.setScripts,
                                  6: self.getTranslatedScript,
                                  7: self.doneTranslation})
        self.rawArgs.update({5: True})
        self.subprocesses = subprocesses
        self.debugRb = debugRb
        self.going = True
        self.tickTasks = [self.checkForQuit, self.getInputComs]
        self.outputComs.send('setProgressDiv', 'patching', 
                             len(self.filesToProcess))
        
    @staticmethod
    def makeFilesToProcess(indir, outdir):
        files = {}
        for fn in os.listdir(indir):
            if fn == 'Armors.rvdata': #fn.endswith('.rvdata') and fn != 'Scripts.rvdata':
                files[os.path.join(indir, fn)] = (os.path.join(outdir, fn), fn.rpartition('.rvdata')[0])
        return files    
                
    def start(self):
        base = os.path.split(__file__)[0]
        rbScriptPath = os.path.join(base, 'rubyscripts', 'main.rb')
        piping = None if self.debugRb else subprocess.PIPE
        openRuby = lambda: subprocess.Popen([RUBYPATH, rbScriptPath],
                                stdin=piping, stdout=piping, stderr=piping) 
        self.rubies = [openRuby() for _ in range(self.subprocesses)]
        super().start()
        
    @asyncio.coroutine
    def checkForQuit(self):
        while self.going:
            yield from asyncio.sleep(0.1)
            for ruby in self.rubies[:]:
                if ruby.poll() is not None:
                    self.rubies.remove(ruby)
            if len(self.rubies) == 0: 
                self.going = False
            
    @asyncio.coroutine
    def getInputComs(self):
        while self.going:
            yield from asyncio.sleep(0.1)
            if self.inputComs:
                for code, args, kwargs in self.inputComs.get():
                    assert code == 'setTranslatedScript', 'Can only respond to one event!'
                    self.setTranslatedScript(*args, **kwargs)
        
    def translate(self, string, context):
        return self.translator.translate(string, context)
    
    def setScripts(self, *scripts):
        self.scripts = list(scripts)
        self.scriptWaiting = False
    
    def translateScript(self, bName, bScript):
        for encoding in ('utf-8', 'cp932'):
            try:
                name = bName.decode(encoding)
                script = bScript.decode(encoding)
                self.outputComs.send('translateScript', name, script, 
                                     self.translator, self.inputComs)
            except UnicodeDecodeError:
                pass
            
    def setTranslatedScript(self, name, script):
        self.translatedScripts[name] = script
        
    def getTranslatedScript(self):
        if self.scripts:
            name = self.scripts.pop(0)
            script = self.translatedScripts.pop(name)
            return len(self.scripts), name, script
        else:
            raise RBCommsError('Asked for translated script which does not exist')
    
    def getTaskParams(self):
        if len(self.filesToProcess) > 0:
            item = self.filesToProcess.popitem()
            return ('translateFile', item[0]) + item[1]
        elif self.scriptsAreTranslated:
            return ('quit')
        elif (len(self.scripts) == len(self.translatedScripts)
              and not self.scriptsRebuilding):
            self.scriptsRebuilding = True
            return ('rebuildScripts')
        else:
            return ('wait')
        
    def doneTranslation(self, context):
        self.outputComs.send('incProgress', 'patching')
        
    def loadVersion(self):
        return self.rpgversion

@errorWrap
def startRBComms(indir, outdir, translator, mtimes, newmtimes, 
                 outputComs, inputComs):
    filesToProcess = RBComms.makeFilesToProcess(indir, outdir)
    rpgversion = 'vx'
    subprocesses = 1
    rbcomms = RBComms(translator, filesToProcess, rpgversion, inputComs,
                      outputComs, subprocesses)
    rbcomms.start()

if __name__ == '__main__':
    indir = '/home/habisain/LiliumUnion/Data'
    from ..translator.translator3 import Translator3
    from ..translator import TranslatorManager
    from ...controllers.sender import SenderManager
    files = {}
    for fn in os.listdir(indir):
        if fn == 'Armors.rvdata': #fn.endswith('.rvdata') and fn != 'Scripts.rvdata':
            files[os.path.join(indir, fn)] = (os.path.join(indir, 'o', fn), fn.rpartition('.rvdata')[0])
    senderManager = SenderManager()
    senderManager.start()
    errour = senderManager.Sender()
    translatorManager = TranslatorManager()
    translatorManager.start(errour)
    translator = translatorManager.Translator3({})
    tester = RBComms(translator, files, 'vx', None, None, 1, debugRb=True)
    tester.start()