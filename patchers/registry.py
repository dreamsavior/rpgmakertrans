'''
Created on 5 Oct 2013

@author: habisain
'''
import os.path
from sniffers import sniffer, sniff, SniffedType

FilePatchv2 = SniffedType('PATCH', 'update')
ZipPatchv2 = SniffedType('PATCH', 'use')
NewDir = SniffedType('PATCH', 'create')

patchers = {}

def patcherSniffer(name, patcherclassname):
    def f(func):
        func = sniffer(name)(func)
        patchers[name] = patcherclassname
        return func
    return f

@patcherSniffer(NewDir, None)
def newDirSniffer(path):
    return not os.path.exists(path)

def getClassName(path):
    pathtype = sniff(path)
    if pathtype in patchers:
        return patchers[pathtype]
    else:
        return None