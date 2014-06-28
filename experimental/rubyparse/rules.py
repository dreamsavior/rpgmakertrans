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
    begins = None
    escapeRules = None
    terminator = None
    successorRules = defaultdict(set)
    
    def __init__(self, string, index):
        pass
    
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

    def enter(self, string, index):
        pass

    def terminate(self, string, index):
        if type(self).terminator is None:
            raise NotImplementedError('Not implemented for this rule')
        else:
            return string[index] == type(self).terminator
    
    @classmethod
    def addContextRule(cls, rule):
        Rule.successorRules[cls].add(rule)
        
    @classmethod
    def getSuccessorRules(cls):
        return Rule.successorRules[cls]


class Base(Rule):
    begins = None
    escapeRules = []

    def terminate(self, string, index):
        return index >= len(string)


class DoubleQuote(Rule):
    begins = '"'
    escapeRules = ['\"']
    terminator = '"'

Base.addContextRule(DoubleQuote)

class SingleQuote(Rule):
    begins = '\''
    escapeRules = []
    terminator = '\''


class Bracket(Rule):
    begins = '('
    escapeRules = []
    terminator = ')'


class Curly(Rule):
    begins = '{'
    escapeRules = []
    terminator = '}'


class Square(Rule):
    begins = '['
    escapeRules = []
    terminator = ']'


class HereDoc(Rule):
    begins = '-->'
    escapeRules = []

    def enter(self):
        pass

    def terminate(self, parser):
        pass


class HereDocLenient(Rule):
    pass


class InnerCode(Base):
    begins = '#{'
    escapeRules = []
    terminator = '}'

