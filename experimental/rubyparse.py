'''
Created on 16 May 2014

@author: habisain
'''

"""
There are essentially two contexts: strings / non strings.
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
        
class RubyParser:
    def __init__(self):
        self.string = None
        self.index = None
        self.matchers = []
        self.escapeRules = []
    
    def parse(self, string):
        self.string = string
        self.index = 0
        while self.index < len(self.string):
            
            self.index += 1
        self.string = None
        self.index = None