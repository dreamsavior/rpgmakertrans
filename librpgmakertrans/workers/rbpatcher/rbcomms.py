"""
rbcomms
*******

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

RBComms is the communicator to the child Ruby processes, which
happens over sockets. It is given a list of files to process, and
sorts things out from there.
"""
import asyncio
import os
import subprocess
from collections import OrderedDict
import multiprocessing

from ...controllers.socketcomms import SocketComms
from librpgmakertrans.errorhook import errorWrap

if os.name == 'posix':
    RUBYPATH = 'ruby'
else:
    raise Exception('Unsupported Platform')

class RBCommsError(Exception):
    """Error raised when something goes wrong in RBComms"""

class RBComms(SocketComms):
    """RBComms is the specific instance of SocketComms to handle talking
    to Ruby processes. In general, I think I'd like to migrate away from
    subprocess Senders to asyncio + sockets, but this can ultimately wait."""

    maxRubyErrors = 10

    def __init__(self, translator, filesToProcess, rpgversion, inputComs,
                 outputComs, subprocesses, debugRb = False, *args, **kwargs):
        """Initialise RBComms"""
        super().__init__(*args, **kwargs)
        self.inputComs = inputComs
        self.outputComs = outputComs
        self.translator = translator
        self.scripts = []
        self.magicNumbers = {}
        self.translatedScripts = {}
        self.scriptInput = None
        self.scriptOutput = None
        self.scriptWaiting = False
        self.outputComs.send('setProgressDiv', 'patching',
                             len(filesToProcess))
        for item in [x for x in filesToProcess]:
            if item.endswith('Scripts.rvdata'):
                self.scriptWaiting = True
                self.scriptInput = item
                self.scriptOutput = filesToProcess.pop(item)[0]
        self.scriptsAreTranslated = not self.scriptWaiting
        self.scriptsRebuilding = False
        self.scriptsDumped = False
        self.filesToProcess = OrderedDict(filesToProcess)
        self.rpgversion = rpgversion
        self.codeHandlers.update({1: self.translate,
                                  2: self.translateScript,
                                  3: self.getTaskParams,
                                  4: self.loadVersion,
                                  6: self.getTranslatedScript,
                                  7: self.doneTranslation})
        self.rawArgs.update({2: True})
        self.subprocesses = subprocesses
        self.debugRb = debugRb
        self.going = True
        self.tickTasks = [self.checkForQuit, self.getInputComs, self.startRubies]
        self.rubyErrorMessages = set()
        self.rubyErrors = 0

    @staticmethod
    def makeFilesToProcess(indir, outdir):
        """Make the list of files to process."""
        files = {}
        for fn in os.listdir(indir):
            if fn.endswith('.rvdata'): # TODO: Support for VX Ace + XP
                files[os.path.join(indir, fn)] = (os.path.join(outdir, fn),
                                                  fn.rpartition('.rvdata')[0])
        return files

    def openRuby(self):
        """Open a ruby process"""
        base = os.path.split(__file__)[0]
        rbScriptPath = os.path.join(base, 'rubyscripts', 'main.rb')
        piping = None if self.debugRb else subprocess.PIPE
        return subprocess.Popen([RUBYPATH, rbScriptPath],
                                stdin=piping, stdout=piping, stderr=subprocess.PIPE)

    @asyncio.coroutine
    def startRubies(self):
        """Start ruby processes"""
        self.rubies = [self.openRuby() for _ in range(self.subprocesses)]

    @asyncio.coroutine
    def checkForQuit(self):
        """Check to see if we should quit"""
        while self.going:
            yield from asyncio.sleep(0.1)
            for ruby in self.rubies[:]:
                rbpoll = ruby.poll()
                if rbpoll is not None:
                    self.rubies.remove(ruby)
                    if rbpoll != 0:
                        print('WARNING: Ruby with nonzero exit code')
                        errMsg = ruby.stderr.read()
                        self.rubyErrors += 1
                        if errMsg in self.rubyErrorMessages:
                            # TODO: Replace these errors with fatal error messages
                            raise RBCommsError('Repeated Ruby Error Message %s, Quitting' % errMsg)
                            self.going = False
                        elif self.rubyErrors >= type(self).maxRubyErrors:
                            errorMessageLS = ['More than %s Ruby Error Messages:' % type(self).maxRubyErrors]
                            errorMessageLS.extend(self.rubyErrors)
                            raise RBCommsError('\n'.join(errorMessageLS))
                            self.going = False
                        self.rubyErrorMessages.add(errMsg)
                        if not self.debugRb:
                            print(ruby.stderr.read())
                        self.rubies.append(self.openRuby())
            if len(self.rubies) == 0:
                self.going = False

    @asyncio.coroutine
    def getInputComs(self):
        """Get input communications from inputcoms sender"""
        while self.going:
            yield from asyncio.sleep(0.1)
            for code, args, kwargs in self.inputComs.get():
                if code != 'setTranslatedScript':
                    raise RBCommsError('Cannot respond to event %s' % code)
                self.setTranslatedScript(*args, **kwargs)

    def translate(self, string, context):
        """Handler to translate a string"""
        return self.translator.translate(string, context)

    def translateScript(self, bName, bScript, magicNo):
        """Handler to request translation of a string"""
        for encoding in ('utf-8', 'cp932'):
            try:
                name = bName.decode(encoding)
                script = bScript.decode(encoding)
                self.outputComs.send('translateScript', name, script,
                                     self.translator, self.inputComs)
                self.scripts.append(name)
                self.magicNumbers[name] = magicNo.decode('utf-8')
                return
            except UnicodeDecodeError:
                pass
        # TODO: Send an error of errout, and set script to be raw script.
        raise UnicodeDecodeError('Couldn\'t find appropriate'
                                 'encoding for script')

    def setTranslatedScript(self, name, script):
        """Handler to receive the translation of a script"""
        self.translatedScripts[name] = script

    def getTranslatedScript(self):
        """Handler to output a translated script to Ruby"""
        if self.scripts:
            name = self.scripts.pop(0)
            script = self.translatedScripts.pop(name)
            if len(self.scripts) == 0:
                self.scriptsAreTranslated = True
            return (str(len(self.scripts)), name, self.magicNumbers[name],
                    script)
        else:
            raise RBCommsError('Asked for translated script'
                               'which does not exist')

    def getTaskParams(self):
        """Handler to get parameters for next Ruby task"""
        if self.scriptInput is not None:
            ret = ('translateScripts', self.scriptInput)
            self.scriptInput = None
            return ret
        elif len(self.filesToProcess) > 0:
            item = self.filesToProcess.popitem()
            return ('translateFile', item[0]) + item[1]
        elif self.scriptsAreTranslated:
            return ('quit')
        elif (self.scriptsDumped and
              len(self.scripts) == len(self.translatedScripts)
              and not self.scriptsRebuilding):
            self.scriptsRebuilding = True
            return ('rebuildScripts', self.scriptOutput)
        else:
            return ('wait')

    def doneTranslation(self, context):
        """Handler to register completion of a task"""
        if context == 'ScriptsDumped':
            self.scriptsDumped = True
        else:
            self.outputComs.send('incProgress', 'patching')

    def loadVersion(self):
        """Handler to tell Ruby what RPGMaker version to use"""
        return self.rpgversion

@errorWrap
def startRBComms(indir, outdir, translator, mtimes, newmtimes,
                 outputComs, inputComs):
    """Entry point for multiprocessing to start RBComms.
    VX only at present. The input/output directories should be
    the data directories (todo: recursive approach)"""
    filesToProcess = RBComms.makeFilesToProcess(indir, outdir)
    rpgversion = 'vx'
    subprocesses = multiprocessing.cpu_count()
    rbcomms = RBComms(translator, filesToProcess, rpgversion, inputComs,
                      outputComs, subprocesses)
    rbcomms.start()
