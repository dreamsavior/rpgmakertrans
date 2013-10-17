'''
Created on 8 Oct 2013

@author: habisain
'''

import os.path
from errorhook import ErrorMeta

SNIFFERS = set()

class SniffedType(object):
    maintype = None
    subtype = None
    def __init__(self, canonicalpath=None):
        self.canonicalpath = canonicalpath
        
    def __str__(self):
        return '<%s:%s:%s>' % (type(self).maintype, type(self).subtype, self.canonicalpath)
        
    def __getitem__(self, item):
        if isinstance(item, str):
            return self.__getattribute__(item)
        elif isinstance(item, int):
            if item == 0: return self.maintype
            elif item == 1: return self.subtype
            elif item == 2: return self.canonicalpath
        else:
            raise Exception('Invalid index %s' % str(item))

def SniffedTypeCons(name, maintypeN, subtypeN):
    class SniffedTypeB(SniffedType):
        maintype = maintypeN
        subtype = subtypeN
    SniffedTypeB.__name__ = name
    return SniffedTypeB

class RPG2k(SniffedType): maintype, subtype = 'GAME', 'RPG2k'
class TransLoc(SniffedType): maintype, subtype = 'TRANS', 'overwrite'
class NewDirTransLoc(SniffedType): maintype, subtype = 'TRANS', 'create'

class Sniffer(object):
    __metaclass__ = ErrorMeta
    def __init__(self, sniffedType, func):
        self.sniffedType = sniffedType
        self.func = func
        global SNIFFERS
        SNIFFERS.add(self)
        self.maintype = self.sniffedType.maintype
        
    def __call__(self, path):
        path = self.func(path)
        if path: return self.sniffedType(path)
        else: return False
        
def sniffer(sniffedType):
    def f(func):
        return Sniffer(sniffedType, func)
    return f

#def sniffer(sniffedType, func):
#    global SNIFFERS
#    class Sniffer(object):
#        
#        sniffedType = sniffedType
#        def __call__(self, path):
#            path = func(path)
#            if path: return type(self).sniffedType(path)
#            else: return False
#    x = Sniffer()
#    SNIFFERS.add(x)
#    return func

def checkForFiles(path, req):
    if not os.path.isdir(path): 
        return False
    subdirlist = os.listdir(path)
    for fn in subdirlist:
        fn = fn.upper()
        if fn in req: req[fn] = not req[fn]
    if all([req[x] for x in req]):
        return path
    else:
        return False 

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

@sniffer(NewDirTransLoc)
def sniffNewDirTransLoc(path):
    if (os.path.isdir(path) and len(os.listdir(path)) == 0) or (not os.path.exists(path)):
        return path
    return False

def sniff(path):
    for sniffer in SNIFFERS:
        result = sniffer(path)
        if result is not False: 
            return result
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
    