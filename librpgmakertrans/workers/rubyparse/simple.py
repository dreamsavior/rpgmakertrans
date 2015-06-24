"""
simple
******

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2015
:license: GNU Public License version 3

SimpleRule class and simple rules
"""
from collections import defaultdict

from .base import Rule, Translateable, BaseSuccessor
from .successor import FormatBaseSuccessor, AllCodeSuccessor, EmbeddedCodeSuccessor

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

    def terminate(self, parser):
        return parser.startswith('\n') or parser.index >= len(parser.string)

class BeginEndComment(SimpleRule, metaclass = AllCodeSuccessor):
    begins = '\n=begin'
    escapeRules = []
    terminator = '\n=end'

class Bracket(SimpleCode, metaclass = FormatBaseSuccessor):
    begins = '('
    escapeRules = []
    terminator = ')'

class Curly(SimpleCode, metaclass = FormatBaseSuccessor):
    begins = '{'
    escapeRules = []
    terminator = '}'

class Square(SimpleCode, metaclass = FormatBaseSuccessor):
    begins = '['
    escapeRules = []
    terminator = ']'

class Require(SimpleRule, metaclass = BaseSuccessor):
    begins = 'require'
    escapeRules = []

    def terminate(self, parser):
        return parser.startswith('\n') or parser.startswith(';')

class Backtick(SimpleRule, metaclass = BaseSuccessor):
    begins = '`'
    escapeRules = []
    terminator = '`'

class EmbeddedCode(SimpleRule, metaclass = EmbeddedCodeSuccessor):
    successorClass = BaseSuccessor

    begins = '#{'
    escapeRules = []
    terminator = '}'

class Regex(SimpleRule, Translateable, metaclass = BaseSuccessor):
    """Matching regexs is a little trickier as '/' is either a regex
    or division. So there are a few strategies: 1) If / is followed
    by ' ' or '=', its division. 2) Otherwise, assume it's a regex
    3) If we see a newline or run out of space, the parser fails and
    should resume assuming it's division. 4) Check to see that any
    unescaped brackets make sense in the context of RegEx syntax.
    This will ensure that strings such as (1/4) / 5 don't propogate
    an unmatched (, which is computationally super expensive. 

    Will this see false positives? Well, yes, but that can't be helped
    without a lot more work in parsing.    
    """
    successorClass = EmbeddedCodeSuccessor
    escapeRules = [r'\/', r'\\', r'\#']
    terminator = '/'
    
    matchBrackets = {'[': ']', '(': ')'}
    
    def __init__(self, parser):
        self.brackets = []
        self.escape = False
        self.bracketCounts = defaultdict(int)
        self.regexBegins = parser.index
        super().__init__(parser)

    def advance(self, parser):
        if parser.currentChar == '\n':
            parser.failed = True
        elif self.escape:
            self.escape = False
        elif parser.currentChar == '\\':
            self.escape = True
        elif self.brackets and parser.currentChar == self.brackets[-1]:
            self.brackets.pop()
        elif parser.currentChar in type(self).matchBrackets.values():
            parser.failed = True
        elif parser.currentChar in type(self).matchBrackets:
            self.brackets.append(type(self).matchBrackets[parser.currentChar])
        return super().advance(parser)

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
    
    def exit(self, parser):
        if self.brackets:
            parser.failed = True
        return super().exit(parser)