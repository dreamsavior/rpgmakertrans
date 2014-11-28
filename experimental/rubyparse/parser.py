"""
parser
******

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Implementation of the Ruby Parser.
"""

from .rules import Base


class RubyParserState:
    def __init__(self, string, translationHandler, index, ruleStack, verbose = False):
        self.string = string
        self.translationHandler = translationHandler
        self.__index = index
        self.ruleStack = ruleStack
        self.verbose = verbose
        
    def __str__(self):
        return ('RubyParserState(string=..%s.., index=%s, ruleStack=%s)' % 
                (self.string[max(0, self.index-2):min(self.index+3, len(self.string))], 
                 self.index, [type(rule).__name__ for rule in self.ruleStack]))
    
    @property
    def index(self):
        return self.__index
    
    @index.setter
    def index(self, newindex):
        adv = newindex - self.__index
        for _ in range(adv):
            self.__index += 1
            if self.verbose:
                print(self.__index, self.ruleStack[-1])
        assert self.__index == newindex
        
    @property
    def currentRule(self):
        if self.ruleStack:
            return self.ruleStack[-1]
        else:
            return None
                  
    def startswith(self, substring, index = None):
        if index is None:
            index = self.__index
        return self.string.startswith(substring, index)
                    
    def addRule(self, rule):
        if self.currentRule is not None:
            self.currentRule.unfocus(self)
        self.ruleStack.append(rule)
        
    def popRules(self):
        ruleFlux = True
        while ruleFlux and self.ruleStack:
            if self.currentRule.terminate(self):
                if self.verbose:
                    print('released %s at %s' % (type(self.currentRule).__name__, self.index))
                self.index += self.currentRule.advance(self)
                self.currentRule.exit(self)
                self.ruleStack.pop()
                if self.ruleStack:
                    self.currentRule.resume(self)
            else:
                self.index += self.currentRule.advance(self)
                ruleFlux = False

class RubyParserException(Exception): pass

def parseRuby(string, translationHandler, verbose = False):
    state = RubyParserState(string, translationHandler, 0, [], verbose)
    state.addRule(Base(state))

    while state.ruleStack:
        if state.index > len(state.string):
            raise RubyParserException('String out of bounds: %s' % state)
        result = state.currentRule.getSuccessorRule(state)
        while result is not None:
            if verbose:
                print('got %s at %s' % (type(result[1]).__name__, state.index))
            state.index += result[0]
            state.addRule(result[1])
            result = state.currentRule.getSuccessorRule(state)
        
        state.popRules()
        
            

