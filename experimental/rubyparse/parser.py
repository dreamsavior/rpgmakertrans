"""
parser
******

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Implementation of the Ruby Parser.
"""

from .rules import Base
from .base import Translateable
from .scripttranslator import ScriptTranslator


class RubyParserState:
    def __init__(self, string, filename, scriptTranslator, index, ruleStack, verbose = False):
        self.string = string
        self.filename = filename
        self.scriptTranslator = scriptTranslator
        self.__index = index
        self.ruleStack = ruleStack
        self.verbose = verbose
        self.rollbacks = {}
        self.currentRollBack = None
        self.failed = False
        self.char = 1
        self.line = 1
        
    def __str__(self):
        return ('RubyParserState(string=..%s.., index=%s, ruleStack=%s)' % 
                (repr(self.string[max(0, self.index-2):min(self.index+3, len(self.string))]), 
                 self.index, [str(rule) for rule in self.ruleStack]))
        
    def __getitem__(self, indx):
        if isinstance(indx, slice):
            if slice.start is not None and slice.start < 0: raise ValueError('No negative slices')
            if slice.stop is not None and slice.stop < 0: raise ValueError('No negative slices')
            if slice.step is not None and slice.step != 1: raise ValueError('No stepped slices')
            start = slice.start + self.__index if slice.start is not None else slice.start
            stop = slice.stop + self.__index if slice.stop is not None else slice.stop
            return self.string[slice(start, stop, 1)]
        else:
            if indx < 0: raise ValueError('No negative indices')
            return self.string[self.__index+indx:self.__index+indx+1]
        
    def setRollback(self):
        self.rollbacks[self.__index] = (self.__index, self.ruleStack[:], self.char, self.line)
        
    def resumeRollback(self):
        if self.rollbacks:
            rollback = max(self.rollbacks)
            if self.verbose:
                print('Failure, resuming at %s' % self.rollbacks[rollback][0])
            self.__index, self.ruleStack, self.char, self.line = self.rollbacks.pop(rollback)
            if Translateable.focus not in self.ruleStack:
                Translateable.focus = None
            self.currentRollBack = self.__index
            self.failed = False
            self.scriptTranslator.rollback(self.__index)
            return True
        else:
            return False
    
    @property
    def index(self):
        return self.__index
    
    @property
    def rolledBack(self):
        return self.__index == self.currentRollBack
    
    @index.setter
    def index(self, newindex):
        adv = newindex - self.__index
        for _ in range(adv):
            self.char += 1
            if self.currentChar == '\n':
                self.line += 1
                self.char = 1
            self.__index += 1
            if self.verbose:
                print(adv, self)
        assert self.__index == newindex
        
    @property
    def currentRule(self):
        if self.ruleStack:
            return self.ruleStack[-1]
        else:
            return None
    
    @property
    def currentChar(self):
        if self.__index < len(self.string):
            return self.string[self.__index]
        else:
            return ''
                  
    def startswith(self, substring, index = None):
        if index is None:
            index = self.__index
        return self.string.startswith(substring, index)
                    
    def addRule(self, rule):
        self.ruleStack.append(rule)
        
    def checkNextRule(self):
        result = self.currentRule.getSuccessorRule(self)
        while result is not None:
            if self.verbose:
                print('got %s at %s' % (type(result[1]).__name__, self.index))
            self.index += result[0]
            self.addRule(result[1])
            result = self.currentRule.getSuccessorRule(self)
            
    def popRules(self):
        ruleFlux = True
        ruleTerminated = False
        while ruleFlux and self.ruleStack:
            if self.currentRule.terminate(self):
                if self.verbose:
                    print('released %s at %s' % (type(self.currentRule).__name__, self.index))
                self.index += self.currentRule.advance(self)
                self.currentRule.exit(self)
                self.ruleStack.pop()
                if self.ruleStack:
                    self.currentRule.resume(self)
                ruleTerminated = True
            else:
                ruleFlux = False
        if not ruleTerminated:
            self.index += self.currentRule.advance(self)

class RubyParserException(Exception): pass

def translateRuby(string, translationHandler, filename = '', verbose = False):
    scriptTranslator = ScriptTranslator(string, translationHandler)
    state = RubyParserState(string, filename, scriptTranslator, 0, [], verbose)
    state.addRule(Base(state))

    while state.ruleStack:
        if state.index > len(state.string):
            if not state.resumeRollback():
                raise RubyParserException('String out of bounds: %s' % state)
        if state.failed:
            if not state.resumeRollback():
                raise RubyParserException('Entered failed state: %s' % state)
        state.checkNextRule()
        state.popRules()
        
    scriptTranslator.translate()
    