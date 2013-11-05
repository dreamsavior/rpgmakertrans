'''
Created on 15 Aug 2013

@author: habisain
'''

from metamanager import CustomManager, MetaCustomManager

class TranslatorManager(CustomManager): pass
class TranslatorMeta(MetaCustomManager): customManagerClass = TranslatorManager

class Translator(object, metaclass=TranslatorMeta):
    def __init__(self, mtime, *args, **kwargs):
        self.mtime = mtime
        
    def updateMTime(self, newmtime):
        self.mtime = max(self.mtime, newmtime)
        
    def getMTime(self):
        return self.mtime