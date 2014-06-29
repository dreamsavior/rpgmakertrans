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
        
def parseRuby(string, translationHandler):
    index = 0
    ruleStack = [Base(translationHandler)]
    while ruleStack:
        for SimpleRule in ruleStack[-1].getSuccessorRules():
            result = SimpleRule.match(string, index)
            if result is not False:
                ruleStack.append(SimpleRule(string, index))
                index += result
        if ruleStack[-1].terminate(string, index):
            index += ruleStack[-1].advance(string, index)
            ruleStack.pop()
        else:
            index += ruleStack[-1].advance(string, index)

if __name__ == '__main__':
    parseRuby('x = "abc"', DummyTranslator())     
