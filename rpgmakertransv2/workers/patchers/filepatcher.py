'''
Created on 18 Apr 2013

@author: habisain
'''

import os.path
import codecs
from .basepatcher import BasePatch
from ..filecopier2 import copyfiles
from .registry import patcherSniffer, FilePatchv2

def listdir(path):
    return [os.path.normcase(x) for x in os.listdir(path)]

class FilePatcher(BasePatch):
    def __init__(self, path, *args, **kwargs):
        super(FilePatcher, self).__init__(path, *args, **kwargs)
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
        patchmarkerfn = os.path.join(self.path, 'RPGMKTRANSPATCH')
        if not os.path.exists(patchmarkerfn):
            if os.path.isdir(patchmarkerfn):
                raise Exception('Can\'t create patch marker file due to directory name conflict')
            with open(patchmarkerfn, 'w') as f:
                f.write('')
        for name in data:
            fn = name + '.txt'
            fullfn = os.path.join(self.path, fn)
            with codecs.open(fullfn, 'w', encoding='utf-8') as f:
                f.write(data[name])
                    
    def allPaths(self):
        for dr, _, files in os.walk(self.path):
            if dr != self.path: yield dr
            for fn in files:
                if not fn.endswith('RPGMKTRANSPATCH'):
                    fpath = os.path.normcase(os.path.join(dr, fn))
                    yield fpath
                
    def fileDirs(self):
        for dr, _, _ in os.walk(self.path):
            yield dr
            
    def getAssetNames(self):
        return [os.path.relpath(fn, self.path) for fn in self.assetFiles]
    
    def getNonCopyNames(self):
        return [os.path.relpath(fn, self.path) for fn in self.patchDataFiles] + ['rpgmktranspatch']
    
    def doFullPatches(self, outpath, translator, mtimes, newmtimes):
        self.coms.send('waitUntil', 'dirsCopied', 'copier', copyfiles, 
            indir=self.path, outdir=outpath, ignoredirs=[], ignoreexts=[], 
            ignorefiles=self.getNonCopyNames(), comsout='outputcoms', translator=translator,
            mtimes=mtimes, newmtimes=newmtimes, progresssig='patchdata',
            dirssig=None 
            )
                
class FilePatcherv2(FilePatcher):
    translatorClass = 'Translator2kv2'
    def categorisePatchFiles(self):
        """Work out if a file is an asset or patch data"""
        self.assetFiles = []
        self.patchDataFiles = []
        rootls = set(listdir(self.path))
        for fn in self.allPaths():
            if fn.lower().endswith('.txt') and os.path.normcase(os.path.split(fn)[1]) in rootls and os.path.isfile(fn):
                try:
                    with codecs.open(fn, 'r', encoding='utf-8') as f:
                        header = '# RPGMAKER TRANS PATCH'
                        x = f.read(len(header))
                        x = x.replace('\r', '')
                        if x.startswith(header):
                            self.patchDataFiles.append(fn)
                        else:
                            self.assetFiles.append(fn)
                except UnicodeError:
                    self.assetFiles.append(fn)
            else:
                if not fn.endswith('RPGMKTRANSPATCH'):
                    self.assetFiles.append(fn)
                
@patcherSniffer(FilePatchv2, 'FilePatcherv2')
def sniffv2(path):
    if os.path.isdir(path):
        cands = [x for x in listdir(path) if x.lower() == 'rpgmktranspatch']
        if len(cands) == 1:
            path = os.path.join(path, cands[0])
    elif not path.lower().endswith('rpgmktranspatch'):
        return False
    if os.path.isfile(path):
        with open(path, 'r') as f:
            versionString = f.read()
        if not versionString.strip():
            return os.path.split(path)[0]
    return False         

if __name__ == '__main__':
    from ...controllers.sender import Sender
    errout, coms = Sender(), Sender()
    tp = """C:\\tr\\RyonaRPG_patch"""
    x = FilePatcherv2(tp, coms, errout)
    