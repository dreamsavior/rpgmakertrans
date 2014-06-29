"""
parser
******

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Implementation of the Ruby Parser.
"""

from .rules import Base

class DummyTranslator:
    def translate(self, string):
        print(string)
        
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
            if ruleStack[-1].terminate(self):
                self.index += ruleStack[-1].advance(self)
                ruleStack.pop()
            else:
                self.index += ruleStack[-1].advance(self)
            
    

if __name__ == '__main__':
    RubyParser('x = "abc"', DummyTranslator())     
