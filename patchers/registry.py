'''
Created on 5 Oct 2013

@author: habisain
'''

from sniffers import sniffer, sniff, SniffedType

FilePatchv2 = SniffedType('PATCH', 'FilePatchv2')
ZipPatchv2 = SniffedType('PATCH', 'ZipPatchv2')


patchers = {}

def patcherSniffer(name, patcherclassname):
    def f(func):
        func = sniffer(name)(func)
        patchers[name] = patcherclassname
        return func
    return f
        
def getClassName(path):
    pathtype = sniff(path)
    if pathtype in patchers:
        return patchers[pathtype]
    else:
        return None