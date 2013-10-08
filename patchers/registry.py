'''
Created on 5 Oct 2013

@author: habisain
'''

from sniffers import sniffer, sniff

patchers = {}

def patcherSniffer(name, patcherclassname):
    def f(func):
        func = sniffer(name)(func)
        patchers[name] = patcherclassname
        
def getClassName(path):
    pathtype = sniff(path)
    if pathtype in patchers:
        return patchers[pathtype]
    else:
        return None