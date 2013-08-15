import time

from multiprocessing import Manager, Pool, freeze_support
from errorhook import testExcept, setErrorOut
from ui.qtui import startView
from ui.qterror import errorMsg

class Controller(object):
    def __init__(self):
        self.manager = Manager()
        self.comsin, self.comsout = self.manager.list(), self.manager.list()
        self.comsout.append(['toggleUI', [True]])
        self.uiworker = Pool(processes=1, initializer=setErrorOut, initargs=[self.comsin])
        self.uiworker.apply_async(startView, [self.comsout, self.comsin])
        self.uiworker.close()
        self.workers = [self.uiworker]
        self.going = False
        
        self.actions = {'KILL': self.kill,
                        'ERROR': self.error,}
        
    def kill(self):
        self.going = False
        for workers in self.workers:
            workers.terminate()
            
    def error(self, exString):
        self.kill()
        errorMsg(exString)
        
    def main(self):
        self.going = True
        while self.going:
            while self.comsin:
                code, params = self.comsin.pop(0)
                if code in self.actions:
                    self.actions[code](*params)
                else:
                    print 'Got an unknown UI code'
                    print code, params
        
if __name__ == '__main__':
    freeze_support()
    x = Controller()
    x.main()