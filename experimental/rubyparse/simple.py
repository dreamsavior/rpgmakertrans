'''
Created on 15 Jul 2014

@author: habisain
'''
from .base import Rule, Base

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

class InnerCode(SimpleRule):
    begins = '#{'
    escapeRules = []
    terminator = '}'
