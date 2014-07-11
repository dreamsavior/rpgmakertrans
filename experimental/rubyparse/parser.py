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
            for SimpleRule in ruleStack[-1].getSuccessorRules():
                result = SimpleRule.match(self)
                if result is not False:
                    ruleStack.append(SimpleRule(self))
                    self.index += result
                    break
            if ruleStack[-1].terminate(self):
                self.index += ruleStack[-1].advance(self)
                ruleStack.pop()
                if ruleStack:
                    ruleStack[-1].resume(self)
            else:
                self.index += ruleStack[-1].advance(self)
            
    

