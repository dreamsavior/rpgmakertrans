'''
Created on 15 Aug 2013

@author: habisain
'''

from multiprocessing.managers import BaseManager

class TranslatorManager(BaseManager):
    def __init__(self):
        self.start()

class TranslatorMeta(type):
    def __init__(cls, a, b, c):
        super(TranslatorMeta, cls).__init__(a, b, c)
        global TRANSLATORS
        TranslatorManager.register(cls.__name__, cls)
        
class Translator(object):
    __metaclass__ = TranslatorMeta