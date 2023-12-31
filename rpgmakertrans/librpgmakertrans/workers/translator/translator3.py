"""
translator3
***********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Version 3 of the patch file format. 
"""

import traceback

from operator import itemgetter
from collections import OrderedDict
from fuzzywuzzy import process

from .translatorbase import Translator, TranslatorError

def _convertContext(context):
    """Convert any filename component to upper case
    internally"""
    if '/' in context:
        fn, _, remainder = context.partition('/')
        return '%s/%s' % (fn.upper(), remainder)
    else:
        return context
        
class ContextDict(dict):
    """Special dictionary that handles context->translation
    mapping. Takes into account that the first element of a multipart
    context is a filename and therefore case insensitive due to,
    well, Windows."""
    
    def get(self, key, *args, **kwargs):
        """Implement get method, converting key as appropriate"""
        return super().get(_convertContext(key), *args, **kwargs)
    
    def __contains__(self, item):
        """Implement contains, converting key as appropriate"""
        return super().__contains__(_convertContext(item))
    
    def __getitem__(self, key):
        """Implement getitem, converting key as appropriate"""
        return super().__getitem__(_convertContext(key))
    
    def __setitem__(self, key, value):
        """Implement setitem, converting key as appropriate"""
        return super().__setitem__(_convertContext(key), value)
    
    def __delitem__(self, key):
        """Implement delitem, converting key as appropriate"""
        return super().__delitem__(_convertContext(key))
    
class ContextSet(ContextDict):
    """Thin implementation of a set over ContextDict; Implemented
    over ContextDict rather than Set for ease of programming."""
    def add(self, key):
        """Add element to set"""
        self[key] = True
        
    def remove(self, key):
        """Delete element from set"""
        del self[key]
             
class TranslationLine:
    """A token representing a single line of a translation file"""
    escapes = [('\\', '\\\\'), ('>', '\\>'), ('#', '\\#')]

    def __init__(self, cType, data, command='', comment=''):
        self.cType, self.data, self.command, self.comment = cType, data, command, comment

    @classmethod
    def Context(cls, context):
        """Create a line which is a context"""
        return cls('context', context, '> CONTEXT: ')

    @classmethod
    def Begin(cls):
        """Create a begin line"""
        return cls('begin', '', '> BEGIN STRING')

    @classmethod
    def Data(cls, data, comment=''):
        """Create a data line"""
        return cls('data', data, comment=comment)

    @classmethod
    def End(cls):
        """Create an end line"""
        return cls('end', '', '> END STRING')

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
        data = string[:indx].rstrip()
        command = ''

        if string.startswith('> BEGIN STRING'):
            cType = 'begin'
            command = data
            data = ''
        elif string.startswith('> END STRING'):
            cType = 'end'
            command = data
            data = ''
        elif string.startswith('> CONTEXT:'):
            cType = 'context'
            command, _, data = data.partition(':')
            if data.startswith(' '):
                data.lstrip()
                command += ' '
            if '<' in data:
                data = data.partition('<')[0].strip()
            else:
                data = data.strip()
        elif string.startswith('>'):
            raise Exception('Invalid command %s' % string)
        elif len(comment) > 0 and not data.strip():
            cType = 'comment'
        else:
            cType = 'data'

        for orig, escaped in reversed(cls.escapes):
            data = data.replace(escaped, orig)

        return cls(cType, data, command, comment)

    def __str__(self):
        return 'Translation(%r, %r, %r)' % (self.cType, self.data, self.comment)

    @classmethod
    def escapeString(cls, unescaped):
        escapedData = unescaped
        for orig, escaped in cls.escapes:
            escapedData = escapedData.replace(orig, escaped)
        return escapedData

    def isUsed(self, contexts):
        """Determine if a line is used by a list of contexts"""
        return (self.cType != 'context' or self.data in contexts
                or self.comment.strip())

    def asString(self, translations, contexts):
        """Return a line as a string"""
        if self.cType == 'context':
            translation = translations.get(self.data, '').strip()
            translated = len(translation) > 0 or self.data == 'None'
            translatedString = '' if translated else ' < UNTRANSLATED'
            unusedString = '' if self.data in contexts else ' < UNUSED'
            escapedData = self.escapeString(self.data)
            return '> CONTEXT: %s%s%s%s'% (escapedData, translatedString,
                                           unusedString, self.comment)
        else:
            return '%s%s%s' % (self.command, self.escapeString(self.data),
                               self.comment)

