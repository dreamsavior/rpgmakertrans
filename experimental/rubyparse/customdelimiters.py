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

class HereDoc(SimpleRule):
    begins = '-->'
    escapeRules = []

    def enter(self):
        pass

    def terminate(self, parser):
        pass
    
class Regex(SimpleRule):
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