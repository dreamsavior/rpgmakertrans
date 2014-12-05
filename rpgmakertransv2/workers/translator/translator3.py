"""
translator3
***********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Version 3 of the patch file format. Currently WIP. Different from experimental
newtranslator, although backwards compatible with it.
"""
from .translatorbase import Translator
from collections import namedtuple, defaultdict
from fuzzywuzzy import process

class TranslationLine(namedtuple('TranslateableLine', 
                                   ['cType', 'data', 'comment'])):
    def __new__(cls, cType, data, comment=''):
        return super().__new__(cls, cType, data, comment)
    
    @classmethod
    def Context(cls, context):
        return cls('context', context)
    
    @classmethod
    def Begin(cls):
        return cls('begin', '> BEGIN STRING')
    
    @classmethod
    def Data(cls, data, comment=''):
        return cls('data', data, comment)
    
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
        if items[0].cType != 'begin':
            items.insert(0, TranslationLine('begin', '> BEGIN STRING'))
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
    def fromDesc(cls, raw, contexts):
        return ([TranslationLine.Begin(),
                 TranslationLine.Data(raw)] +
                [TranslationLine.Context(context) for context in contexts]
                + [TranslationLine.Data('')])
        
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
            
    def insert(self, context, afterContext):
        indx = 0
        line = self.items[indx]
        while indx < len(self.items) and not (line.cType == 'context' and line.data == afterContext):
            indx += 1
            line = self.items[indx]
        while indx < len(self.items) and line.cType == 'context':
            indx += 1
        self.items.insert(indx-2, TranslationLine.Context(context))
        
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
            fileVersion[1] = 1
        if fileVersion[1] != 1:
            raise TranslatorError('Wrong version')
        
        self.translateables = [Translation(x) for x in type(self).splitLines(lines)]
    
    def __iter__(self):
        return iter(self.translateables)
    
    def __str__(self):
        output = ['> %s %s' % (type(self).header, 
                              '.'.join(str(x) for x in type(self).version))]
        output.extend(str(x) for x in self)
        return '\n'.join(output)
    
    @staticmethod
    def splitLines(lines):
        current = []
        for line in lines:
            translationLine = TranslationLine.fromString(line)
            if translationLine.cType in ('begin',):
                if len(current) > 0: 
                    yield current
                    current = []
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

class CanonicalTranslation:
    """Seperate from the structure of the files, the canonical translation
    keeps tabs on which Translation object holds translations for what context
    and also where to put a new context."""
    def __init__(self, raw):
        self.raw = raw
        self.contexts = {}
        self.__default = None
        
    @property
    def default(self):
        if self.__default is None:
            tally = {}
            for context in self.contexts:
                translationString = self.contexts[context][0]
                if translationString not in tally: 
                    tally[translationString] = [0, context]
                tally[translationString][0] += 1
            bestScore, bestContext = 0, None
            for translationString in tally:
                score, context = tally[translationString]
                if score > bestScore:
                    bestScore, bestContext = score, context
            self.__default = bestContext, self.contexts[bestContext]
        return self.__default
        
    def addTranslation(self, translation):
        newContexts = {}
        for context in translation.translations:
            newContexts[context] = (translation, translation.translations[context])
        self.contexts.update(newContexts)
        #self.contexts.update({(context, (translation, translation.translations[context])): 
        #                      context for context in translation.translations})
        
    def translate(self, context):
        if context in self.contexts:
            return self.contexts[context][1] # Simple case
        else:
            bestMatch, confidence = process.extractOne(context, self.contexts.keys())
            if confidence > 90:
                matchContext, matchTranslation = bestMatch, self.contexts[bestMatch]
            else:
                matchContext, matchTranslation = self.default
            matchTranslation[0].insert(context, matchContext)
            return matchTranslation[1]

class TranslationDict(dict):
    def __missing__(self, key):
        self[key] = CanonicalTranslation(key)
        return self[key]
    
class Translator3(Translator):
    def __init__(self, namedStrings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(namedStrings, dict):
            namedStrings = namedStrings.items()
        self.translationFiles = {}
        for name, string in namedStrings:
            self.translationFiles[name] = TranslationFile(name, string)
        self.translationDB = TranslationDict()
        for translationFileName in self.translationFiles:
            translationFile = self.translationFiles[translationFileName]
            for translation in translationFile:
                self.translationDB[translation.raw].addTranslation(translation)
        self.newtranslations = defaultdict(list)
        
    def getPatchData(self):
        # TODO: Sort out any new translations, then gather and output a
        # dictionary of the data
        pass

    def translate(self, string, context):
        if string in self.translationDB:
            ret = self.translationDB[string].translate(context)
        else:
            self.newtranslations[string].append(context)
            ret = ''
        if len(ret.strip()) == 0:
            return string
        else:
            return ret

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
    t = Translator3({'d2': dummy2}, mtime=1)
    print(t.translate('ローレル', 'Actors/2/Actor/name/'))
    #print(Translateable(dummy))