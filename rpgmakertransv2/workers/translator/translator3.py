'''
Created on 3 Dec 2014

@author: habisain
'''

from collections import namedtuple, defaultdict

class TranslationLine(namedtuple('TranslateableLine', 
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
            return '> CONTEXT: %s%s'% (self.data, self.comment)
        else:
            return '%s%s' % (self.data, self.comment)
    
class Translation:
    def __init__(self, items):
        self.items = items
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
        self.raw = strings.pop('RAW')
        self.translations = strings
        
    @classmethod
    def fromString(cls, string):
        itemsGen = (TranslationLine.fromString(line) for line in string.split('\n'))
        items = [item for item in itemsGen if item.cType not in ('begin', 'end')]
        return items        
    
    @staticmethod
    def __addTranslations(stringDict, stringLS, contexts):
        string = '\n'.join(stringLS)
        for context in contexts:
            stringDict[context] = string 
        
    def __str__(self):
        return '\n'.join(str(item) for item in self.items)

class TranslatorError(Exception): pass

class TranslationFile:
    version = (3, 1)
    header = 'RPGMAKER TRANS PATCH FILE VERSION '
    def __init__(self, filename, string):
        self.filename = filename
        lines = string.split('\n')
        versionLine = lines.pop(0)
        versionString = versionLine.partition(type(self).header)[2].strip()
        if not versionString:
            raise TranslatorError('Cannot parse version')
        fileVersion = [int(x) for x in versionString.split('.')]
        if fileVersion[0] != type(self).version[0]:
            raise TranslatorError('Wrong version')
        if fileVersion[1] == 0:
            lines = type(self).convertFrom30(lines)
        elif fileVersion[1] != 1:
            raise TranslatorError('Wrong version')
        
        self.translateables = [Translation(x) for x in type(self).splitLines(lines)]
        print(len(self.translateables))
        for x in self.translateables: print(x)
    
    @staticmethod
    def splitLines(lines):
        current = []
        for line in lines:
            translationLine = TranslationLine.fromString(line)
            if translationLine.cType in ('begin', 'end'):
                if len(current) > 0: 
                    yield current
                    current = []
            else:
                current.append(translationLine)
        if current:
            yield current
                
    @staticmethod
    def convertFrom30(lines):
        return [TranslationFile.convertLineFrom30(line) for line in lines]
    
    @staticmethod
    def convertLineFrom30(string):
        ls = list(string)
        for indx in range(len(ls)):
            char = ls[indx]
            if char == '#':
                if ls[indx-1:indx] != '\\' and ls[indx-2:indx] != '\\\\': 
                    ls[indx] = '>'
            elif char == '>':
                ls[indx] = '\>'
        return ''.join(ls)
    
class Translator3:
    pass

dummy = """ローレル  # Protag name
> CONTEXT: Actors/1/Actor/name/
Laurel \# Not a comment"""

dummy2 = """# RPGMAKER TRANS PATCH FILE VERSION 3.0
# BEGIN STRING
ローレル
# CONTEXT: Actors/1/Actor/name/
Laurel
# END STRING"""

if __name__ == '__main__':
    TranslationFile('d2', dummy2)
    #print(Translateable(dummy))