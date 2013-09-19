'''
Created on 18 Apr 2013

@author: habisain
'''

if __name__ == '__main__':
    import sys
    sys.path.append('../')

import os, os.path, shutil
import codecs
from resources import BasePatch
from translator import TranslatorManager

filePatchers = {}
class FilePatcher(BasePatch):
    
    def __init__(self, path):
        super(FilePatcher, self).__init__(path)
        if os.path.isfile(self.path):
            self.path = os.path.split(path)[0]
        self.translatorManager = TranslatorManager()
        self.translatorManager.start()
            
    def makeTranslator(self):
        data = {}
        mtime = 0
        self.genPatchDataFiles()
        for fn in self.patchDataFiles:
            name = os.path.split(fn)[1].rpartition('.')[0].lower()
            mtime = max(mtime, os.path.getmtime(fn))
            with codecs.open(fn, 'r', encoding='utf-8') as f:
                data[name] = f.read()
            
        return getattr(self.translatorManager, type(self).translatorClass)(data, mtime)
    
    def writeTranslator(self, translator, path=None):
        if path is None: path = self.path # Normal non-debug behaviour
        if not os.path.exists(path):
            os.mkdir(path)
        data = translator.getPatchData()
        for name in data:
            fn = name + '.txt'
            fullfn = os.path.join(path, fn)
            with codecs.open(fullfn, 'w', encoding='utf-8') as f:
                f.write(data[name])
                
    def patchDataFiles(self):
        raise Exception('This method needs to be overridden')
                
    def genPatchDataFiles(self):
        self.patchDataFiles = [x for x in self.patchDataFiles()]
    
    def filePaths(self):
        for dir, subdir, files in os.walk(self.path):
            for fn in files:
                fpath = os.path.join(dir, fn)
                yield fpath
                
    def fileDirs(self):
        for dr, subdirs, fns in os.walk(self.path):
            yield dr

    def getNonPatchedList(self):
        ret = []
        for fpath in self.filePaths():
            name = os.path.relpath(fpath, self.path) #fpath.replace(self.path + os.sep, '')
            ret.append(name)
        return ret
    
    def doFullPatches(self, inpath, outpath):
        # TODO: Not a good way of doing it. Should make it into a seperate function
        # and get arguments. 
        for fn in self.filePaths():
            name = fn.replace(self.path + os.sep, '')
            infn = os.path.join(inpath, name)
            if os.path.isfile(infn):
                outfn = os.path.join(outpath, name)
                if os.path.isdir(outfn):
                    shutil.rmtree(outfn)
                shutil.copy(fn, outfn)
                
class FilePatcherv3(FilePatcher):
    def patchDataFiles(self):
        raise Exception('This needs to be made compliant with the final version of v3 patches')
        for fn in self.filePaths():
            if fn.endswith('.txt'):
                try:
                    with codecs.open(fn, 'r', encoding='utf-8') as f:
                        header = '# RPGMAKER TRANS PATCH'
                        x = f.read(len(header))
                        if x.startswith(header):
                            yield fn
                except UnicodeError:
                    pass
    
def sniffv3(path):
    if os.path.isdir(path):
        path = os.path.join(path, 'rpgmktranspatch')
    if os.path.isfile(path) and path.endswith('rpgmktranspatch'):
        with open(path, 'r') as f:
            versionString = f.read()
        if versionString == 'RPGMAKER TRANS PATCH v3.0':
            return True
    return False

#filePatchers[sniffv3] = FilePatcherv3

class FilePatcherv2(FilePatcher):
    translatorClass = 'Translator2kv2'
    def patchDataFiles(self):
        # TODO: Move this down into subclasses: reason - may not be constant amongst versions.
        for fn in os.listdir(self.path):
            if fn.lower().endswith('.txt'):
                try:
                    with codecs.open(fn, 'r', encoding='utf-8') as f:
                        header = '# RPGMAKER TRANS PATCH'
                        x = f.read(len(header))
                        if x.startswith(header):
                            yield fn
                except UnicodeError:
                    pass
                
def sniffv2(path):
    if os.path.isdir(path):
        path = os.path.join(path, 'rpgmktranspatch')
    if os.path.isfile(path):
        with open(path, 'r') as f:
            versionString = f.read()
        if not versionString.strip():
            return True
    #if os.path.isfile(path) and path.endswith('rpgmktranspatch'):
    #    path = os.path.split(path)[0]
    #if os.path.isdir(path):
    #    path = os.path.join(path, 'Map0001.txt')
    #if os.path.isfile(path):
    #    with open(path, 'r') as f:
    #        content = f.read()
    #    if content.startswith('# RPGMAKER TRANS PATCH FILE VERSION 2.0'):
    #        return True
    return False         
        
filePatchers[sniffv2] = FilePatcherv2
DEFAULT = FilePatcherv2

def getFilePatcher(path):
    for x in filePatchers:
        if x(path):
            return filePatchers[x](path)
    if not os.path.exists(path):
        os.mkdir(path)
    return DEFAULT(path)
    
if __name__ == '__main__':
    x = getFilePatcher('/home/habisain/tr/RyonaRPG_patch')
    y = x.makeTranslator()
    print type(y)
    x.writeTranslator(y, path='/home/habisain/tr/RyonaRPG_patch2')
    #x = FilePatcher('/home/habisain/tr/RyonaRPG_patch')
    #print x.getNonPatchedList()
    #x.doFullPatches('/home/habisain/tr/RyonaRPG_translated')