class TLFileStats:
    def __init__(self, strings = 0, contexts = 0, translations = 0):
        self.strings = strings
        self.contexts = contexts
        self.translations = translations
        
    def __repr__(self):
        return 'TLFileStats(%s, %s, %s)' % (self.strings, self.contexts,
                                            self.translations)
        
    def __str__(self):
        percentage = int((self.translations / self.contexts) * 100)
        return 'U:%s, C:%s, T:%s, P:%s%%' % (self.strings, self.contexts, 
                                             self.translations, percentage)
    
    def __add__(self, other):
        assert isinstance(other, TLFileStats), 'Wrong type'
        return TLFileStats(self.strings + other.strings,
                           self.contexts + other.contexts,
                           self.translations + other.translations)
        
class Translation:
    """A single block of translations, usually referring to all instances
    of a single string in a game with 1 or more contexts."""
    def __init__(self, items):
        """Initialise, based on a list of translation lines"""
        if items[0].cType != 'begin':
            items.insert(0, TranslationLine.Begin())
        if not any(item.cType == 'end' for item in items):
            items.append(TranslationLine.End())
            items.append(TranslationLine.Data(''))
        self.items = items
        currentContexts = ['RAW']
        currentString = []
        strings = ContextDict()
        for item in self.items:
            if item.cType != 'data':
                if currentString:
                    self.__addTranslations(strings, currentString, currentContexts)
                    currentContexts = []
                    currentString = []
                if item.cType == 'context':
                    currentContexts.append(item.data)
            elif item.cType == 'data':
                currentString.append(item.data)
        self.__addTranslations(strings, currentString, currentContexts)
        self.raw = strings.pop('RAW')
        self.translations = strings
        self.usedContexts = ContextSet()
        
    @classmethod
    def fromDesc(cls, raw, contexts):
        """Method to create a new Translation based on untranslated string
        and contexts it occurs in"""
        ret =  Translation([TranslationLine.Begin(),
                 TranslationLine.Data(raw)] +
                [TranslationLine.Context(context) for context in contexts]
                + [TranslationLine.Data('')])
        for context in contexts:
            ret.useContext(context)
        return ret

    @classmethod
    def fromString(cls, string):
        """Create a Translation from a string of a translation"""
        items = Translation([TranslationLine.fromString(line)
                             for line in string.split('\n')])
        return items

    def __addTranslations(self, stringDict, stringLS, contexts):
        """Add translations to a given dictionary"""
        string = '\n'.join(stringLS)
        for context in contexts:
            stringDict[context] = string
            
    def getStats(self, filters=()):
        translations = [self.translations[x] for x in self.translations if all(not f(x) for f in filters)]
        stats = TLFileStats(min(1, len(translations)), len(translations), sum(1 for t in translations if t.strip()))
        return stats


    def insert(self, context, afterContext, translation):
        """Insert a new context (and translation) after a given context"""
        indx = 0
        line = self.items[indx]
        while indx < len(self.items) and not (line.cType == 'context' and _convertContext(line.data) == afterContext):
            indx += 1
            line = self.items[indx]
        while indx < len(self.items) and line.cType == 'context':
            indx += 1
            line = self.items[indx]
        self.items.insert(indx, TranslationLine.Context(context))
        self.translations[context] = translation

    def asString(self):
        if self.items[-1].cType != 'data':
            self.items.append(TranslationLine.Data(''))
        return '\n'.join(item.asString(self.translations, self.usedContexts) for item in self.items)

    def useContext(self, context):
        """Mark a context as being currently in use"""
        self.usedContexts.add(context)

    def prune(self):
        """Prune unused contexts from translation file. If a translation
        has no context available to it, then it is given the special
        context 'None'"""
        self.items = [item if item.isUsed(self.usedContexts) else None
                      for item in self.items]
        while None in self.items:
            neighbourContexts = False
            for direction in (-1, +1):
                indx = self.items.index(None)
                while 0 < indx < len(self.items) and self.items[indx] is None:
                    indx += direction
                if (isinstance(self.items[indx], TranslationLine)
                    and self.items[indx].cType == 'context'):
                    neighbourContexts = True
                    break
            if not neighbourContexts:
                self.items.insert(self.items.index(None),
                                  TranslationLine.Context('None'))
            self.items.remove(None)


