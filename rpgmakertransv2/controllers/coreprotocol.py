'''
Created on 20 Sep 2013

@author: habisain
'''

import multiprocessing, time, signal
from collections import defaultdict
from .sender import SenderManager
from ..errorhook import setErrorOut, ErrorMeta
import sys
import collections

class CoreRunner(object):
    def __init__(self, runners=None, errors=None):
        if errors is None:
            self.errorManager = SenderManager()
            self.errorManager.start()
            errors = self.errorManager.Sender()
        self.errors = errors
        self.errorHandler = None
        self.running = []
        setErrorOut(self.errors)
        signal.signal(signal.SIGINT, self.sigint)
        
    def sigint(self, signal, frame):
        for runner in self.running:
            runner.terminate()        
        
    def initialise(self, cls, **kwargs):
        newinstance = cls(runner=self, errout=self.errors, **kwargs)
        self.attach(newinstance)
        return newinstance
    
    def setErrorHandler(self, handler):
        self.errorHandler = handler
        
    def getErrorSender(self):
        return self.errors
    
    def attach(self, runner):
        self.running.append(runner)
        
    def detach(self, runner):
        if runner in self.running: self.running.remove(runner)
    
    def doError(self, errMsg):
        for x in self.running:
            x.terminate()
        if self.errorHandler is not None:
            self.errorHandler(errMsg)
        else:
            sys.__stderr__.write('An error was found with the following traceback \n\n%s\n\nIf you believe this is a bug, please report it to habisain@gmail.com\n\n' % errMsg)
            sys.__stderr__.flush()
        
    def run(self):
        while self.running:
            detachments = []
            for runner in self.running:
                runner.update()
                if runner.finished():
                    detachments.append(runner)
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

class CoreProtocol(object, metaclass=ErrorMeta):
    def __init__(self, runner=None, inputcoms=None, outputcoms=None, errout=None):
        if runner is None and errout is not None:
            raise Exception('%s: Must supply runner and errout arguments as a pair or not at all' % str(type(self)))
        if inputcoms is None or outputcoms is None:
            self.senderManager = SenderManager()
            self.senderManager.start()
        if inputcoms is None: inputcoms = self.senderManager.Sender()
        self.runner = runner
        self.inputcoms = inputcoms
        if outputcoms is None: outputcoms = self.senderManager.Sender()
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
        
    def finished(self):
        return not self.going
        
    def reset(self): 
        for pool in self.pools: pool.join()
        self.pools.clear()
        
    def comboTrigger(self, triggername, subtriggers):
        subtriggerset = set(x for x in subtriggers if x not in self.dispatched)
        if subtriggerset:
            for subtrigger in subtriggers:
                self.subtriggers[subtrigger].append((triggername, subtriggerset))
        else:
            self.trigger(triggername)
        
    def waitUntil(self, signal, pool, fn, *args, **kwargs):
        if signal in self.dispatched: self.submit(pool, fn, *args, **kwargs)
        else: self.waiting[signal].append((pool, fn, args, kwargs))
        
    def localWaitUntil(self, signal, fn, *args, **kwargs):
        if signal in self.dispatched: fn(*args, **kwargs)
        else: self.localWaiting[signal].append((fn, args, kwargs))
        
    def submit(self, pool, fn, *args, **kwargs):
        if pool == 'dbg':
            return fn(*args, **kwargs)
        if 'outputcoms' in args:
            args = list(args)
            args[args.index('outputcoms')] = self.inputcoms
        else:
            for (key, value) in list(kwargs.items()):
                if value == 'outputcoms':
                    kwargs[key] = self.inputcoms
        ret = self.pools[pool].apply_async(fn, args=args, kwds=kwargs)
        self.results.add(ret)
        return ret
        
    def trigger(self, signal):
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
                    
    def checkResults(self):
        remove = set()
        for ret in self.results:
            if ret.ready(): 
                ret.get()
                remove.add(ret)
        for removal in remove:
            self.results.remove(removal)
            
    def setupPool(self, pool, processes=None):
        if processes is None: 
            processes = multiprocessing.cpu_count()
        self.pools[pool] = multiprocessing.Pool(
                            processes=processes,
                            initializer=setErrorOut, 
                            initargs=[self.errout])
                
    def shutdown(self, pools=None):
        if pools is None: poolobjs = list(self.pools.values())
        else: poolobjs = [self.pools[pool] for pool in pools]
        for ret in self.results: ret.get()
        for pool in poolobjs: 
            pool.close()
        for pool in poolobjs:
            pool.join()
        self.going = False
        
    def terminate(self, pools=None):
        if pools is None: poolobjs = list(self.pools.values())
        else: poolobjs = [self.pools[pool] for pool in pools]
        for pool in poolobjs: pool.terminate()
        self.going = False
                    
    def update(self, coms=None):
        events = self.inputcoms.get()
        while events:
            code, args, kwargs = events.pop(0)
            if hasattr(self, code) and isinstance(getattr(self, code), collections.Callable):
                getattr(self, code)(*args, **kwargs)
            else:
                self.errout.send('ERROR', 'Got an unknown code: %s ' % str(code))
        #self.checkResults()
