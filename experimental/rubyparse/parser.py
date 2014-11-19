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
    def __init__(self, string, translationHandler, index, ruleStack):
        self.string = string
        self.translationHandler = translationHandler
        self.index = index
        self.ruleStack = ruleStack
        
    def __str__(self):
        return ('RubyParserState(string=..%s.., index=%s, ruleStack=%s)' % 
                (self.string[max(0, self.index-2):min(self.index+3, len(self.string))], 
                 self.index, [type(rule).__name__ for rule in self.ruleStack]))

class RubyParserException(Exception): pass

def parseRuby(string, translationHandler, verbose = False):
    state = RubyParserState(string, translationHandler, 0, [])
    state.ruleStack.append(Base(state))

    while state.ruleStack:
        if state.index > len(state.string):
            raise RubyParserException('String out of bounds')
        result = state.ruleStack[-1].getSuccessorRule(state)
        while result is not None:
            if verbose:
                print('got %s at %s' % (type(result[1]).__name__, state.index))
            state.index += result[0]
            state.ruleStack.append(result[1])
            result = state.ruleStack[-1].getSuccessorRule(state)
            
        ruleFlux = True
        while ruleFlux and state.ruleStack:
            if state.ruleStack[-1].terminate(state):
                if verbose:
                    print('released %s at %s' % (type(state.ruleStack[-1]).__name__, state.index))
                state.index += state.ruleStack[-1].advance(state)
                state.ruleStack[-1].exit(state)
                state.ruleStack.pop()
                if state.ruleStack:
                    state.ruleStack[-1].resume(state)
            else:
                state.index += state.ruleStack[-1].advance(state)
                ruleFlux = False
            

