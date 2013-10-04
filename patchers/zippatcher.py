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
        super(ZIPPatcher, self).__init__(path, coms)
    
    def loadPatchData(self):
        data = {}
        mtime = os.path.getmtime(self.path)
        for fn in self.patchDataFiles:
            zfile = self.zip.open(fn)
            raw = zfile.read(2**22)
            dec = raw.decode('utf-8')
            name = fn.partition(self.root)[2].strip(SEPERATORS).rpartition('.')[0].lower()
            data[name] = dec
        return data, mtime

    def writePatchData(self, data):
        pass
    
class ZIPPatcherv2(ZIPPatcher):
    def categorisePatchFiles(self):
        
        contents = self.zip.namelist()
        transpatches = [x for x in contents if x.endswith('RPGMKTRANSPATCH')]
        if len(transpatches) > 1:
            raise Exception('ZIP file contains more than one RPGMKTRANSPATCH file; cannot determine root')
        self.root = transpatches[0].rpartition('RPGMKTRANSPATCH')[0]
        patchfiles = [x for x in contents if x.startswith(self.root)]
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
                self.assetFiles.append(fn)
                
if __name__ == '__main__':
    zipfn = '/home/habisain/tr/rrpg_patch.zip'
    x = ZIPPatcherv2(zipfn, None)
    
