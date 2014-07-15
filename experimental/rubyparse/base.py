'''
Created on 15 Jul 2014

@author: habisain
'''
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
                parser.index += result
                parser.ruleStack.append(PotentialSuccessor(parser))
                return

class Base(Rule):
    def __init__(self, parser):
        super().__init__(parser)
        self.lastIndex = 0
        
    def advance(self, parser):
        self.lastIndex = parser.index
        return 1
    
    def resume(self, parser):
        parser.translationHandler.translate(parser.string[self.lastIndex + 1:parser.index])

    def terminate(self, parser):
        return parser.index >= len(parser.string)