'''
Created on 15 Aug 2013

@author: habisain
'''

from multiprocessing.managers import BaseManager
from errorhook import ErrorMeta

class TranslatorManager(BaseManager):
    pass
    #def __init__(self):
    #    self.start()

class TranslatorMeta(ErrorMeta):
    def __init__(cls, a, b, c):
        super(TranslatorMeta, cls).__init__(a, b, c)
        TranslatorManager.register(cls.__name__, cls)
        
class Translator(object):
    __metaclass__ = TranslatorMeta
    def __init__(self, mtime, *args, **kwargs):
        self.mtime = mtime
        
    def updateMTime(self, newmtime):
        self.mtime = max(self.mtime, newmtime)
        
    def getMTime(self):
        return self.mtime