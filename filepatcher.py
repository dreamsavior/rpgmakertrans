'''
Created on 18 Apr 2013

@author: habisain
'''


import os, os.path, shutil

from resource import BasePatch
from errorhook import ErrorMeta

filePatchers = {}
class FilePatcher(BasePatch):
    
    def __init__(self, path):
        super(FilePatcher, self).__init__(path)
        if os.path.isfile(self.path):
            self.path = os.path.split(path)[0]
            
    def makeTranslator(self):
        raise Exception('Not implemented')
    
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

filePatchers[sniffv3] = FilePatcherv3

class FilePatcherv2(FilePatcher):
    pass
    
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
    print getFilePatcher('/home/habisain/tr/RyonaRPG_patch').getNonPatchedList()
    #x = FilePatcher('/home/habisain/tr/RyonaRPG_patch')
    #print x.getNonPatchedList()
    #x.doFullPatches('/home/habisain/tr/RyonaRPG_translated')
