'''
Created on 4 Oct 2013

@author: habisain
'''

from .basepatcher import BasePatch
import zipfile
import os.path
from .registry import patcherSniffer, ZipPatchv2
from ..fileops import winescape, getmtime, WinOpen
SEPERATORS = '\\/' 

class ZIPPatcher(BasePatch):
    def __init__(self, path, *args, **kwargs):
        self.zip = zipfile.ZipFile(winescape(path))
        self.mtime = getmtime(path)
        super(ZIPPatcher, self).__init__(path, *args, **kwargs)
    
    def patchIsWritable(self):
        return False
    
    def loadPatchData(self):
        data = {}
        for fn in self.patchDataFiles:
            zfile = self.zip.open(fn)
            raw = zfile.read(2**22)
            dec = raw.decode('utf-8')
            name = fn.partition(self.root)[2].strip(SEPERATORS).rpartition('.')[0].lower()
            data[name] = dec
        return data, self.mtime

    def writePatchData(self, data):
        pass
    
    def toOSFileStyle(self, path):
        for sep in SEPERATORS:
            path = path.replace(sep, os.path.sep)
        return path
    
    def getAssetNames(self):
        return [self.toAssetName(x) for x in self.assetFiles]
        
    def toAssetName(self, string):
        return self.toOSFileStyle(string.partition(self.root)[2].strip(SEPERATORS)) 
    
    def makeDir(self, dirname):
        if os.path.exists(dirname):
            if os.path.isfile(dirname):
                raise Exception('Directory name conflicts with patch file name')
        else:
            os.makedirs(dirname)

    def doFullPatches(self, outpath, translator, mtimes, newmtimes):
        for d in self.patchdirs:
            outdir = os.path.join(outpath, self.toAssetName(d))
            self.makeDir(outdir)
        for fn in self.assetFiles:
            outfn = os.path.join(outpath, self.toAssetName(fn))
            outfntime = mtimes.get(outfn, None)
            if outfntime != self.mtime:
                dirname = os.path.split(outfn)[0]
                self.makeDir(dirname)
                z = self.zip.open(fn)
                data = z.read(2**20)
                with WinOpen(outfn, 'wb') as f:
                    while data:
                        f.write(data)
                        data = z.read(2**20)
            newmtimes[outfn] = self.mtime

    
class ZIPPatcherv2(ZIPPatcher):
    translatorClass = 'Translator2kv2'
    def categorisePatchFiles(self):
        
        contents = self.zip.namelist()
        transpatches = [x for x in contents if x.endswith('RPGMKTRANSPATCH')]
        if len(transpatches) > 1:
            raise Exception('ZIP file contains more than one RPGMKTRANSPATCH file; cannot determine root')
        self.root = transpatches[0].rpartition('RPGMKTRANSPATCH')[0]
        patchbits = [x for x in contents if x.startswith(self.root)]
        patchfiles = [x for x in patchbits if not any(x.endswith(sep) for sep in SEPERATORS)]
        self.patchdirs = [x for x in patchbits if x not in patchfiles]
         
        rootfiles = [x for x in patchfiles if 
            all([y not in x.partition(self.root)[2] for y in SEPERATORS])]
        
        self.assetFiles = []
        self.patchDataFiles = []
        for fn in patchfiles:
            if fn.lower().endswith('.txt') and fn in rootfiles:
                try:
                    header = '# RPGMAKER TRANS PATCH'
                    z = self.zip.open(fn)
                    raw = z.read(2**22)
                    dec = raw.decode('utf-8')
                    if dec.startswith(header):
                        self.patchDataFiles.append(fn)
                    else:
                        self.assetFiles.append(fn)
                except UnicodeError:                
                    self.assetFiles.append(fn)
            else:
                if not fn.endswith('RPGMKTRANSPATCH'):
                    self.assetFiles.append(fn)

@patcherSniffer(ZipPatchv2, 'ZIPPatcherv2')
def sniffzipv2(path):
    if os.path.isfile(path) and zipfile.is_zipfile(path):
        z = zipfile.ZipFile(winescape(path))
        contents = z.namelist()
        transpatches = [x for x in contents if x.endswith('RPGMKTRANSPATCH')]
        if len(transpatches) == 1:
            f = z.open(transpatches[0])
            x = f.read()
            if not x.strip():
                return path
    return False
     
if __name__ == '__main__':
    zipfn = '/home/habisain/tr/cr_p.zip'
    print(sniffzipv2(zipfn))
    x = ZIPPatcherv2(zipfn, None)
    x.doFullPatches('/home/habisain/tr/cr_pzip_test', None, {}, {})
    