class TranslationFile:
    """Represents a v3.2 Translation File. Also has the capacity to convert
    v3.0/v3.1 patch files"""
    version = (3, 2)
    header = 'RPGMAKER TRANS PATCH FILE VERSION'
    def __init__(self, filename, translateables, enablePruning=True):
        """Initialise from a filename and list of translateables"""
        self.filename = filename
        self.translateables = translateables
        self.enablePruning = enablePruning

    @classmethod
    def fromString(cls, filename, string, *args, **kwargs):
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
        if fileVersion[1] == 1:
            lines = cls.convertFrom31(lines)
            fileVersion[1] = 2
        if fileVersion[1] != 2:
            raise TranslatorError('Wrong version')
        translateables = [Translation(x) for x in cls.splitLines(lines)]
        return cls(filename, translateables, *args, **kwargs)
    
    def getStats(self, filters=()):
        stats = TLFileStats()
        for translateable in self.translateables:
            stats += translateable.getStats(filters)
        return stats

    def __iter__(self):
        """Iterate over translateables"""
        return iter(self.translateables)

    def prune(self):
        for translateable in self:
            translateable.prune()

    def asString(self):
        """Return the file in string form"""
        if self.enablePruning:
            self.prune()
        output = ['> %s %s' % (type(self).header,
                              '.'.join(str(x) for x in type(self).version))]
        output.extend(x.asString() for x in self)
        return '\n'.join(output)

    def addTranslation(self, translation):
        """Add a translation to the file"""
        assert isinstance(translation, Translation)
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
            current.append(translationLine)
        if current:
            yield current
    
    @staticmethod
    def convertFrom30(lines):
        """Convert a file from 3.0 format"""
        return [TranslationFile.convertLineFrom30(line) for line in lines if not line.startswith('# UNTRANSLATED')]

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

    @staticmethod
    def convertFrom31(lines):
        """Convert contexts from v3.1 to v3.2. This does 3 things:
        1) Remove class names from contexts
        2) Flip the order of descriptor and position in page for 
        Dialogue and Choice
        3) Remove Scripts prefix from InlineScripts, so that they can
        be better fuzzy matched. The InlineScript contexts are horribly
        broken, so they can't be rewritten, but hopefully the fuzzy
        matcher is enough.
        """
        removeParts = ('Class', 'Map', 'Enemy', 'Armor', 'Weapon', 
                       'System', 'Actor', 'Item', 'State', 'Troop', 'Skill',
                       'Event', 'System::Terms')
        flippers = ('Dialogue', 'Choice')
        newLines = []
        for line in lines:
            if line.startswith('> CONTEXT:'):
                tmp, _, comment = line.partition('#')
                context = tmp.partition(':')[2].partition('<')[0]
                parts = context.split('/')
                for flipper in flippers:
                    if flipper in parts:
                        indx = parts.index(flipper)
                        parts[indx], parts[indx+1] = parts[indx+1], parts[indx]
                if 'InlineScript' in parts and parts[0].lower() == 'scripts':#
                    parts.pop(0)
                newContext = '/'.join([parts[0]] + [part for part in parts[1:] if part not in removeParts])
                line = '> CONTEXT: %s%s' % (newContext, ('#%s' % comment) if comment else '')
            newLines.append(line) 
        return newLines
    
