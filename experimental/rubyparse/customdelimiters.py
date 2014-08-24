"""
customdelimiters
****************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Custom Delimiter based strings
"""

from .simple import SimpleRule
from .base import Rule
from .successor import FormatSuccessor

class RubyVar(Rule, metaclass = FormatSuccessor):
    """Hackish Ruby variable detector - just an alphanumeric string. 
    It would also work for string literals.
    TODO: It needs to handle attributes (prefixed @) and any other non
    alphanumeric prefixes."""
    def __init__(self, parser):
        super().__init__(parser)
        self.gotAl = False
    
    @classmethod
    def match(cls, parser):
        char = parser.string[parser.index]
        return char in '@$' or char.isalnum()
        
    def terminate(self, parser):
        char = parser.string[parser.index]
        if not self.gotAl and (char == '@' or char == '$'):
            return False
        elif char.isalnum():
            self.gotAl = True
            return False
        else:
            return True
        
class HereDoc(SimpleRule):
    begins = '-->'
    escapeRules = []

    def enter(self):
        pass

    def terminate(self, parser):
        pass
    
class CustomDelimiter(Rule):
    pass

class CustomSingleQuoteString(CustomDelimiter):
    pass

class CustomDoubleQuoteString(CustomDelimiter):
    pass

class CustomRegex(CustomDelimiter):
    pass

class HereDocLenient(SimpleRule):
    pass