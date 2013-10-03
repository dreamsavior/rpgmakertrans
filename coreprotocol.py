'''
Created on 20 Sep 2013

@author: habisain
'''

import multiprocessing, time
from collections import defaultdict
from sender import SenderManager
from errorhook import setErrorOut

class CoreRunner(object):
    def __init__(self, runners):
        self.running = []
        for runner in runners:
            self.attach(runner)
    
    def attach(self, runner):
        self.running.append(runner)
        
    def detach(self, runner):
        if runner in self.running: self.running.remove(runner)
        
    def run(self):
        while self.running:
            detachments = []
            for runner in self.running:
                runner.update()
                if runner.finished():
                    detachments.append(runner)
            for runner in detachments:
                self.detach(runner)
            time.sleep(0.1)

class CoreProtocol(object):
    def __init__(self, comsout=None, errout=None):
        self.senderManager = SenderManager()
        self.senderManager.start()
        self.coms = self.senderManager.Sender()
        if comsout is None: comsout = self.senderManager.Sender()
        self.comsout = comsout
        self.waiting = defaultdict(list)
        self.dispatched = set()
        self.pools = defaultdict(lambda: multiprocessing.Pool(initializer=setErrorOut, initargs=[errout]))
        self.results = []
        self.going = True
        self.localWaiting = defaultdict(list)
        
    def finished(self):
        return not self.going
        
    def reset(self): 
        for pool in self.pools: pool.join()
        self.pools.clear()
        
    def waitUntil(self, signal, pool, fn, *args, **kwargs):
        if signal in self.dispatched: self.submit(pool, fn, *args, **kwargs)
        else: self.waiting[signal].append((pool, fn, args, kwargs))
        
    def localWaitUntil(self, signal, fn, *args, **kwargs):
        if signal in self.dispatched: fn(*args, **kwargs)
        else: self.localWaiting[signal].append((fn, args, kwargs))
        
    def submit(self, pool, fn, *args, **kwargs):
        if 'comsout' in args:
            args = list(args)
            args[args.index('comsout')] = self.coms
        else:
            for (key, value) in kwargs.items():
                if value == 'comsout':
                    kwargs[key] = self.coms
        ret = self.pools[pool].apply_async(fn, args=args, kwds=kwargs)
        self.results.append(ret)
        return ret
        
    def trigger(self, signal):
        self.dispatched.add(signal)
        for pool, fn, args, kwargs in self.waiting[signal]:
            self.submit(pool, fn, *args, **kwargs)
        for fn, args, kwargs in self.localWaiting[signal]:
            fn(*args, **kwargs)
            
    def shutdown(self):
        for ret in self.results: ret.get
        for pool in self.pools.values(): pool.join()
        
    def terminate(self):
        for pool in self.pools.values(): pool.terminate()
                    
    def update(self):
        events = self.coms.get()
        while events:
            code, args, kwargs = events.pop(0)
            if hasattr(self, code) and callable(getattr(self, code)):
                getattr(self, code)(*args, **kwargs)
            else:
                print 'Got an unknown code'
                print code, args, kwargs
