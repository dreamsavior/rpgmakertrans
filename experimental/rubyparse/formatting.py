"""
escaping
********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

FormatRule class and Formatted rules (eventually)
"""
from collections import defaultdict

from .simple import SimpleRule
from .base import Rule, Base

class FormatRule(SimpleRule):
    """Must go to terminal character, check to see if % is after string, and if so consume the next thing."""
    formatSuccessors = defaultdict(set)
    @classmethod
    def addFormatSuccessor(cls, succ):
        cls.formatSuccessors[cls].add(succ)
        return succ
        
    def __init__(self, parser):
        self.gotString = False
        self.gotFormat = False
        
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
            for PotentialSuccessor in FormatRule.formatSuccessors[type(self)]:
                result = PotentialSuccessor.match(parser)
                if result is not False:
                    parser.index += result
                    parser.ruleStack.append(PotentialSuccessor(parser))
                    return        
        
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
    It would also work for string literals."""
    def terminate(self, parser):
        return parser.string[parser.index].isalnum()

@Base.addSuccessorRule
class DoubleQuote(FormatRule):
    begins = '"'
    escapeRules = [r'\"']
    terminator = '"'
DoubleQuote.addFormatSuccessor(DoubleQuote)

@DoubleQuote.addFormatSuccessor
@Base.addSuccessorRule
class SingleQuote(SimpleRule):
    begins = '\''
    escapeRules = [r"\'"]
    terminator = '\''
#SingleQuote.addFormatSuccessor(SingleQuote)
#SingleQuote.addFormatSuccessor(DoubleQuote)