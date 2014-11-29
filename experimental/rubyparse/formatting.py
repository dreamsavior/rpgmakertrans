"""
escaping
********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

FormatRule class and Formatted rules (eventually)
"""

from .simple import SimpleRule
from .base import Translateable
from .successor import FormatSuccessor, FormatBaseSuccessor

    
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
        if not self.gotString: 
            super().getSuccessorRule(parser)
        else:
            return self.matchSuccessors(FormatSuccessor, parser)
        
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

class DoubleQuote(FormatRule, Translateable, metaclass=FormatBaseSuccessor):
    begins = '"'
    escapeRules = [r'\"', r'\\']
    terminator = '"'

class SingleQuote(FormatRule, Translateable, metaclass=FormatBaseSuccessor):
    begins = '\''
    escapeRules = [r"\'", r'\\']
    terminator = '\''

