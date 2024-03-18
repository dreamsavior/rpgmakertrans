"""
coreprotocol
************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2015
:license: GNU Public License version 3

Defines CoreRunner and CoreProtocol, which take care of a lot of the hard
work of getting multiprocessing to play nicely with error messages/tracebacks,
and passing/taking action on messages between processes.
"""

import multiprocessing
import time
import signal
from collections import defaultdict
from .sender import SenderManager, SenderID
from ..errorhook import setErrorOut, handleError
import sys
import collections

try:
    # For Python 3.10 and above
    from collections.abc import Callable as ABCCallable
except ImportError:
    # For Python versions prior to 3.10
    ABCCallable = collections.Callable

ERRORSTRING = """An error was found with the following traceback:

%s

If you believe this is a bug, please report it to habisain@gmail.com
"""

class CoreRunner:
    """CoreRunner is the main scheduler that runs a set of CoreProtocol
    derived tasks"""
    def __init__(self, runners=None, errors=None):
        """Initialise the CoreRunner; can be given runners to run immediately,
        as well as an error Sender (if not given, error sender will be
        created automatically)"""
        if errors is None:
            self.errorManager = SenderManager()
            self.errorManager.start()
            errors = self.errorManager.Sender()
        self.errors = errors
        self.errorHandler = None
        self.__runOnFinished = {}
        self.running = []
        setErrorOut(self.errors)
        signal.signal(signal.SIGINT, self.sigint)

    def sigint(self, signal, frame):
        """Kill all processes when receiving a sigint"""
        for runner in self.running:
            runner.terminate()
        if hasattr(self, 'errorManager'):
            self.errorManager.shutdown()
        sys.exit(1)

    def initialise(self, cls, runOnFinished=None, **kwargs):
        """Given a class of a given CoreProtocol, initialise an
        instance of it. Supports kwargs"""
        newinstance = cls(runner=self, errout=self.errors, **kwargs)
        self.attach(newinstance)
        if runOnFinished is not None:
            self.runOnFinished(newinstance, runOnFinished)
        return newinstance

    def runOnFinished(self, runner, func):
        """Run a function when a runner stops running"""
        self.__runOnFinished[runner] = func

    def setErrorHandler(self, handler):
        """Set an error handler"""
        self.errorHandler = handler

    def getErrorSender(self):
        """Return the current error sender"""
        return self.errors

    def attach(self, runner):
        """Attach a CoreProtocol runner to this CoreRunner"""
        self.running.append(runner)

    def detach(self, runner):
        """Detach a runner from this CoreRunner"""
        if runner in self.running:
            self.running.remove(runner)

    def doError(self, errMsg):
        """Handle an error message"""
        for x in self.running:
            x.terminate()
        if self.errorHandler is not None:
            self.errorHandler(errMsg)
        else:
            sys.__stderr__.write(ERRORSTRING % errMsg)
            sys.__stderr__.flush()

    def run(self):
        """The main loop for the CoreRunner; will run all attached
        runners until all have died."""
        while self.running:
            detachments = []
            for runner in self.running:
                if runner.finished():
                    detachments.append(runner)
                    if runner in self.__runOnFinished:
                        self.__runOnFinished.pop(runner)()
                else:
                    runner.update()
            for runner in detachments:
                self.detach(runner)
            for msg in self.errors.get():
                if msg[0] == 'ERROR':
                    self.doError(*msg[1], **msg[2])
                else:
                    self.doError('Unknown code on error bus %s' % str(msg))
                    print('Unknown code on error bus %s' % str(msg))
                sys.exit(1)
            time.sleep(0.1)
        self.errorManager.shutdown()


