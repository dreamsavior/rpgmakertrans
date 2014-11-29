"""
simple
******

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

SimpleRule class and simple rules
"""
from .base import Rule, Translateable, BaseSuccessor, StatementContainer
from .successor import FormatBaseSuccessor, AllCodeSuccessor

class SimpleRule(Rule):
    begins = ''
    escapeRules = []
    terminator = ''
      
    @classmethod
    def match(cls, parser):
        if parser.startswith(cls.begins):
            return len(cls.begins)
        else:
            return False
    
    def advance(self, parser):
        for escape in type(self).escapeRules:
            if parser.startswith(escape):
                return len(escape)
        else:
            return 1

    def terminate(self, parser):
        return parser.startswith(type(self).terminator)
    
class SimpleCode(SimpleRule):
    successorClass = AllCodeSuccessor

class Comment(SimpleRule, metaclass = AllCodeSuccessor):
    begins = '#'
    escapeRules = []
    terminator = '\n'
    
class Bracket(SimpleCode, StatementContainer, metaclass = FormatBaseSuccessor):
    statementSeperators = [','] 
    begins = '('
    escapeRules = []
    terminator = ')'

class Curly(SimpleRule, StatementContainer, metaclass = FormatBaseSuccessor):
    statementSeperators = [',', '=>']
    begins = '{'
    escapeRules = []
    terminator = '}'

class Square(SimpleRule, StatementContainer, metaclass = FormatBaseSuccessor):
    statementSeperators = [',']
    begins = '['
    escapeRules = []
    terminator = ']'

class InnerCode(SimpleRule):
    successorClass = BaseSuccessor
    
    begins = '#{'
    escapeRules = []
    terminator = '}'

class Regex(SimpleRule, Translateable, metaclass = BaseSuccessor):
    escapeRules = ['\/']
    terminator = '/'
    
    @classmethod
    def match(cls, parser):
        if parser.startswith('/'):
            if parser[1] in ' =': # These always mean division
                return False
            elif parser.rolledBack: # We tried a regex and it broke everything
                return False
            else:
                parser.setRollback()
                return 1
        else:
            return False