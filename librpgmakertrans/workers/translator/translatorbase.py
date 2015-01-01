"""
translatorbase
**************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Specifies the shared methods/interfaces of the Translator.
"""

from ...metamanager import CustomManager, MetaCustomManager
from ...errorhook import ErrorMeta

class TranslatorError(Exception): pass

class TranslatorManager(CustomManager): pass

class TranslatorMeta(MetaCustomManager, ErrorMeta):
    customManagerClass = TranslatorManager


class Translator(metaclass=TranslatorMeta):

    def __init__(self, mtime, *args, **kwargs):
        self.mtime = mtime
        self.final = False

    def updateMTime(self, newmtime):
        self.mtime = max(self.mtime, newmtime)

    def getMTime(self):
        return self.mtime

    def translate(self, string, context):
        if self.final:
            raise TranslatorError('Cannot translate from finalised'
                                  'translator')
        return string

    def getPatchData(self):
        self.final = True
        return {}
