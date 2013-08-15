'''
Created on 15 Aug 2013

@author: habisain
'''

from multiprocessing.managers import BaseManager

class TranslatorManagerClass(BaseManager):
    pass

TranslatorManager = TranslatorManagerClass()

class TranslatorMeta(type):
    def __init__(cls, a, b, c):
        super(TranslatorMeta, cls).__init__(a, b, c)
        TranslatorManager.register(cls, cls.__name__)
        
class Translator(object):
    pass