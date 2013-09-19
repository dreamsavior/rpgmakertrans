import time
from patchers import getPatcher
from filecopier2 import copyfiles
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
from sender import SenderManager
from collections import defaultdict
from twokpatcher import process2kgame

class Headless(object):
    def __init__(self):
        self.senderManager = SenderManager()
        self.senderManager.start()
        self.manager = multiprocessing.Manager()
        self.coms = self.senderManager.Sender()
        self.mtimes = self.manager.dict()
        self.newmtimes = self.manager.dict()
        self.waiting = defaultdict(list)
        self.dispatched = set()
        self.pools = defaultdict(ProcessPoolExecutor)
        self.results = []
        self.going = True
        self.actions = {'trigger': self.trigger, 'setProgress': self.setProgress, 
                        'submit': self.submit, 'waitUntil': self.waitUntil,
                        'setProgressDiv': self.setProgressDiv, 'incProgress': self.incProgress}
        self.progress = {'copying': [0, 1], 'patching': [0, 1], 'patchdata': [0, 1]}
        
    def setProgressDiv(self, key, div):
        self.progress[key][1] = div
        
    def setProgress(self, key, progress):
        self.progress[key][0] = progress
        #print self.progress
        if all((self.progress[0] == self.progress[1] for x in self.progress)):
            self.going = False
            
    def incProgress(self, key):
        self.progress[key][0] += 1
        #print self.progress
        if all((self.progress[x][0] == self.progress[x][1] for x in self.progress)):
            self.going = False
        
    def waitUntil(self, signal, pool, fn, *args, **kwargs):
        if signal in self.dispatched: self.submit(pool, fn, *args, **kwargs)
        else: self.waiting[signal].append((pool, fn, args, kwargs))
        
    def submit(self, pool, fn, *args, **kwargs):
        if 'comsout' in args:
            args = list(args)
            args[args.index('comsout')] = self.coms
        else:
            for (key, value) in kwargs.items():
                if value == 'comsout':
                    kwargs[key] = self.coms
        future = self.pools[pool].submit(fn, *args, **kwargs)
        self.results.append(future)
        return future
        
    def trigger(self, signal):
        self.dispatched.add(signal)
        for pool, fn, args, kwargs in self.waiting[signal]:
            self.submit(pool, fn, *args, **kwargs)
            
    def shutdown(self):
        for future in self.results: future.result()
        for pool in self.pools.values(): pool.shutdown()     
            
    def run(self, indir, patchpath, outdir):
        patcher = getPatcher(patchpath, self.coms)
        translator = patcher.makeTranslator()
        dontcopy = patcher.getAssetNames()
        self.submit('copier', copyfiles, indir=indir, outdir=outdir,
              ignoredirs=[], ignoreexts=['.lmu', '.ldb', '.lsd'], ignorefiles= dontcopy, 
              comsout=self.coms, translator=translator, mtimes=self.mtimes, 
              newmtimes=self.newmtimes, progresssig='copying', dirssig='dirsCopied')
        self.submit('patcher', process2kgame, indir, outdir, translator, 
                mtimes=self.mtimes, newmtimes=self.newmtimes, comsout=self.coms)
        patcher.doFullPatches(outdir, translator, self.mtimes, self.newmtimes)
        while self.going:
            events = self.coms.get()
            while events:
                code, args, kwargs = events.pop(0)
                if code in self.actions:
                    self.actions[code](*args, **kwargs)
                else:
                    print 'Got an unknown code'
                    print code, args, kwargs
            time.sleep(0.1)
        patcher.writeTranslator(translator, path=patchpath + '_2')
                
    
    

if __name__ == '__main__':
    indir = '/home/habisain/tr/cr'
    patchpath = '/home/habisain/tr/cr_p'
    outdir = '/home/habisain/tr/cr_t'
    x = Headless()
    x.run(indir, patchpath, outdir)
    