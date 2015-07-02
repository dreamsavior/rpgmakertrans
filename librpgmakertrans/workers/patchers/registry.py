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
from ..sniffers import sniffer, sniff, SniffedType


class FilePatchv2(SniffedType):
    """Sniffed type for FilePatch v2"""
    maintype, subtypes = 'PATCH', ['v2', 'update']

class FilePatchv3(SniffedType):
    """Sniffed type for FilePatch v3"""
    def __init__(self, path=None, extraData=None):
        if extraData is None: extraData = {}
        bannerfn = os.path.join(path, 'banner.html')
        if os.path.isfile(bannerfn):
            with open(bannerfn) as f:
                extraData['banner.html'] = f.read() 
        super().__init__(path, extraData)
        
    maintype, subtypes = 'PATCH', ['v3', 'update']

class ZipPatchv2(SniffedType):
    """Sniffed type for ZipPatchv2"""
    maintype, subtypes = 'PATCH', ['v2', 'use']

class ZipPatchv3(SniffedType):
    """Sniffed type for ZipPatchv3"""
    maintype, subtypes = 'PATCH', ['v3', 'use']

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
