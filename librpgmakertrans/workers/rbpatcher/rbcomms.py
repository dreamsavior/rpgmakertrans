"""
rbcomms
*******

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2015
:license: GNU Public License version 3

RBComms is the communicator to the child Ruby processes, which
happens over sockets. It is given a list of files to process, and
sorts things out from there.
"""
import asyncio
import os
import subprocess
import sys
from collections import OrderedDict
import multiprocessing

from ...controllers.socketcomms import SocketComms
from ..rubyparse import translateRuby
from ...errorhook import errorWrap, handleError

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
                                  5: self.translateInlineScript,
                                  6: self.getTranslatedScript,
                                  7: self.doneTranslation,})
        self.rawArgs.update({2: True, 5: True})
        self.subprocesses = subprocesses
        self.debugRb = debugRb
        self.going = True
        self.tickTasks = [self.checkForQuit, self.getInputComs, self.startRubies]
        self.rubyErrorMessages = set()
        self.rubyErrors = 0
        self.setEnv()

    def setEnv(self):
        """Set the variables for the ruby interpreter used"""
        if getattr(sys, 'frozen', False):
            self.basedir = os.path.dirname(sys.executable)
        else:
            self.basedir = os.path.dirname(__file__)
        if os.name in ('posix', 'darwin'):
            self.rubypath = 'ruby'
        elif os.name == 'nt':
            self.rubypath = None
            rubyPaths = (os.path.join(self.basedir, 'pruby', 'bin', 'rubyw.exe'),
                         'C:\\Ruby193\\bin\\ruby.exe')
            for attempt in rubyPaths:
                if os.path.isfile(attempt):
                    self.rubypath = attempt
                    break
            if not self.rubypath is None:
                raise Exception('No applicable Ruby found\nDo you have the pruby folder or Ruby 1.93 installed?\n(Tried:\n%s)' %
                                '\n'.join(rubyPaths))
        else:
            raise Exception('Unsupported Platform')

    def openRuby(self):
        """Open a ruby process"""
        rbScriptPath = os.path.join(self.basedir, 'rubyscripts', 'main.rb')
        piping = None if self.debugRb else subprocess.PIPE
        return subprocess.Popen([self.rubypath, rbScriptPath, str(self.socket)],
                                stdin=piping, stdout=piping, stderr=subprocess.PIPE)

    @asyncio.coroutine
    def startRubies(self):
        """Start ruby processes"""
        try:
            self.rubies = [self.openRuby() for _ in range(self.subprocesses)]
        except:
            handleError()

    @asyncio.coroutine
    def checkForQuit(self):
        """Check to see if we should quit"""
        try:
            while self.going:
                yield from asyncio.sleep(0.1)
                for ruby in self.rubies[:]:
                    rbpoll = ruby.poll()
                    if rbpoll is not None:
                        self.rubies.remove(ruby)
                        if rbpoll != 0:
                            self.outputComs.send('nonfatalError',
                                                 'WARNING: Ruby with nonzero exit code %s' % rbpoll)
                            errMsg = ruby.stderr.read().decode('utf-8')
                            self.rubyErrors += 1
                            if errMsg in self.rubyErrorMessages:
                                # TODO: Replace these errors with fatal error messages
                                raise RBCommsError('Repeated Ruby Error Message %s, Quitting' % errMsg)
                                self.going = False
                            elif self.rubyErrors >= type(self).maxRubyErrors:
                                errorMessageLS = ['More than %s Ruby Error Messages:' % type(self).maxRubyErrors]
                                errorMessageLS.extend(errMsg for errMsg in self.rubyErrorMessages)
                                raise RBCommsError('\n'.join(errorMessageLS))
                                self.going = False
                            self.rubyErrorMessages.add(errMsg)
                            if self.debugRb:
                                print(errMsg)
                            self.rubies.append(self.openRuby())
                if len(self.rubies) == 0:
                    self.going = False
        except:
            handleError()

    @asyncio.coroutine
    def getInputComs(self):
        """Get input communications from inputcoms sender"""
        try:
            while self.going:
                yield from asyncio.sleep(0.1)
                for code, args, kwargs in self.inputComs.get():
                    if code != 'setTranslatedScript':
                        raise RBCommsError('Cannot respond to event %s' % code)
                    self.setTranslatedScript(*args, **kwargs)
        except:
            handleError()

    def translate(self, string, context):
        """Handler to translate a string"""
        return self.translator.translate(string, context)

    def translateScript(self, bName, bScript, magicNo):
        """Handler to request translation of a string"""
        name = bName.decode('utf-8')
        for encoding in ('utf-8', 'cp932'):
            try:
                script = bScript.decode(encoding)
                self.outputComs.send('translateScript', name, script,
                                     self.translator, self.inputComs,
                                     self.outputComs)
                self.scripts.append(name)
                self.magicNumbers[name] = magicNo.decode('utf-8')
                return
            except UnicodeDecodeError:
                pass
        self.outputComs.send('Couldn\'t find appropiate encoding for script %s, so script is untranslated' % name)
        self.scripts.append(name)
        self.translatedScripts[name] = bScript

    def translateInlineScript(self, bScript, bContext):
        """Translate an inline script. These are typically short, so they're
        done in the main process.
        TODO: If encountering a big inline script, offload it"""
        context = bContext.decode('utf-8')
        for encoding in ('utf-8', 'cp932'):
            try:
                script = bScript.decode(encoding)
                try:
                    return translateRuby(script, context, self.translator)[1]
                except Exception as excpt:
                    errmsg = 'Error parsing inline script: %s; script not translated' % str(excpt)
                    self.outputComs.send('nonfatalError', errmsg)
                    return script
            except UnicodeDecodeError:
                pass
        self.outputComs.send('Couldn\'t find appropiate encoding for inline script %s, so script is untranslated' % context)
        return bScript

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
def startRBComms(filesToProcess, translator, mtimes, newmtimes,
                 outputComs, inputComs, rpgversion, socket=None):
    """Entry point for multiprocessing to start RBComms."""
    subprocesses = multiprocessing.cpu_count()
    rbcomms = RBComms(translator, filesToProcess, rpgversion, inputComs,
                      outputComs, subprocesses, socket=socket)
    rbcomms.start()
