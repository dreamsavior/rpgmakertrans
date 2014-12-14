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

from ...controllers.socketcomms import SocketComms

class RBCommsError(Exception): pass

class RBComms(SocketComms):
    def __init__(self, translator, filesToProcess, rpgversion, inputComs,
                 outputComs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inputComs = inputComs
        self.outputComs = outputComs
        self.translator = translator
        self.scripts = []
        self.translatedScripts = {}
        self.scriptWaiting = any(x.startswith('Scripts.') for x in filesToProcess)
        self.scriptsAreTranslated = not self.scriptWaiting
        self.scriptsRebuilding = False
        self.filesToProcess = filesToProcess
        self.rpgversion = rpgversion
        self.codeHandlers.update({1: self.translate,
                                  2: self.translateScript,
                                  3: self.getTaskParams,
                                  4: self.loadVersion,
                                  5: self.setScripts,
                                  6: self.getTranslatedScript})
        self.rawArgs.update({5: True})
        
    @asyncio.coroutine
    def checkForQuit(self):
        while True:
            yield from asyncio.sleep(0.1)
            if len(self.filesToProcess) == 0 and len(self.scripts) == 0 and not self.scriptWaiting:
                return
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
                self.outputComs.send('translateScript', name, script)
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
            return ('translateFile', self.filesToProcess.pop())
        elif self.scriptsAreTranslated:
            return ('quit')
        elif (len(self.scripts) == len(self.translatedScripts)
              and not self.scriptsRebuilding):
            self.scriptsRebuilding = True
            return ('rebuildScripts')
        else:
            return ('wait')
        
    def loadVersion(self):
        return self.rpgversion
