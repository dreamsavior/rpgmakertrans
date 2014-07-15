"""
parser
******

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Implementation of the Ruby Parser.
"""

from .rules import Base



class RubyParser:
    def __init__(self, string, translationHandler):
        self.string = string
        self.translationHandler = translationHandler
        self.index = 0
        self.ruleStack = [Base(self)] 
        while self.ruleStack:
            self.ruleStack[-1].getSuccessorRule(self)
            ruleFlux = True
            while ruleFlux and self.ruleStack:
                if self.ruleStack[-1].terminate(self):
                    self.index += self.ruleStack[-1].advance(self)
                    self.ruleStack.pop()
                    if self.ruleStack:
                        self.ruleStack[-1].resume(self)
                else:
                    self.index += self.ruleStack[-1].advance(self)
                    ruleFlux = False
            
    

