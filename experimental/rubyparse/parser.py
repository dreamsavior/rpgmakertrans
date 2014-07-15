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
        ruleStack = [Base(self)]
        while ruleStack:
            for Rule in ruleStack[-1].getSuccessorRules(): # TODO: Move inside Rule somehow. 
                result = Rule.match(self)
                if result is not False:
                    ruleStack.append(Rule(self))
                    self.index += result
                    break
            ruleFlux = True
            while ruleFlux and ruleStack:
                if ruleStack[-1].terminate(self):
                    self.index += ruleStack[-1].advance(self)
                    ruleStack.pop()
                    if ruleStack:
                        ruleStack[-1].resume(self)
                else:
                    self.index += ruleStack[-1].advance(self)
                    ruleFlux = False
            
    

