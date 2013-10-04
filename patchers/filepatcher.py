'''
Created on 18 Apr 2013

@author: habisain
'''

import os, os.path
import codecs
from basepatcher import BasePatch
from filecopier2 import copyfiles

filePatchers = {}
class FilePatcher(BasePatch):
    def __init__(self, path, coms):
        super(FilePatcher, self).__init__(path, coms)
        if os.path.isfile(self.path):
            self.path = os.path.split(path)[0]
    
    def loadPatchData(self):
        data = {}
        mtime = 0
        for fn in self.patchDataFiles:
            name = os.path.split(fn)[1].rpartition('.')[0].lower()
            mtime = max(mtime, os.path.getmtime(fn))
            with codecs.open(fn, 'r', encoding='utf-8') as f:
                data[name] = f.read()
        return data, mtime
        
    def writePatchData(self, data):
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        for name in data:
            fn = name + '.txt'
            fullfn = os.path.join(self.path, fn)
            with codecs.open(fullfn, 'w', encoding='utf-8') as f:
                f.write(data[name])
                    
    def allPaths(self):
        for dr, _, files in os.walk(self.path):
            if dr != self.path: yield dr
            for fn in files:
                fpath = os.path.join(dr, fn)
                yield fpath
                
    def fileDirs(self):
        for dr, _, _ in os.walk(self.path):
            yield dr
            
    def getAssetNames(self):
        return [os.path.relpath(fn, self.path) for fn in self.assetFiles]
    
    def doFullPatches(self, outpath, translator, mtimes, newmtimes):
        self.coms.send('waitUntil', 'dirsCopied', 'copier', copyfiles, 
            indir=self.path, outdir=outpath, ignoredirs=[], ignoreexts=[], 
            ignorefiles=self.patchDataFiles, comsout='comsout', translator=translator,
            mtimes=mtimes, newmtimes=newmtimes, progresssig='patchdata',
            dirssig=None 
            )
                
class FilePatcherv3(FilePatcher):
    def patchDataFiles(self):
        raise Exception('This needs to be made compliant with the final version of v3 patches')
        for fn in self.allPaths():
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
    def categorisePatchFiles(self):
        """Work out if a file is an asset or patch data"""
        self.assetFiles = []
        self.patchDataFiles = []
        rootls = set(os.listdir(self.path))
        for fn in self.allPaths():
            if fn.lower().endswith('.txt') and fn in rootls and os.path.isfile(fn):
                try:
                    with codecs.open(fn, 'r', encoding='utf-8') as f:
                        header = '# RPGMAKER TRANS PATCH'
                        x = f.read(len(header))
                        if x.startswith(header):
                            self.patchDataFiles.append(fn)
                        else:
                            self.assetFiles.append(fn)
                except UnicodeError:
                    self.assetFiles.append(fn)
            else:
                if not fn.endswith('RPGMKTRANSPATCH'):
                    self.assetFiles.append(fn)
                
                
def sniffv2(path):
    if os.path.isdir(path):
        path = os.path.join(path, 'rpgmktranspatch')
    if os.path.isfile(path):
        with open(path, 'r') as f:
            versionString = f.read()
        if not versionString.strip():
            return True
    return False         
        
filePatchers[sniffv2] = 'FilePatcherv2'
DEFAULT = FilePatcherv2

def getFilePatcher(path, coms):
    for x in filePatchers:
        if x(path):
            return filePatchers[x](path, coms)
    if not os.path.exists(path):
        os.mkdir(path)
    return DEFAULT(path, coms)
    