class CanonicalTranslation:
    """Seperate from the structure of the files, the canonical translation
    keeps tabs on which Translation object holds translations for what context
    and also where to put a new context."""
    def __init__(self, raw):
        """Initialise a canonical translation for the given string"""
        self.raw = raw
        self.contexts = ContextDict()
        self.__default = None

    @property
    def default(self):
        """Gives a default translation. This is simply the most popular
        translation, unless it has been set by a translation with 'Default'
        context"""
        if self.__default is None:
            tally = {}
            for context in self.contexts:
                translationString = self.contexts[context][0]
                if translationString not in tally:
                    tally[translationString] = [0, context]
                tally[translationString][0] += 1
            bestContext = max(tally.values(), key=itemgetter(0))[1]
            self.__default = bestContext, self.contexts[bestContext]
        return self.__default
    
    def markAllUsed(self):
        for context, translation in self.contexts.items():
            translation[0].useContext(context)

    def addTranslation(self, translation):
        """Add a Translation object to this CanonicalTranslation"""
        newContexts = {}
        for context in translation.translations:
            newContexts[context] = (translation, translation.translations[context])
            if context == 'Default':
                self.__default = context, translation
        self.contexts.update(newContexts)
        
    def __translate(self, context):
        if context in self.contexts:
            self.contexts[context][0].useContext(context)
            return self.contexts[context] # Simple case
        else:
            bestMatch, confidence = process.extractOne(context, self.contexts.keys())
            if confidence > 90:
                matchContext, matchTranslation = bestMatch, self.contexts[bestMatch]
            else:
                matchContext, matchTranslation = self.default
            matchTranslation[0].insert(context, matchContext, matchTranslation[1])
            matchTranslation[0].useContext(context)
            return matchTranslation
        
    def translate(self, context):
        """Return a translation for given context. If context is untranslated,
        try using FuzzyWuzzy to find a good match. If no match found, use
        default. Either way, update relevant translation with the new
        context"""
        return self.__translate(context)[1]
    
    def getTranslationObj(self, context):
        return self.__translate(context)[0]


class TranslationDict(dict):
    """An object to lazily create CanonicalTranslations"""
    def __missing__(self, key):
        """Lazily create a CanonicalTranslation"""
        self[key] = CanonicalTranslation(key)
        return self[key]
    
class TranslationFileDict(dict):
    def __init__(self, enablePruning):
        self.enablePruning = enablePruning
        self.missing_map = {}
        
    def __missing__(self, key):
        if key not in self.missing_map:
            for key_2 in self:
                if key_2.lower() == key.lower():
                    self.missing_map[key] = self[key_2]
                    break
            else:
                self[key] = TranslationFile(key, [], self.enablePruning)
        ret = self.missing_map.get(key, self.get(key, None))
        assert ret is not None
        return ret