class CoreProtocol:
    """The CoreProtocol runner which all tasks should inherit from"""
    def __init__(self, runner=None, inputcoms=None, outputcoms=None,
                 errout=None):
        """Initialise the CoreProtocol; normally should be on a runner
        and with an errout, but not necessarily. Each runner can manage
        one or more process pools."""
        if runner is None and errout is not None:
            errMsg = ('Must supply runner and errout arguments as '
                      'a pair or not at all')
            raise Exception(type(self).__name__ + errMsg)
        if inputcoms is None or outputcoms is None:
            self.senderManager = SenderManager()
            self.senderManager.start()
        if inputcoms is None:
            inputcoms = self.senderManager.Sender()
        if errout is None and hasattr(self, 'senderManager'):
            errout = self.senderManager.ErrorSender()
        self.runner = runner
        self.inputcoms = inputcoms
        if outputcoms is None:
            outputcoms = self.senderManager.Sender()
        self.outputcoms = outputcoms
        self.waiting = defaultdict(list)
        self.dispatched = set()
        self.pools = {}
        self.results = set()
        self.going = True
        self.localWaiting = defaultdict(list)
        self.combotriggers = {}
        self.subtriggers = defaultdict(list)
        self.errout = errout
        self.senderIDsToSenders = {}
        self.registerSenders(self.inputcoms, self.outputcoms, self.errout)

    def finished(self):
        """Return if the runner has finished"""
        return not self.going

    def reset(self):
        """Wait for and reset all pools of the runner"""
        for pool in self.pools:
            pool.join()
        self.pools.clear()

    def registerSender(self, sender):
        """Register a sender; the sender can then be automagically sent over
        multiprocess function calls to this runner only."""
        if sender:
            self.senderIDsToSenders[sender.senderID()] = sender

    def registerSenders(self, *senders):
        """Register a number of senders"""
        for sender in senders:
            self.registerSender(sender)

    def comboTrigger(self, triggername, subtriggers):
        """Define a combotrigger; when all subtrigger signals have been
        activated, the combotrigger signal will be activated."""
        subtriggerset = set(x for x in subtriggers
                            if x not in self.dispatched)
        if subtriggerset:
            for subtrigger in subtriggers:
                self.subtriggers[subtrigger].append((triggername,
                                                     subtriggerset))
        else:
            self.trigger(triggername)

    def waitUntil(self, signal, pool, fn, *args, **kwargs):
        """Wait until a given trigger signal, then activate the given
        function with given arguments on a given pool"""
        if signal in self.dispatched:
            self.submit(pool, fn, *args, **kwargs)
        else:
            self.waiting[signal].append((pool, fn, args, kwargs))

    def localWaitUntil(self, signal, fn, *args, **kwargs):
        """A version of waitUntil which dispatches the function on the
        main process rather than a pool. Useful for coroutine type
        pauses."""
        if signal in self.dispatched:
            fn(*args, **kwargs)
        else:
            self.localWaiting[signal].append((fn, args, kwargs))

    def processArg(self, arg):
        """Process an argument, replacing any SenderID with the corresponding
        sender"""
        if isinstance(arg, SenderID):
            if arg in self.senderIDsToSenders:
                return self.senderIDsToSenders[arg]
            else:
                raise Exception('Unknown Sender ID')
        else:
            return arg

    def submit(self, pool, fn, *args, **kwargs):
        """Submit a job to a pool"""
        #print("Target", pool, args, kwargs)
        if not self.going:
            return
        if pool == 'dbg':
            return fn(*args, **kwargs)
        args = [self.processArg(arg) for arg in args]
        for arg in kwargs:
            kwargs[arg] = self.processArg(kwargs[arg])
        ret = self.pools[pool].apply_async(fn, args=args, kwds=kwargs)
        self.results.add(ret)
        return ret

    def trigger(self, signal):
        """Send a trigger singal"""
        if signal not in self.dispatched:
            self.dispatched.add(signal)
            for pool, fn, args, kwargs in self.waiting[signal]:
                self.submit(pool, fn, *args, **kwargs)
            for fn, args, kwargs in self.localWaiting[signal]:
                fn(*args, **kwargs)
            for combotrigger, subtriggers in self.subtriggers[signal]:
                subtriggers.remove(signal)
                if not subtriggers:
                    self.trigger(combotrigger)

    def setupPool(self, pool, processes=None, minProcesses=None):
        """Setup a pool with the given name."""
        if processes is None:
            processes = multiprocessing.cpu_count()
        if minProcesses is not None:
            processes = max(processes, minProcesses)
        self.pools[pool] = multiprocessing.Pool(processes=processes,
                                                initializer=setErrorOut,
                                                initargs=[self.errout])

    def shutdown(self, pools=None):
        """Shutdown the CoreProtocol instance, stopping all associated
        subprocesses."""
        if pools is None:
            poolobjs = list(self.pools.values())
        else:
            poolobjs = [self.pools[pool] for pool in pools]
        for ret in self.results:
            ret.get()
        for pool in poolobjs:
            pool.close()
        for pool in poolobjs:
            pool.join()
        if hasattr(self, 'senderManager'):
            self.senderManager.shutdown()
        self.going = False

    def terminate(self, pools=None):
        """Terminate all pools. This is somewhat more immediate than
        shutdown."""
        if pools is None:
            poolobjs = list(self.pools.values())
        else:
            poolobjs = [self.pools[pool] for pool in pools]
        for pool in poolobjs:
            pool.terminate()
        self.going = False

    def update(self):
        """The main function of the CoreProtocol, handles dispatch of
        messages received of input coms."""
        events = self.inputcoms.get()
        while events:
            code, args, kwargs = events.pop(0)
            if (hasattr(self, code) and
                isinstance(getattr(self, code), ABCCallable)):  # Using ABCCallable
                try:
                    getattr(self, code)(*args, **kwargs)
                except Exception:
                    handleError()
            else:
                self.errout.send('ERROR', 'Got an unknown code: ' + str(code))
