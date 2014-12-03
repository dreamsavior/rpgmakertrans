'''
Created on 3 Dec 2014

@author: habisain
'''

from collections import namedtuple, defaultdict

class TranslateableLine(namedtuple('TranslateableLine', 
                                   ['cType', 'data', 'comment'])):
    def __new__(cls, cType, data, comment=''):
        return super().__new__(cls, cType, data, comment)
    
    @classmethod
    def fromString(cls, string):
        indx = string.find('#', 0)
        going = True
        while going and indx != -1:
            if string[indx-1] != '\\':
                going = False
            else:
                indx = string.find('#', indx + 1)
        if indx == -1: 
            indx = len(string)
        
        while indx > 1 and string[indx-1].isspace():
            indx -= 1
        comment = string[indx:]
        data = string[:indx]
        
        if string.startswith('> BEGIN STRING'):
            cType = 'begin'
        elif string.startswith('> END STRING'):
            cType = 'end'
        elif string.startswith('> CONTEXT:'):
            cType = 'context'
            data = data.partition(':')[2].lstrip()
        elif not string.strip():
            cType = 'comment'
        else:
            cType = 'data'
            
        return cls(cType, data, comment)
            
    def __str__(self):
        if self.cType == 'context':
            return '> CONTEXT: %s'% (self.data, self.comment)
        else:
            return '%s%s' % (self.data, self.comment)
    
class Translateable:
    def __init__(self, string):
        self.items = [TranslateableLine.fromString(line) for line in string.split('\n')]
    
    @staticmethod
    def __addTranslations(stringDict, stringLS, contexts):
        string = '\n'.join(stringLS)
        for context in contexts:
            stringDict[context] = string
            
    def getStrings(self):
        currentContexts = ['RAW']
        currentString = []
        strings = {}
        for item in self.items:
            if item.cType == 'context':
                if currentString:
                    self.__addTranslations(strings, currentString, currentContexts)
                    currentContexts = []
                    currentString = []
                currentContexts.append(item.data)
            elif item.cType == 'data':
                currentString.append(item.data)
        self.__addTranslations(strings, currentString, currentContexts)
        return strings.pop('RAW'), strings 
        
    def __str__(self):
        return '\n'.join(str(item) for item in self.items)
        
class Translator3:
    pass

dummy = """ローレル  # Protag name
> CONTEXT: Actors/1/Actor/name/
Laurel \# Not a comment"""

if __name__ == '__main__':
    print(Translateable(dummy).getStrings())