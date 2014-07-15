"""
rules
*****

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Provides rules for the Ruby parser.
"""

from collections import defaultdict

class Rule:
    successorRules = defaultdict(set)
    
    def __init__(self, parser):
        pass
    
    @classmethod
    def match(cls, parser):
        raise NotImplementedError('Needs to be overridden')
    
    def advance(self, parser):
        return 1
    
    def resume(self, parser):
        pass
    
    def terminate(self, parser):
        raise NotImplementedError('Needs to be overridden')
    
    @classmethod
    def addSuccessorRule(cls, rule):
        SimpleRule.successorRules[cls].add(rule)
        return rule
        
    @classmethod
    def getSuccessorRule(cls, parser):
        for PotentialSuccessor in Rule.successorRules[cls]:
            result = PotentialSuccessor.match(parser)
            if result is not False:
                parser.index += result
                parser.ruleStack.append(PotentialSuccessor(parser))
                return

    
class SimpleRule(Rule):
    begins = ''
    escapeRules = []
    terminator = ''
      
    @classmethod
    def match(cls, parser):
        if parser.string.startswith(cls.begins, parser.index):
            return len(cls.begins)
        else:
            return False
    
    def advance(self, parser):
        for escape in type(self).escapeRules:
            if parser.string.startswith(escape, parser.index):
                return len(escape)
        else:
            return 1

    def terminate(self, parser):
        return parser.string.startswith(type(self).terminator, parser.index)
    

class Base(Rule):
    def __init__(self, parser):
        super().__init__(parser)
        self.lastIndex = 0
        
    def advance(self, parser):
        self.lastIndex = parser.index
        return 1
    
    def resume(self, parser):
        parser.translationHandler.translate(parser.string[self.lastIndex + 1:parser.index])

    def terminate(self, parser):
        return parser.index >= len(parser.string)

class EscapingRule(SimpleRule):
    """Must go to terminal character, check to see if % is after string, and if so consume the next thing."""
    def advance(self, parser):
        pass
    
    def terminate(self, parser):
        pass


class RubyVar(Rule):
    """Hackish Ruby variable detector - just an alphanumeric string. 
    It would also work for string literals."""
    def terminate(self, parser):
        return parser.string[parser.index].isalnum()

@Base.addSuccessorRule
class DoubleQuote(SimpleRule):
    begins = '"'
    escapeRules = [r'\"']
    terminator = '"'

@Base.addSuccessorRule
class SingleQuote(SimpleRule):
    begins = '\''
    escapeRules = [r"\'"]
    terminator = '\''

@Base.addSuccessorRule
class Bracket(SimpleRule):
    begins = '('
    escapeRules = []
    terminator = ')'

@Base.addSuccessorRule
class Curly(SimpleRule):
    begins = '{'
    escapeRules = []
    terminator = '}'

@Base.addSuccessorRule
class Square(SimpleRule):
    begins = '['
    escapeRules = []
    terminator = ']'


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


class InnerCode(SimpleRule):
    begins = '#{'
    escapeRules = []
    terminator = '}'

