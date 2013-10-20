'''
Created on 5 Oct 2013

@author: habisain
'''
import os.path
from sniffers import sniffer, sniff, SniffedType

class FilePatchv2(SniffedType): maintype, subtype = 'PATCH', 'v2][update'
class ZipPatchv2(SniffedType): maintype, subtype = 'PATCH', 'v2][use'
class NewDir(SniffedType): maintype, subtype = 'PATCH', 'create'

patchers = {}

def patcherSniffer(sniffedtype, patcherclassname):
    def f(func):
        func = sniffer(sniffedtype)(func)
        name = sniffedtype
        if name in patchers: raise Exception('Clashsed name %s' % name)
        patchers[name] = patcherclassname
        return func
    return f

@patcherSniffer(NewDir, None)
def newDirSniffer(path):
    if not os.path.exists(path) or (os.path.isdir(path) and len(os.listdir(path) == 0)):
        return path
    else:
        return False

def getClassName(path):
    pathtype = sniff(path, positives=['PATCH'])
    if len(pathtype) == 1: pathtype = pathtype[0]
    else: raise Exception('Could not work out an ambiguous patcher format')
    if pathtype is not False and type(pathtype) in patchers:
        return patchers[type(pathtype)]
    else:
        return None