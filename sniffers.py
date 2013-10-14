'''
Created on 8 Oct 2013

@author: habisain
'''

import os.path
from collections import namedtuple
from errorhook import errorWrap

SNIFFERS = {}

SniffedType = namedtuple('SniffedType', ['maintype', 'subtype'])
RPG2k = SniffedType('GAME', 'RPG2k')
TransLoc = SniffedType('TRANS', 'TransLocation')
def sniffer(name):
    global SNIFFERS
    def f(func):
        func = errorWrap(func)
        SNIFFERS[name] = func
        return func
    return f

def checkForFiles(path, req):
    if not os.path.isdir(path): 
        return False
    subdirlist = os.listdir(path)
    for fn in subdirlist:
        fn = fn.upper()
        if fn in req: req[fn] = not req[fn]
    return all([req[x] for x in req])

@sniffer(RPG2k)
def sniff2kGame(path):
    req = {'RPG_RT.LDB': False,
           'RPGMKTRANSPATCH': True,
           'RPGMKTRANSLATED': True,}
    return checkForFiles(path, req)

@sniffer(TransLoc)
def sniffTransLoc(path):
    req = {'RPG_RT.LDB': False,
           'RPGMKTRANSPATCH': True,
           'RPGMKTRANSLATED': False,}
    return checkForFiles(path, req)

def sniff(path):
    for name, sniffer in SNIFFERS.items():
        if sniffer(path): 
            return name
    return False

def sniffAll(path):
    if os.path.isdir(path):
        return [x for x in ((sniff(path2), path2) for path2 in 
                (os.path.join(path, fn) for fn in os.listdir(path)))
                if x[0] is not False]
    elif os.path.isfile(path):
        return [x for x in ((sniff(path), path)) if x[0] is not False]
    else:
        return []
            

if __name__ == '__main__':
    import sys
    print sniff(sys.argv[-1])
    