"""
customdelimiters
****************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Custom Delimiter based strings
"""

from .base import Rule
from .simple import SimpleRule
from .successor import FormatSuccessor, BaseSuccessor

class RubyVar(Rule, metaclass = FormatSuccessor):
    """Hackish Ruby variable detector - just an alphanumeric string. 
    It would also work for string literals.
    TODO: It needs to handle attributes (prefixed @) and any other non
    alphanumeric prefixes."""
    def __init__(self, parser):
        super().__init__(parser)
        self.gotAl = False
        self.terminated = False
    
    @classmethod
    def match(cls, parser):
        char = parser.string[parser.index]
        return char in '@$' or char.isalnum()
    
    def advance(self, parser):
        return 0 if self.terminated else 1
        
    def terminate(self, parser):
        char = parser.string[parser.index]
        if not self.gotAl and (char == '@' or char == '$'):
            return False
        elif char.isalnum():
            self.gotAl = True
            return False
        else:
            self.terminated = True
            return True
        
class HereDocError(Exception): pass

class HereDoc(Rule, metaclass = BaseSuccessor):
    """Heredocs are not supported in this version of the Ruby parser. The
    current behaviour is to flat out refuse to do anything to a document
    containing a Heredoc"""
    def __init__(self, parser):
        raise HereDocError('Cannot parse heredoc')
     
    @classmethod
    def match(cls, parser):
        if parser.string.startswith('<<', parser.index):
            char = parser.string[parser.index + 2]
            if char == '-' or char.isalpha():
                return 0
            else:
                return False
        else:
            return False

class CustomDelimiter(SimpleRule):
    def __init__(self, parser):
        self.delimiter = parser.string[parser.index]
        parser.index += 1
        
    def terminator(self, parser):
        if parser.string.startswith(self.delimiter, parser.index):
            return True
        else:
            return False

class CustomSingleQuoteString(CustomDelimiter):
    pass

class CustomDoubleQuoteString(CustomDelimiter):
    pass

class CustomRegex(CustomDelimiter):
    pass
