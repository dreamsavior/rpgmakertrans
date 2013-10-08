'''
Created on 8 Oct 2013

@author: habisain
'''

import os.path
from errorhook import errorWrap

GAMESNIFFERS = {}

def sniffer(name):
    global SNIFFERS
    def f(func):
        func = errorWrap(func)
        GAMESNIFFERS[name] = func
        return func
    return f
        
@sniffer('RPG2k')
def sniff2kGame(path):
    if not os.path.isdir(path): 
        return False
    subdirlist = os.listdir(path)
    req = {'RPG_RT.LDB': False,
           'RPGMKTRANSPATCH': True,
           'RPGMKTRANSLATED': True,}            
    for fn in subdirlist:
        fn = fn.upper()
        if fn in req: req[fn] = not req[fn]
    return all([req[x] for x in req])


def sniff(path):
    for name, sniffer in SNIFFERS.items():
        if sniffer(path): 
            return name
    return None

def sniffAll(path):
    if os.path.isdir(path):
        return [x for x in ((sniff(path2), path2) for path2 in 
                (os.path.join(path, fn) for fn in os.listdir(path)))
                if x[0] is not None]
    elif os.path.isfile(path):
        return [x for x in ((sniff(path), path)) if x[0] is not None]
    else:
        return []
            

if __name__ == '__main__':
    import sys
    print sniffGame(sys.argv[-1])
    