"""
translator3
***********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Version 3 of the patch file format. Currently WIP. Different from experimental
newtranslator, although backwards compatible with it.
"""

from collections import namedtuple, OrderedDict
from fuzzywuzzy import process

from .translatorbase import Translator, TranslatorError

class TranslationLine(namedtuple('TranslateableLine', 
                                   ['cType', 'data', 'comment'])):
    """A token representing a single line of a translation file"""
    def __new__(cls, cType, data, comment=''):
        """Give comment the a useful default argument"""
        return super().__new__(cls, cType, data, comment)
    
    @classmethod
    def Context(cls, context):
        """Create a line which is a context"""
        return cls('context', context)
    
    @classmethod
    def Begin(cls):
        """Create a begin line"""
        return cls('begin', '> BEGIN STRING')
    
    @classmethod
    def Data(cls, data, comment=''):
        """Create a data line"""
        return cls('data', data, comment)
    
    @classmethod
    def fromString(cls, string):
        """Instantiate a line from a string"""
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
            data = data.partition(':')[2].strip()
            if '<' in data:
                data = data.rpartition('<')[0].strip()
        elif not string.strip():
            cType = 'comment'
        else:
            cType = 'data'
            
        return cls(cType, data, comment)
            
    def asString(self, translations):
        """Return a line as a string"""
        if self.cType == 'context':
            translation = translations.get(self.data, '').strip()
            translated = True if len(translation) > 0 else False 
            translatedString = '' if translated else ' < UNTRANSLATED'
            return '> CONTEXT: %s%s%s'% (self.data, translatedString, 
                                         self.comment)
        else:
            return '%s%s' % (self.data, self.comment)
    
class Translation:
    """A single block of translations, usually referring to all instances
    of a single string in a game with 1 or more contexts."""
    def __init__(self, items):
        """Initialise, based on a list of translation lines"""
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
        """Method to create a new Translation based on untranslated string
        and contexts it occurs in"""
        return Translation([TranslationLine.Begin(),
                 TranslationLine.Data(raw)] +
                [TranslationLine.Context(context) for context in contexts]
                + [TranslationLine.Data('')])
        
    @classmethod
    def fromString(cls, string):
        """Create a Translation from a string of a translation"""
        itemsGen = (TranslationLine.fromString(line) for line in string.split('\n'))
        items = [item for item in itemsGen if item.cType not in ('begin', 'end')]
        return items        
    
    @staticmethod
    def __addTranslations(stringDict, stringLS, contexts):
        """Add translations to a given dictionary"""
        string = '\n'.join(stringLS)
        for context in contexts:
            stringDict[context] = string
            
    def insert(self, context, afterContext, translation):
        """Insert a new context (and translation) after a given context"""
        indx = 0
        line = self.items[indx]
        while indx < len(self.items) and not (line.cType == 'context' and line.data == afterContext):
            indx += 1
            line = self.items[indx]
        while indx < len(self.items) and line.cType == 'context':
            indx += 1
            line = self.items[indx]
        self.items.insert(indx, TranslationLine.Context(context))
        self.translations[context] = translation
        
    def asString(self):
        return '\n'.join(item.asString(self.translations) for item in self.items)

