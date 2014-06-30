"""
newtranslator
*************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Experimental version 3 of the patch file format. Still not final, needs some
work, including on Ruby side.
"""

import pyrbComms
from collections import defaultdict
import os.path
import os


class Translator(object):
    version = '3.0'
    header = '# RPGMAKER TRANS PATCH FILE VERSION '
    def __init__(self):
        self.stringOrder = []
        self.translations = defaultdict(dict)
        
    def exportToRubyString(self):
        return pyrbComms.dumpTranslations(self.translations)
    
    def exportToRubyFragment(self, fn):
        with open(fn, 'wb') as f:
            f.write(self.exportToRubyString())
            
    def mergeFromFile(self, fn):
        with open(fn, 'rb') as f:
            x = f.read()
        self.mergeFromString(x)
        
    def mergeFromString(self, string):
        newTrans, newOrder = pyrbComms.loadFromString(string)
        self.merge(newTrans, newOrder)
        
    def merge(self, newTrans, newOrder):
        for x in newOrder:
            if x not in self.stringOrder:
                self.stringOrder.append(x)
        for string in newTrans:
            self.translations[string].update(newTrans[string])

    def getNonCommand(self, lines, startIndex):
        index = startIndex
        while not lines[index].startswith('#'):
            index += 1
        originalString = self.unescapeString('\n'.join(lines[startIndex:index]))
        return index, originalString
            
    def loadString(self, string):
        lines = string.split('\n')
        versionString = lines.pop(0)
        if not versionString.startswith(self.header):
            raise Exception('Can\'t load string')
        elif versionString.partition(self.header)[2].strip() != self.version:
            version = versionString.partition(self.header)[2].strip()
            raise Exception('Incorrect version %s' % str(version))
        
        index = 0
        lineslen = len(lines)
        contexts = []
        while index < lineslen:
            line = lines[index]
            if line.startswith('# BEGIN STRING'):
                index += 1
                index, originalString = self.getNonCommand(lines, index)
            elif line.startswith('# CONTEXT:'):
                while lines[index].startswith('# CONTEXT'):
                    contexts.append(lines[index].partition('# CONTEXT:')[2].strip())
                    index += 1
            elif line.startswith('#'):
                index += 1
            elif contexts:
                index, translationString = self.getNonCommand(lines, index)                
                if translationString:
                    for context in contexts:
                        self.translations[originalString][context] = translationString
                contexts = []
            else:
                index += 1
                
    def loadDir(self, dir):
        for fn in os.listdir(dir):
            if fn.endswith('.txt'):
                fullfn = os.path.join(dir, fn)
                self.loadFile(fullfn)
                
    def loadFile(self, fn):
        with open(fn, 'rb') as f:
            string = f.read()
        self.loadString(string)
                
    def escapeString(self, string):
        return string.replace('/', '//').replace('#', '/#')
    
    def unescapeString(self, string):
        return string.replace('/#', '#').replace('//', '/')
    
    def dumpString(self, string, orderedContexts, contextDict):
        translations = defaultdict(list)
        stringLS = []
        for context in orderedContexts:
            translations[contextDict[context]].append(context)
        #print translations.keys()
        stringLS.append('# BEGIN STRING')
        stringLS.append(self.escapeString(string))
        #print orderedContexts
        while orderedContexts:
            currentContext = orderedContexts.pop(0)
            translation = contextDict[currentContext]
            contextsMatching = translations[translation]
            for context in contextsMatching:
                if context in orderedContexts:
                    orderedContexts.remove(context)
                stringLS.append('# CONTEXT: %s' % context)
            if translation == 0:
                stringLS.append('# UNTRANSLATED\n')
            else:
                stringLS.append(self.escapeString(translation))
        stringLS.append('# END STRING')
        return stringLS
        
    def patchStrings(self, contextPrefixes):
        stringLSs = defaultdict(lambda: list([self.header + self.version]))
        for string in self.stringOrder:
            contextDict = self.translations[string]
            orderedContexts = sorted(contextDict.keys()) 
            leadContext = orderedContexts[0]
            stringLS = None
            for contextPrefix in contextPrefixes:
                if leadContext.startswith(contextPrefix):
                    stringLS = stringLSs[contextPrefix]
                    break
            if stringLS is None:
                stringLS = stringLSs['MISC']
            stringLS.extend(self.dumpString(string, orderedContexts, contextDict))
            
        unused = [string for string in self.translations if string not in self.stringOrder
                  and any((val != 0 for val in list(self.translations[string].values())))]
        for string in unused:
            stringLS = stringLSs['UNUSED']
            contextDict = self.translations[string]
            orderedContexts = sorted(contextDict.keys())
            stringLS.extend(self.dumpString(string, orderedContexts, contextDict))
            
        strings = dict([(key, '\n'.join(stringLSs[key])) for key in stringLSs])
        return strings
        
    def patchFiles(self, contexts, directory='.'):
        strings = self.patchStrings(contexts)
        for key in strings:
            fn = os.path.join(directory, '%s.txt' % key)
            with open(fn, 'wb') as f:
                f.write(strings[key])
        return strings
            
if __name__ == '__main__':
    #x = Translator()         
    #x.mergeFromFile('CommonEvents.pyf')
    #y = x.patchFiles([])
    z = Translator()
    #z.loadString(y)
    z.loadFile('MISC.txt')
    #print z.translations
    print(z.patchFiles([]))
    
    