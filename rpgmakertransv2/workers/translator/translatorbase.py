"""
translatorbase
**************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Specifies the shared methods/interfaces of the Translator.
"""

from ...metamanager import CustomManager, MetaCustomManager

class TranslatorManager(CustomManager): pass
class TranslatorMeta(MetaCustomManager): customManagerClass = TranslatorManager

class Translator(object, metaclass=TranslatorMeta):
    def __init__(self, mtime, *args, **kwargs):
        self.mtime = mtime
        
    def updateMTime(self, newmtime):
        self.mtime = max(self.mtime, newmtime)
        
    def getMTime(self):
        return self.mtime