class Translator3(Translator):
    """A Version 3 Translator"""
    def __init__(self, namedStrings, enablePruning = True, debug = False, 
                 config=None, *args, **kwargs):
        """Initialise the translator from a dictionary of filenames to
        file contents"""
        super().__init__(*args, **kwargs)
        if isinstance(namedStrings, dict):
            namedStrings = namedStrings.items()
        self.translationFiles = TranslationFileDict(enablePruning)
        self.errors = []
        for name, string in namedStrings:
            try:
                self.translationFiles[name] = TranslationFile.fromString(name, string, enablePruning=enablePruning)
            except Exception:
                self.errors.append('Encountered an error in file %s; traceback follows %s:\n' % (name, traceback.format_exc()))
        self.translationDB = TranslationDict()
        for translationFileName in self.translationFiles:
            translationFile = self.translationFiles[translationFileName]
            for translation in translationFile:
                self.translationDB[translation.raw].addTranslation(translation)
        self.newtranslations = OrderedDict()
        self.debug = debug
        self.translateLabels = False if config is None else config.translateLabels

    def get_errors(self):
        return self.errors

    def getPatchData(self):
        """Return a dictionary of filenames to file contents of the patch"""
        super().getPatchData()
        for raw in self.newtranslations:
            contexts = self.newtranslations[raw]
            baseContext = contexts[0]
            name = baseContext.partition('/')[0]
            transObj = Translation.fromDesc(raw, contexts)
            self.translationFiles[name].addTranslation(transObj)
        ret = {}
        for name in self.translationFiles:
            ret[name] = self.translationFiles[name].asString()
        return ret
    
    def getStats(self, filters=()):
        statDict = OrderedDict()
        for translationFileName in sorted(self.translationFiles):
            translationFile = self.translationFiles[translationFileName]
            statDict[translationFileName] = translationFile.getStats(filters)
        return statDict
    
    def markAllUsed(self):
        """Mark everything as being used - useful for debug tools"""
        for canonicalTranslation in self.translationDB.values():
            canonicalTranslation.markAllUsed()

    def translate(self, string, context):
        """Get translation of string in given context"""
        super().translate(string, context)
        string = '\n'.join(line.rstrip() for line in string.split('\n'))
        if not string:
            return string
        if self.debug:
            print('TRANSLATORDEBUG: %s:%s' % (string, context))
        if string in self.translationDB:
            ret = self.translationDB[string].translate(context)
        elif not self.translateLabels and context.endswith('Label'):
            return string
        else:
            if string not in self.newtranslations:
                self.newtranslations[string] = []
            if context not in self.newtranslations[string]:
                self.newtranslations[string].append(context)
            ret = ''
        if len(ret.strip()) == 0:
            return string
        else:
            return ret
        
class Translator3Rebuild(Translator3):
    """Specialised version of Translator3 which rebuilds the patch,
    i.e. it puts every translation where RPGMaker Trans thinks it
    would go in a new patch"""
    def __init__(self, *args, **kwargs):
        """Initialise Translator3Rebuilds extra things"""
        super().__init__(*args, **kwargs)
        self.newPatch = TranslationFileDict(True)
        self.reassigned = set()
        
    def translate(self, string, context):
        """Wraps translate so that the translation object is
        reassigned in the new patch, strips out any untranslated
        and unused items, and places any unused but translated items
        in a special file."""
        ret = super().translate(string, context)
        string = '\n'.join(line.rstrip() for line in string.split('\n'))
        if string in self.translationDB:
            transObj = self.translationDB[string].getTranslationObj(context)
            newFile = context.partition('/')[0]
            if transObj not in self.reassigned:
                self.newPatch[newFile].addTranslation(transObj)
                self.reassigned.add(transObj)
        return ret
    
    def getPatchData(self):
        """Wraps getPatchData to substitute the new patch"""
        for transFile in self.translationFiles.values():
            for transObj in transFile.translateables:
                if any(transObj.translations.values()) and transObj not in self.reassigned:
                    self.newPatch['Unused'].addTranslation(transObj)
        self.oldPatch, self.translationFiles = self.translationFiles, self.newPatch
        ret = super().getPatchData()
        self.translationFiles = self.oldPatch
        return ret

def debugDirToNamedStrings(directory):
    import os
    data = OrderedDict()
    ls = sorted([fn for fn in os.listdir(directory) if fn.endswith('.txt')])
    for fn in ls:
        with open(os.path.join(directory, fn)) as f:
            data[fn.rpartition('.')[0]] = f.read()
    return data

def debugLoadDir(directory):
    """Debug function for loading a directory based patch"""
    data = debugDirToNamedStrings(directory)
    return Translator3(data, mtime=0)

def debugGetStats(directory, onlyIncomplete=True):
    """Debug function to get stats from a directory based patch"""
    translator = debugLoadDir(directory)
    stats = translator.getStats([lambda x: '/Label' in x, lambda x: 'TROOP' in x and 'name' in x])
    for filename, stat in stats.items():
        if stat.contexts > stat.translations:
            print('%s: %s' % (filename, stat))
    print('Total: %s' % (sum(stats.values(), TLFileStats())))

if __name__ == '__main__':
    import sys
    if sys.argv[1] == '-d':
        debugGetStats(sys.argv[2])
    
