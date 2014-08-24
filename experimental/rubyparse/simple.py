"""
simple
******

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

SimpleRule class and simple rules
"""
from .base import Rule

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

class InnerCode(SimpleRule):
    begins = '#{'
    escapeRules = []
    terminator = '}'
