"""
base
****

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Basic Rule class and Base rule
"""

from .successor import BaseSuccessor
from collections import namedtuple

class Rule:
    successorClass = None
    def __init__(self, parser):
        pass
    
    def __str__(self):
        return type(self).__name__
    
    @classmethod
    def match(cls, parser):
        raise NotImplementedError('Needs to be overridden')
    
    def advance(self, parser):
        return 1
    
    def resume(self, parser):
        pass
    
    def exit(self, parser):
        pass
    
    def terminate(self, parser):
        raise NotImplementedError('Needs to be overridden')
        
    @classmethod
    def getSuccessorRule(cls, parser):
        if cls.successorClass is None:
            return None
        else:
            return Rule.matchSuccessors(cls.successorClass, parser)
    
    @staticmethod
    def matchSuccessors(cls, parser):
        for PotentialSuccessor in cls.get():
            result = PotentialSuccessor.match(parser)
            if result is not False:
                return result, PotentialSuccessor(parser)

TranslationData = namedtuple('TranslationData', ['begin', 'end', 'file', 'line', 'char'])

class Translateable(Rule):
    focus = None
    
    def __init__(self, parser):
        if Translateable.focus is None:
            self.beginsAt = parser.index
            self.char = parser.char
            self.line = parser.line
            Translateable.focus = self
        super().__init__(parser)
        
    def exit(self, parser):
        if Translateable.focus is self:
            translationData = TranslationData(self.beginsAt, parser.index, 
                                              parser.filename, self.line, self.char)
            parser.scriptTranslator.addIndicies(translationData)
            Translateable.focus = None
        super().exit(parser) 
            
class Base(Rule):
    statementSeperators = ['\n', ';']
    successorClass = BaseSuccessor
            
    def terminate(self, parser):
        return parser.index >= len(parser.string)
    
        