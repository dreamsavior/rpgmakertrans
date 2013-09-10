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
from translator.translatorbase import TranslatorManager

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
        for fn in os.listdir(self.path):
            if fn.lower().endswith('.txt'):
                fullfn = os.path.join(self.path, fn)
                name = fn.rpartition('.')[0].lower()
                mtime = max(mtime, os.path.getmtime(fullfn))
            try:
                with codecs.open(fullfn, 'r', encoding='utf-8') as f:
                    data[name] = f.read()
            except UnicodeError:
                pass # Not a valid RPGMaker Trans file, evidently.
        return getattr(self.translatorManager, type(self).translatorClass)(data, mtime)
    
    def __filePaths(self):
        for dir, subdir, files in os.walk(self.path):
            for fn in files:
                fpath = os.path.join(dir, fn)
                yield fpath
                
    def __fileDirs(self):
        for dr, subdirs, fns in os.walk(self.path):
            yield dr

    def getNonPatchedList(self):
        ret = []
        for fpath in self.__filePaths():
            name = os.path.relpath(fpath, self.path) #fpath.replace(self.path + os.sep, '')
            ret.append(name)
        return ret
    
    def doFullPatches(self, inpath, outpath): 
        for fn in self.__filePaths():
            name = fn.replace(self.path + os.sep, '')
            infn = os.path.join(inpath, name)
            if os.path.isfile(infn):
                outfn = os.path.join(outpath, name)
                if os.path.isdir(outfn):
                    shutil.rmtree(outfn)
                shutil.copy(fn, outfn)
                
class FilePatcherv3(FilePatcher):
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
    
def sniffv2(path):
    if os.path.isfile(path) and path.endswith('rpgmktranspatch'):
        path = os.path.split(path)[0]
    if os.path.isdir(path):
        path = os.path.join(path, 'Map0001.txt')
    if os.path.isfile(path):
        with open(path, 'r') as f:
            content = f.read()
        if content.startswith('# RPGMAKER TRANS PATCH FILE VERSION 2.0'):
            return True
    return False         
        
filePatchers[sniffv2] = FilePatcherv2

def getFilePatcher(path):
    for x in filePatchers:
        if x(path):
            return filePatchers[x](path)
            
if __name__ == '__main__':
    print type(getFilePatcher('/home/habisain/tr/RyonaRPG_patch').makeTranslator())
    #x = FilePatcher('/home/habisain/tr/RyonaRPG_patch')
    #print x.getNonPatchedList()
    #x.doFullPatches('/home/habisain/tr/RyonaRPG_translated')
