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
    
    def __init__(self, string, index):
        pass
    
    @classmethod
    def match(cls, string, index):
        raise NotImplementedError('Needs to be overridden')
    
    def advance(self, string, index):
        return 1
    
    def terminate(self, string, index):
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
    def match(cls, string, index):
        if string.startswith(cls.begins, index):
            return len(cls.begins)
        else:
            return False
    
    def advance(self, string, index):
        for escape in type(self).escapeRules:
            if string.startswith(escape, index):
                return len(escape)
        else:
            return 1

    def terminate(self, string, index):
        return string.startswith(type(self).terminator, index)
    

class Base(Rule):
    def __init__(self, translationHandler):
        self.translationHandler = translationHandler
        self.lastIndex = 0
        
    def advance(self, string, index):
        if index != self.lastIndex + 1:
            self.translationHandler.translate(string[self.lastIndex + 1:index])
        self.lastIndex = index
        return 1

    def terminate(self, string, index):
        return index >= len(string)


@Base.addSuccessorRule
class DoubleQuote(SimpleRule):
    begins = '"'
    escapeRules = ['\"']
    terminator = '"'

@Base.addSuccessorRule
class SingleQuote(SimpleRule):
    begins = '\''
    escapeRules = []
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

