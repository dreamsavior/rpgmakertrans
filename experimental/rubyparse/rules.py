"""
rules
*****

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Provides rules for the Ruby parser.
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
    
    def terminate(self, parser):
        raise NotImplementedError('Needs to be overridden')
    
    @classmethod
    def addSuccessorRule(cls, rule):
        SimpleRule.successorRules[cls].add(rule)
        return rule
    
    @classmethod
    def getSuccessorRules(cls):
        return Rule.successorRules[cls]

    
class SimpleRule(Rule):
    begins = ''
    escapeRules = []
    terminator = ''
      
    @classmethod
    def match(cls, parser):
        if parser.string.startswith(cls.begins, parser.index):
            return len(cls.begins)
        else:
            return False
    
    def advance(self, parser):
        for escape in type(self).escapeRules:
            if parser.string.startswith(escape, parser.index):
                return len(escape)
        else:
            return 1

    def terminate(self, parser):
        return parser.string.startswith(type(self).terminator, parser.index)
    

class Base(Rule):
    def __init__(self, parser):
        self.lastIndex = 0
        
    def advance(self, parser):
        self.lastIndex = parser.index
        return 1
    
    def resume(self, parser):
        parser.translationHandler.translate(parser.string[self.lastIndex + 1:parser.index])

    def terminate(self, parser):
        return parser.index >= len(parser.string)


@Base.addSuccessorRule
class DoubleQuote(SimpleRule):
    begins = '"'
    escapeRules = [r'\"']
    terminator = '"'

@Base.addSuccessorRule
class SingleQuote(SimpleRule):
    begins = '\''
    escapeRules = [r"\'"]
    terminator = '\''

@Base.addSuccessorRule
class Bracket(SimpleRule):
    begins = '('
    escapeRules = []
    terminator = ')'

@Base.addSuccessorRule
class Curly(SimpleRule):
    begins = '{'
    escapeRules = []
    terminator = '}'

@Base.addSuccessorRule
class Square(SimpleRule):
    begins = '['
    escapeRules = []
    terminator = ']'


class HereDoc(SimpleRule):
    begins = '-->'
    escapeRules = []

    def enter(self):
        pass

    def terminate(self, parser):
        pass


class HereDocLenient(SimpleRule):
    pass


class InnerCode(SimpleRule):
    begins = '#{'
    escapeRules = []
    terminator = '}'

