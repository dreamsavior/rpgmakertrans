"""
headlessvx
**********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

HeadlessVX is the blind patching engine for RPGMaker VX games. As
with Headless (for 2k games), it communicates progress/errors to an
interface and coordinates progress/errors to an interface and
coordinates worker progress (including Ruby processes by Sockets).
"""
import asyncio

from .socketcomms import SocketComms
from .coreprotocol import CoreProtocol

class SocketCommsVX(SocketComms):
    def __init__(self, translator, filesToProcess, rpgversion, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.translator = translator
        self.filesToProcess = filesToProcess
        self.rpgversion = rpgversion.encode('utf-8')
        self.codeHandlers.update({1: self.translate,
                                  2: self.translateScript,
                                  3: self.getTaskParams,
                                  4: self.loadVersion})
        
    @asyncio.coroutine
    def checkForQuit(self):
        while True:
            yield from asyncio.sleep(0.1)
            if len(self.filesToProcess) > 0:
                return
        
    def translate(self, rawString, rawContext):
        string = rawString.decode('utf-8')
        context = rawContext.decode('utf-8')
        return self.translator.translate(string, context).encode('utf-8')
    
    def translateScript(self, rawScript):
        for encoding in ('utf-8', 'cp932'):
            try:
                script = rawScript.decode(encoding)
                raise NotImplementedError('TODO: Do I want to do this in a coroutine or something?')
            except UnicodeDecodeError:
                pass
    
    def getTaskParams(self):
        if len(self.filesToProcess) > 0:
            return self.filesToProcess.pop().encode('utf-8')
        else:
            return b':QUIT'
        
    def loadVersion(self):
        return self.rpgversion

class HeadlessVX(CoreProtocol):
    pass