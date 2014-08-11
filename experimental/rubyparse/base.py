"""
base
****

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Basic Rule class and Base rule
"""

from .successor import BaseSuccessor

class Rule:
    successorClass = None
    def __init__(self, parser):
        pass
    
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

class Translateable(Rule):
    focus = None
    
    def __init__(self, parser):
        if type(self).focus is None:
            self.beginsAt = parser.index
            type(self).focus = self
        super().__init__(parser)
        
    def exit(self, parser):
        if type(self).focus is self:
            parser.translationHandler.translate(parser.string[self.beginsAt:parser.index])
            type(self).focus = None
        super().exit(parser)
        
class Base(Rule):
    successorClass = BaseSuccessor
            
    def terminate(self, parser):
        return parser.index >= len(parser.string)
    