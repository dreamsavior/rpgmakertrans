'''
Created on 4 Oct 2013

@author: habisain
'''

from basepatcher import BasePatch
import zipfile
import os.path

SEPERATORS = '\\/' 

class ZIPPatcher(BasePatch):
    def __init__(self, path, coms):
        self.zip = zipfile.ZipFile(path)
        self.mtime = os.path.getmtime(path)
        super(ZIPPatcher, self).__init__(path, coms)
    
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
        
    def doFullPatches(self, outpath, translator, mtimes, newmtimes):
        for fn in self.assetFiles:
            outfn = os.path.join(outpath, self.toAssetName(fn))
            outfntime = mtimes.get(outfn, None)
            if outfntime != self.mtime:
                dirname = os.path.split(outfn)[0]
                if os.path.exists(dirname):
                    if os.path.isfile(dirname):
                        raise Exception('Directory name conflicts with patch file name')
                else:
                    os.makedirs(dirname)
                z = self.zip.open(fn)
                data = z.read(2**20)
                with open(outfn, 'wb') as f:
                    while data:
                        f.write(data)
                        data = z.read(2**20)
            newmtimes[outfn] = self.mtime

    
class ZIPPatcherv2(ZIPPatcher):
    def categorisePatchFiles(self):
        
        contents = self.zip.namelist()
        transpatches = [x for x in contents if x.endswith('RPGMKTRANSPATCH')]
        if len(transpatches) > 1:
            raise Exception('ZIP file contains more than one RPGMKTRANSPATCH file; cannot determine root')
        self.root = transpatches[0].rpartition('RPGMKTRANSPATCH')[0]
        patchfiles = [x for x in contents if x.startswith(self.root) and not any(x.endswith(sep) for sep in SEPERATORS)]
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
                
if __name__ == '__main__':
    zipfn = '/home/habisain/tr/cr_p.zip'
    x = ZIPPatcherv2(zipfn, None)
    x.doFullPatches('/home/habisain/tr/cr_pzip_test', None, {}, {})
    
