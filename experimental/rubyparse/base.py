"""
base
****

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Basic Rule class and Base rule
"""
from collections import defaultdict

class Rule:
    successorRules = defaultdict(set)
    
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
    def addSuccessorRule(cls, rule):
        Rule.successorRules[cls].add(rule)
        return rule
        
    @classmethod
    def getSuccessorRule(cls, parser):
        for PotentialSuccessor in Rule.successorRules[cls]:
            result = PotentialSuccessor.match(parser)
            if result is not False:
                parser.ruleStack.append(PotentialSuccessor(parser))
                parser.index += result
                return

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
    
    def terminate(self, parser):
        return parser.index >= len(parser.string)
    