'''
Created on 15 Jul 2014

@author: habisain
'''

from .simple import SimpleRule
from .base import Rule, Base

class EscapingRule(SimpleRule):
    """Must go to terminal character, check to see if % is after string, and if so consume the next thing."""
    def advance(self, parser):
        pass
    
    def terminate(self, parser):
        pass


class RubyVar(Rule):
    """Hackish Ruby variable detector - just an alphanumeric string. 
    It would also work for string literals."""
    def terminate(self, parser):
        return parser.string[parser.index].isalnum()

@Base.addSuccessorRule
class DoubleQuote(SimpleRule):
    begins = '"'
    escapeRules = [r'\"']
    terminator = '"'

@Base.addSuccessorRule
class SingleQuote(SimpleRule):
    begins = '\''
    escapeRules = [r"\'"]
    terminator = '\''
