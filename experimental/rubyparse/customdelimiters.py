"""
customdelimiters
****************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Custom Delimiter based strings
"""

from .base import Rule, StatementContainer, Translateable
from .simple import SimpleRule
from .successor import BaseSuccessor, AllCodeSuccessor, EmbeddedCodeSuccessor

class RubyVar(Rule, metaclass = AllCodeSuccessor):
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
        char = parser.currentChar
        return 0 if char and (char in '@$' or char.isalnum()) else False
    
    def advance(self, parser):
        return 0 if self.terminated else 1
        
    def terminate(self, parser):
        char = parser.currentChar
        if not self.gotAl and (char == '@' or char == '$'):
            return False
        elif char.isalnum():
            self.gotAl = True
            return False
        else:
            self.terminated = True
            return True
        
class RubyKeyword(Rule, metaclass = AllCodeSuccessor):
    """Catch all for Ruby Keywords - these have the property that they should
    *reset* their parents statement detection"""
    keywords = ['if'] # TODO: Populate this list
    
    @classmethod
    def match(cls, parser):
        for keyword in cls.keywords:
            if parser.startswith(keyword):
                return len(keyword)
        return False
    
    def terminate(self, parser):
        return True
    
    def exit(self, parser):
        if isinstance(parser.currentRule, StatementContainer):
            parser.currentRule.statementSeen = False
        return super().exit(parser)
        
class HereDocError(Exception): pass

class HereDoc(Rule, metaclass = BaseSuccessor):
    """Heredocs are not supported in this version of the Ruby parser. The
    current behaviour is to flat out refuse to do anything to a document
    containing a Heredoc"""
    def __init__(self, parser):
        raise HereDocError('Cannot parse heredoc')
     
    @classmethod
    def match(cls, parser):
        if parser.startswith('<<'):
            char = parser.string[parser.index + 2]
            if char == '-' or char.isalpha():
                return 0
            else:
                return False
        else:
            return False

class CustomDelimiter(SimpleRule):
    brackets = {'(':')', '{':'}', '[':']'}
    escapes = [r'\\']
    def __init__(self, parser):
        super().__init__(parser)
        self.delimiter = parser[2]
        parser.index += 1
        
    @property
    def delimiter(self):
        return self.__delimiter
    
    @delimiter.setter
    def delimiter(self, newdelimiter):
        self.__delimiter = type(self).brackets.get(newdelimiter, newdelimiter)
            
    def advance(self, parser):
        if parser.startswith(r'\%s' % self.delimiter):
            return 2
        else:
            return super().advance(parser)
        
    def terminate(self, parser):
        if self.delimiter and parser.string.startswith(self.delimiter, parser.index):
            return True
        else:
            return False

class CustomSingleQuoteString(CustomDelimiter, Translateable, metaclass=AllCodeSuccessor):
    begins = '%q'

class CustomDoubleQuoteString(CustomDelimiter, Translateable, metaclass=AllCodeSuccessor):
    successorClass = EmbeddedCodeSuccessor
    begins = '%Q'

class CustomRegex(CustomDelimiter, Translateable, metaclass=AllCodeSuccessor):
    successorClass = EmbeddedCodeSuccessor
    begins = '%r'
    
class WordSQArray(CustomDelimiter, Translateable, metaclass=AllCodeSuccessor):
    begins = '%w'
    
class WordDQArray(CustomDelimiter, Translateable, metaclass=AllCodeSuccessor):
    successorClass = EmbeddedCodeSuccessor
    begins = '%Q'

class CustomBacktick(CustomDelimiter, metaclass=AllCodeSuccessor):
    successorClass = EmbeddedCodeSuccessor
    begins = '%x'
    
class CustomSymbols(CustomDelimiter, Translateable, metaclass=AllCodeSuccessor):
    begins = '%s'