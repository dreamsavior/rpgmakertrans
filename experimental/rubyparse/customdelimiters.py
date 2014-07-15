'''
Created on 15 Jul 2014

@author: habisain
'''

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