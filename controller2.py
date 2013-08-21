import time

from multiprocessing import Manager, Pool, freeze_support
from multiprocessing.managers import BaseManager
from errorhook import testExcept, setErrorOut
from ui.qtui import startView
from ui.qterror import errorMsg
from sender import SenderManager

class Controller(object):
    def __init__(self):
        self.manager = Manager()
        self.senderManager = SenderManager()
        self.senderManager.start()
        self.sendin = self.senderManager.Sender()
        self.sendout = self.senderManager.Sender()
        self.sendout.send('toggleUI', True)
        self.uiworker = Pool(processes=1, initializer=setErrorOut, initargs=[self.sendin])
        self.uiworker.apply_async(startView, [self.sendout, self.sendin])
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
            events = self.sendin.get() 
            while events:
                code, args, kwargs = events.pop(0)
                if code in self.actions:
                    self.actions[code](*args, **kwargs)
                else:
                    print 'Got an unknown UI code'
                    print code, args, kwargs
            time.sleep(0.1)
        
if __name__ == '__main__':
    freeze_support()
    x = Controller()
    x.main()