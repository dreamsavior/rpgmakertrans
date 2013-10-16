'''
Created on 21 Aug 2013

@author: habisain
'''

from multiprocessing.managers import BaseManager

class SenderManager(BaseManager):
    pass

class Sender(object):
    def __init__(self):
        self.__signals = []
    
    def send(self, signal, *args, **kwargs):
        self.__signals.append((signal, args, kwargs))
        
    def get(self):
        ret = self.__signals
        self.__signals = []
        return ret 
    
    def __getattr__(self, key):
        def wrap(self, *args, **kwargs):
            self.send(key, *args, **kwargs)
        wrap.__name__ = 'send%s' % key
        self.key = wrap
        return self.key
    
SenderManager.register('Sender', Sender)
    
    
        