"""
escaping
********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

FormatRule class and Formatted rules (eventually)
"""

from .simple import SimpleRule
from .base import Rule, Base, Translateable

class FormatSuccessor(type):
    formatSuccessors = set()
    def __init__(cls, name, bases, nmspc):
        super().__init__(name, bases, nmspc)
        type(cls).formatSuccessors.add(cls)
    
class FormatRule(SimpleRule):
    """Must go to terminal character, check to see if % is after string, and if so consume the next thing."""
        
    def __init__(self, parser):
        self.gotString = False
        self.gotFormat = False
        super().__init__(parser)
        
    def advance(self, parser):
        if not self.gotString:
            return super().advance(parser)
        elif self.gotFormat:
            return 0
        else:
            return 1
        
    def getSuccessorRule(self, parser):
        if not self.gotString: super().getSuccessorRule(parser)
        else:
            for PotentialSuccessor in FormatSuccessor.formatSuccessors:
                result = PotentialSuccessor.match(parser)
                if result is not False:
                    return result, PotentialSuccessor(parser)
                        
    def resume(self, parser):
        if self.gotString:
            self.gotFormat = True
    
    def terminate(self, parser):
        if not self.gotString:
            normalTerminate = super().terminate(parser)
            if normalTerminate:
                if parser.string[parser.index+len(self.terminator):].strip().startswith('%'):
                    self.gotString = True
                    return False
                else:
                    return True
        else:
            return self.gotFormat


class RubyVar(Rule):
    """Hackish Ruby variable detector - just an alphanumeric string. 
    It would also work for string literals.
    TODO: It needs to handle attributes (prefixed @) and any other non
    alphanumeric prefixes."""
    def terminate(self, parser):
        return parser.string[parser.index].isalnum()

@Base.addSuccessorRule
class DoubleQuote(FormatRule, Translateable, metaclass=FormatSuccessor):
    begins = '"'
    escapeRules = [r'\"']
    terminator = '"'

@Base.addSuccessorRule
class SingleQuote(FormatRule, Translateable, metaclass=FormatSuccessor):
    begins = '\''
    escapeRules = [r"\'"]
    terminator = '\''

