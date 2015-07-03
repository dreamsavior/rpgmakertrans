"""
registry
********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2015
:license: GNU Public License version 3

Provides a repository for sniffer functions which can
inform which type of backend to use.
"""
import os.path
import zipfile
from ..sniffers import sniffer, sniff, SniffedType


class FilePatchv2(SniffedType):
    """Sniffed type for FilePatch v2"""
    maintype, subtypes = 'PATCH', ['v2', 'update']

class FilePatchv3(SniffedType):
    """Sniffed type for FilePatch v3"""
    def __init__(self, path=None):
        super().__init__(path)
        bannerfns = ['banner.html', 'banner.txt']
        for fn in os.listdir(self.canonicalpath):
            if fn.lower() in bannerfns:
                with open(os.path.join(self.canonicalpath, fn)) as f:
                    self.extraData[fn.lower()] = f.read()
        
    maintype, subtypes = 'PATCH', ['v3', 'update']

class ZipPatchv2(SniffedType):
    """Sniffed type for ZipPatchv2"""
    maintype, subtypes = 'PATCH', ['v2', 'use']

class ZipPatchv3(SniffedType):
    """Sniffed type for ZipPatchv3"""
    maintype, subtypes = 'PATCH', ['v3', 'use']
    def __init__(self, path=None):
        super().__init__(path)
        bannerfns = ['banner.html', 'banner.txt']
        if os.path.isfile(self.canonicalpath) and zipfile.is_zipfile(self.canonicalpath):
            z = zipfile.ZipFile(self.canonicalpath)
            for fn in z.namelist():
                for bannerfn in bannerfns:
                    if fn.lower().endswith(bannerfn):
                        with z.open(fn) as f:
                            self.extraData[bannerfn] = f.read(1e6).decode('utf-8')
            

class NewDir(SniffedType):
    """Sniffed type for an empty directory"""
    maintype, subtypes = 'PATCH', ['create']

patchers = {}


def patcherSniffer(sniffedtype, patcherclassname):
    """Decorator to make something into a patcher sniffer"""
    def wrappedFunc(func):
        func = sniffer(sniffedtype)(func)
        name = sniffedtype
        if name in patchers:
            raise Exception('Clashed name %s' % name)
        patchers[name] = patcherclassname
        return func
    return wrappedFunc

@patcherSniffer(NewDir, None)
def newDirSniffer(path):
    """Sniffer for new directories"""
    if not os.path.exists(path) or (
            os.path.isdir(path) and len(
            os.listdir(path)) == 0):
        return path
    else:
        return False

def getClassName(path):
    """Get the name of name of the class of the appropriate patcher
    for a given path (used to instantiate on a multiprocessing manager)"""
    pathtype = sniff(path, positives=['PATCH'])
    if len(pathtype) == 1:
        pathtype = pathtype[0]
    else:
        raise Exception('Could not work out an ambiguous patcher format')
    if pathtype is not False and type(pathtype) in patchers:
        return patchers[type(pathtype)]
    else:
        return None