class TranslationFile:
    """Represents a v3.1 Translation File. Also has the capacity to convert
    v3.0 patch files"""
    version = (3, 1)
    header = 'RPGMAKER TRANS PATCH FILE VERSION'
    def __init__(self, filename, translateables):
        """Initialise from a filename and list of translateables"""
        self.filename = filename
        self.translateables = translateables
    
    @classmethod
    def fromString(cls, filename, string):
        """Initialiser from a filename and string"""
        lines = string.split('\n')
        versionLine = lines.pop(0)
        versionString = versionLine.partition(cls.header)[2].strip()
        if not versionString:
            raise TranslatorError('Cannot parse version')
        fileVersion = [int(x) for x in versionString.split('.')]
        if fileVersion[0] != cls.version[0]:
            raise TranslatorError('Wrong version')
        if fileVersion[1] == 0:
            lines = cls.convertFrom30(lines)
            fileVersion[1] = 1
        if fileVersion[1] != 1:
            raise TranslatorError('Wrong version')
        translateables = [Translation(x) for x in cls.splitLines(lines)]
        return cls(filename, translateables)
        
    def __iter__(self):
        """Iterate over translateables"""
        return iter(self.translateables)
    
    def asString(self):
        """Return the file in string form"""
        output = ['> %s %s' % (type(self).header, 
                              '.'.join(str(x) for x in type(self).version))]
        output.extend(x.asString() for x in self)
        return '\n'.join(output)
    
    def addTranslation(self, translation):
        """Add a translation to the file"""
        self.translateables.append(translation)
    
    @staticmethod
    def splitLines(lines):
        """Split a file into Translations composed of TranslationLines"""
        current = []
        for line in lines:
            translationLine = TranslationLine.fromString(line)
            if translationLine.cType in ('begin',):
                if len(current) > 0: 
                    yield current
                    current = []
            if translationLine.cType in ('end',):
                pass
            else:
                current.append(translationLine)
        if current:
            yield current
                
    @staticmethod
    def convertFrom30(lines):
        """Convert a file from 3.0 format"""
        return [TranslationFile.convertLineFrom30(line) for line in lines]
    
    @staticmethod
    def convertLineFrom30(string):
        """Convert an individual line from 3.0 format"""
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
        """Initialise a canonical translation for the given string"""
        self.raw = raw
        self.contexts = {}
        self.__default = None
        
    @property
    def default(self):
        """Gives a default translation. This is simply the most popular
        translation"""
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
        """Add a Translation object to this CanonicalTranslation"""
        newContexts = {}
        for context in translation.translations:
            newContexts[context] = (translation, translation.translations[context])
        self.contexts.update(newContexts)
        
    def translate(self, context):
        """Return a translation for given context. If context is untranslated, 
        try using FuzzyWuzzy to find a good match. If no match found, use
        default. Either way, update relevant translation with the new
        context"""
        if context in self.contexts:
            return self.contexts[context][1] # Simple case
        else:
            bestMatch, confidence = process.extractOne(context, self.contexts.keys())
            if confidence > 90:
                matchContext, matchTranslation = bestMatch, self.contexts[bestMatch]
            else:
                matchContext, matchTranslation = self.default
            matchTranslation[0].insert(context, matchContext, matchTranslation[1])
            return matchTranslation[1]

class TranslationDict(dict):
    """An object to lazily create CanonicalTranslations"""
    def __missing__(self, key):
        """Lazily create a CanonicalTranslation"""
        self[key] = CanonicalTranslation(key)
        return self[key]
    
class Translator3(Translator):
    """A Version 3 Translator"""
    def __init__(self, namedStrings, debug = False, *args, **kwargs):
        """Initialise the translator from a dictionary of filenames to
        file contents"""
        if isinstance(namedStrings, dict):
            namedStrings = namedStrings.items()
        self.translationFiles = {}
        for name, string in namedStrings:
            self.translationFiles[name] = TranslationFile.fromString(name, string)
        self.translationDB = TranslationDict()
        for translationFileName in self.translationFiles:
            translationFile = self.translationFiles[translationFileName]
            for translation in translationFile:
                self.translationDB[translation.raw].addTranslation(translation)
        self.newtranslations = OrderedDict()
        self.debug = debug
        
    def getPatchData(self):
        """Return a dictionary of filenames to file contents of the patch"""
        super().getPatchData()
        for raw in self.newtranslations:
            contexts = sorted(self.newtranslations[raw])
            baseContext = contexts[0]
            name = baseContext.partition('/')[0]
            transObj = Translation.fromDesc(raw, contexts)
            if name not in self.translationFiles:
                self.translationFiles[name] = TranslationFile(name, [transObj])
            else:
                self.translationFiles[name].addTranslation(transObj)
        ret = {}
        for name in self.translationFiles:
            ret[name] = self.translationFiles[name].asString()
        return ret

    def translate(self, string, context):
        """Get translation of string in given context"""
        if self.debug:
            print('TRANSLATORDEBUG: %s:%s' % (string, context))
        if string in self.translationDB:
            ret = self.translationDB[string].translate(context)
        else:
            if string not in self.newtranslations:
                self.newtranslations[string] = []
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
# CONTEXT: Actors/1/Actor/name/ < UNTRANSLATED \# Comment
Laurel
# END STRING"""

dummy3 = """> RPGMAKER TRANS PATCH FILE VERSION 3.1
> BEGIN STRING
ローレル
> CONTEXT: Actors/1/Actor/name/ < UNTRANSLATED # Comment
Laurel
> END STRING"""

if __name__ == '__main__':
    t = Translator3({'Actors': dummy3}, mtime=1)
    print(t.translate('ローレル', 'Actors/2/Actor/name/'))
    print(t.translate('Meh','Actors/3/Actor/name/'))
    print(t.translate('Meh','Blargh/3/Actor/name/'))
    print(t.translate('Eeh','Blargh/3/Actor/name/'))
    r = t.getPatchData()
    for name in sorted(r.keys()):
        print('FILENAME:%s' % name)
        print(r[name])
    #print(Translateable(dummy))