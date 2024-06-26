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
from collections import OrderedDict, defaultdict
import multiprocessing

from ...controllers.socketcomms import SocketComms, SocketCommsError
from ..rubyparse import translateRuby
from ...errorhook import errorWrap, handleError
from ...version import debug as debug_flag
import datetime

def _sortKey(item):
    if 'Map' in item[0]: return (1, item[0])
    elif 'CommonEvents' in item[0]: return (2, item[0])
    else: return (0, item[0])
    
class RBCommsError(Exception):
    """Error raised when something goes wrong in RBComms"""

class DummyScriptName(str): pass

def makeDummyScriptName(name, n):
    dummyName = name if name else 'Unnamed Script' 
    ret = DummyScriptName('%s(%s)' % (dummyName, n))
    ret.raw = name
    return ret

class RBComms(SocketComms):
    """RBComms is the specific instance of SocketComms to handle talking
    to Ruby processes. In general, I think I'd like to migrate away from
    subprocess Senders to asyncio + sockets, but this can ultimately wait."""

    def __init__(self, translator, filesToProcess, rpgversion, inputComs,
                 outputComs, subprocesses, debugRb = None, config=None,
                 *args, **kwargs):
        """Initialise RBComms"""
        super().__init__(config=config, *args, **kwargs)
        self.config = config
        self.inputComs = inputComs
        self.outputComs = outputComs
        self.translator = translator
        self.scripts = []
        self.magicNumbers = {}
        self.translatedScripts = {}
        self.rawScripts = []
        self.scriptInput = None
        self.scriptOutput = None
        self.scriptWaiting = False
        self.outputComs.send('setProgressDiv', 'patching',
                             len(filesToProcess))
        for item in [x for x in filesToProcess]:
            fn = os.path.split(item)[1]
            if fn.lower().startswith('scripts'):
                self.scriptWaiting = True
                self.scriptInput = item
                self.scriptOutput = filesToProcess.pop(item)[0]
        self.scriptsAreTranslated = not self.scriptWaiting
        self.scriptsRebuilding = False
        self.scriptsDumped = False
        self.filesToProcess = OrderedDict(sorted(filesToProcess.items(), key=_sortKey))
        self.rpgversion = rpgversion
        self.codeHandlers.update({1: self.translate,
                                  2: self.translateScript,
                                  3: self.getTaskParams,
                                  4: self.loadVersion,
                                  5: self.translateInlineScript,
                                  6: self.getTranslatedScript,
                                  7: self.doneTranslation,
                                  8: self.getScripts,})
        self.rawArgs.update({2: True, 5: True})
        self.subprocesses = subprocesses if not debugRb else 1
        self.debugRb = debugRb if debugRb is not None else debug_flag
        self.going = True
        self.tickTasks = [self.checkForQuit, self.getInputComs, self.startRubies]
        self.setEnv()
        self.name_counts = defaultdict(int)
        self.translationCount = 0
    
    def doFatalError(self, msg):
        """Send a fatal error message, then stop"""
        self.outputComs.send('fatalError', msg)
        self.going = False

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
                         'C:\\Ruby21\\bin\\ruby.exe')
            for attempt in rubyPaths:
                if os.path.isfile(attempt):
                    self.rubypath = attempt
                    return
            if self.rubypath is None:
                self.doFatalError('No applicable Ruby found\nDo you have the pruby folder or Ruby 1.93 installed?\n(Tried:\n%s)' %
                                     '\n'.join(rubyPaths))
        else:
            self.doFatalError('Unsupported platform')

    def openRuby(self):
        """Open a ruby process"""
        rbScriptPath = os.path.join(self.basedir, 'rubyscripts', 'main.rb')
        #dreamsavior debug
        print("Running ruby script")
        self.outputComs.send('displayMessage', "Opening ruby "+rbScriptPath+" with socket "+str(self.socket)+" and maxLine "+str(self.config.maxLine))

        piping = None if self.debugRb else subprocess.PIPE
        return subprocess.Popen([self.rubypath, rbScriptPath, str(self.socket), "-n", str(self.config.maxLine)],
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
                            if errMsg:
                                self.doFatalError('ERROR: Ruby unexpectedly quit.\nRuby Traceback:\n%s' % errMsg)
                            self.rubies.append(self.openRuby())
                if len(self.rubies) == 0:
                    self.going = False
        except:
            handleError()

    @asyncio.coroutine
    def getInputComs(self):
        """Get input communications from inputcoms sender"""
        #dreamsavior debug
        self.outputComs.send('displayMessage', "getInputComs")

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
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.translationCount += 1
        if self.translationCount % 100 == 0:
            self.outputComs.send('displayMessage', "[" + current_time + "] " + str(self.translationCount) + " items processed")
        return self.translator.translate(string, context)

    def translateScript(self, bName, bScript, magicNo):
        """Handler to request translation of a string"""
        print("Translating script", bName)
        name = bName.decode('utf-8')
        if name == '' or self.name_counts[name]:
            self.name_counts[name] += 1
            name = makeDummyScriptName(name, self.name_counts[name])
        self.name_counts[name] += 1
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
                self.outputComs.send('register_inline_script', script, context)
                try:
                    return translateRuby(script, context, self.translator, self.outputComs, inline=True)[1]
                except Exception as excpt:
                    errmsg = 'Error parsing inline script: %s; script not translated. Script %s' % (str(excpt), script)
                    self.outputComs.send('nonfatalError', errmsg)
                    return script
            except UnicodeDecodeError:
                pass
        self.outputComs.send('Couldn\'t find appropiate encoding for inline script %s, so script is untranslated' % context)
        return bScript

    def setTranslatedScript(self, name, script):
        """Handler to receive the translation of a script"""
        assert name not in self.translatedScripts, 'Script with duplicate name %s caused error' % name
        self.translatedScripts[name] = script
        self.outputComs.send('incProgress', 'scripts')
    
    @asyncio.coroutine
    def getScripts(self):
        """Returns the raw scripts, for loading into Ruby. Coroutine so that
        it can wait for the scripts to be loaded first."""
        # self.outputComs.send("displayMessage", '---getScripts')
        # print("getScripts", self)
        print("config:", vars(self.config))
        if not self.config.hasScripts:
            print("getScripts", "Script not found, skipping.")
            return self.rawScripts
        
        while not self.scriptsDumped:
            yield from asyncio.sleep(0.1)
        return self.rawScripts

    def getTranslatedScript(self):
        """Handler to output a translated script to Ruby"""
        if self.scripts:
            name = self.scripts.pop(0)
            rName = name.raw if isinstance(name, DummyScriptName) else name
            script = self.translatedScripts.pop(name)
            if len(self.scripts) == 0:
                self.scriptsAreTranslated = True
            return (str(len(self.scripts)), rName, self.magicNumbers[name],
                    script)
        else:
            raise RBCommsError('Asked for translated script'
                               'which does not exist')

    def getTaskParams(self):
        """Handler to get parameters for next Ruby task"""
        if self.scriptInput is not None:
            # print("Mode translateScripts", self.scriptInput)
            self.outputComs.send("displayMessage", "Script input:"+self.scriptInput)
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
            self.outputComs.send('setProgressDiv', 'scripts', len(self.scripts))
        else:
            self.outputComs.send('incProgress', 'patching')

    def loadVersion(self):
        """Handler to tell Ruby what RPGMaker version to use"""
        return self.rpgversion

@errorWrap
def startRBComms(filesToProcess, translator, mtimes, newmtimes,
                 outputComs, inputComs, rpgversion, config=None):
    """Entry point for multiprocessing to start RBComms."""
    subprocesses = multiprocessing.cpu_count()
    rbcomms = RBComms(translator, filesToProcess, rpgversion, inputComs,
                      outputComs, subprocesses, config=config)
    try:
        rbcomms.start()
    except SocketCommsError as e:
        outputComs.send('nonFatalError', 'Could not start Ruby Patcher.\nTry opening ports, killing processes, or logging off and on again.\nThe following error gives more information\n')
        outputComs.send('fatalError', str(e))
