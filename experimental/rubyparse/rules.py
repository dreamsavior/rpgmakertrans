"""
rules
*****

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Provides rules for the Ruby parser.
"""


class Rule:
    begins = None
    escapeRules = None
    terminator = None

    def enter(self, parser):
        pass

    def terminate(self, parser):
        if type(self).terminator is None:
            raise NotImplementedError('Not implemented for this rule')
        else:
            return parser.string[parser.index] == type(self).terminator

    def addContextRule(self, rule):
        self.contextRules.add(rule)


class Base(Rule):
    begins = None
    escapeRules = []

    def terminate(self, parser):
        return parser.index >= len(parser.string)


class DoubleQuote(Rule):
    begins = '"'
    escapeRules = []
    terminator = '"'


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
