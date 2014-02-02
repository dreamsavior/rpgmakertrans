'''
Created on 8 Oct 2013

@author: habisain
'''

import os.path, itertools
from fileops import (isdir, listdir, isfile, pathexists)
from collections import defaultdict
from errorhook import ErrorMeta

SNIFFERS = set()

class SniffedType(object):
    maintype = None
    subtype = None
    def __init__(self, canonicalpath=None):
        if isinstance(canonicalpath, type(self)):
            self.canonicalpath = canonicalpath.canonicalpath
        elif isinstance(canonicalpath, str):
            self.canonicalpath = canonicalpath
        else:
            raise Exception('Could not work out sniffed type data from a %s' % str(type(canonicalpath)))
        
    def __str__(self):
        return '<%s:%s>' % (type(self).__name__, self.canonicalpath)
        
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
class TransLoc(SniffedType): maintype, subtype = 'TRANS', 'RPG2k][translated'
class NewDirTransLoc(SniffedType): maintype, subtype = 'TRANS', 'create'

class Sniffer(object, metaclass=ErrorMeta):
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
    if not isdir(path): 
        return False
    subdirlist = listdir(path)
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

@sniffer(RPG2k)
def sniff2kGameFile(path):
    if isfile(path) and path.upper().endswith('RPG_RT.EXE'):
        return sniff2kGame(os.path.split(path)[0])
    return False

@sniffer(TransLoc)
def sniffTransLoc(path):
    req = {'RPG_RT.LDB': False,
           'RPGMKTRANSPATCH': True,
           'RPGMKTRANSLATED': False,}
    return checkForFiles(path, req)

@sniffer(TransLoc)
def sniffTransLocFile(path):
    if isfile(path) and path.upper().endswith('RPG_RT.EXE'):
        return sniffTransLoc(os.path.split(path)[0])
    return False

@sniffer(NewDirTransLoc)
def sniffNewDirTransLoc(path):
    if (isdir(path) and len(listdir(path)) == 0) or (not pathexists(path)):
        return path
    return False

def sniff(path, positives=None, negatives=None, conflicts=None):
    if positives is None:
        positives = 'GAME', 'PATCH', 'TRANS'
    if negatives is None:
        negatives = ()
    if conflicts is None:
        conflicts = {'GAME': ['TRANS']}
    results = defaultdict(list)
    for sniffer in SNIFFERS:
        if sniffer.maintype in negatives:
            result = sniffer(path)
            if result: return []
        elif sniffer.maintype in positives:
            result = sniffer(path)
            if result is not False:
                results[sniffer.maintype].append(result)
    for maintype in conflicts:
        if maintype in results:
            delBases = [x.canonicalpath for x in results[maintype]]
            for conflicttype in conflicts[maintype]:
                results[conflicttype] = [x for x in results[conflicttype] if x.canonicalpath not in delBases]
    return list(itertools.chain(*list(results.values())))

def sniffAll(path):
    if isdir(path):
        return list(itertools.chain(*[sniff(path2) for path2 in (os.path.join(path, fn) for fn in listdir(path))]))
    elif isfile(path):
        return sniff(path)
    else:
        return []
            

if __name__ == '__main__':
    import sys
    print(','.join(str(x) for x in sniff(sys.argv[-1])))
    