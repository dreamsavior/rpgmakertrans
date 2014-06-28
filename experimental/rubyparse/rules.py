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
    def addContextRule(cls, rule):
        SimpleRule.successorRules[cls].add(rule)
    
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

    def terminate(self, string, index):
        return index >= len(string)


class DoubleQuote(SimpleRule):
    begins = '"'
    escapeRules = ['\"']
    terminator = '"'

Base.addContextRule(DoubleQuote)

class SingleQuote(SimpleRule):
    begins = '\''
    escapeRules = []
    terminator = '\''


class Bracket(SimpleRule):
    begins = '('
    escapeRules = []
    terminator = ')'


class Curly(SimpleRule):
    begins = '{'
    escapeRules = []
    terminator = '}'


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


class InnerCode(Base):
    begins = '#{'
    escapeRules = []
    terminator = '}'

