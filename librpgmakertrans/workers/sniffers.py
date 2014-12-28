"""
sniffers
********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Provides sniffers, which are used by the API to determine the types
of various things.
"""

import os.path
import itertools
from collections import defaultdict

SNIFFERS = set()


class SniffedType:
    """Represents a sniffed type, along with where that object
    resides on disk"""
    maintype = None
    subtype = None

    def __init__(self, canonicalpath=None):
        if isinstance(canonicalpath, type(self)):
            self.canonicalpath = canonicalpath.canonicalpath
        elif isinstance(canonicalpath, str):
            self.canonicalpath = canonicalpath
        else:
            raise Exception('Could not work out sniffed type data from a %s' %
                            str(type(canonicalpath)))

    def __str__(self):
        return '<%s:%s>' % (type(self).__name__, self.canonicalpath)

    def __getitem__(self, item):
        if isinstance(item, str):
            return self.__getattribute__(item)
        elif isinstance(item, int):
            if item == 0:
                return self.maintype
            elif item == 1:
                return self.subtype
            elif item == 2:
                return self.canonicalpath
        else:
            raise Exception('Invalid index %s' % str(item))

class RPG2k(SniffedType):
    """Sniffed type for an untranslated target game"""
    maintype, subtype = 'GAME', 'RPG2k'

class TransLoc(SniffedType):
    """Sniffed type for a translated game"""
    maintype, subtype = 'TRANS', 'RPG2k][translated'

class NewDirTransLoc(SniffedType):
    """Sniffed Type for a new directory"""
    maintype, subtype = 'TRANS', 'create'

class Sniffer:
    """Sniffer object; can be called with a path, and
    if it matches the sniffer function it returns the appropriate
    sniffer type."""
    def __init__(self, sniffedType, func):
        self.sniffedType = sniffedType
        self.func = func
        global SNIFFERS
        SNIFFERS.add(self)
        self.maintype = self.sniffedType.maintype

    def __call__(self, path):
        path = self.func(path)
        if path:
            return self.sniffedType(path)
        else:
            return False

def sniffer(sniffedType):
    """Sniffer decorator; create Sniffer objects from functions"""
    def f(func):
        return Sniffer(sniffedType, func)
    return f

def checkForFiles(path, req):
    """Given a dictionary of filenames to true/false values (False being
    file required, True being file required to not exist), assert a path
    meets these required"""
    if not os.path.isdir(path):
        return False
    subdirlist = os.listdir(path)
    for fn in subdirlist:
        fn = fn.upper()
        if fn in req:
            req[fn] = not req[fn]
    if all([req[x] for x in req]):
        return path
    else:
        return False

@sniffer(RPG2k)
def sniff2kGame(path):
    """Sniffer for 2k games"""
    req = {'RPG_RT.LDB': False,
           'RPGMKTRANSPATCH': True,
           'RPGMKTRANSLATED': True, }
    return checkForFiles(path, req)

@sniffer(RPG2k)
def sniff2kGameFile(path):
    """Sniffer for 2k games, given a RPG_RT.EXE file"""
    if os.path.isfile(path) and path.upper().endswith('RPG_RT.EXE'):
        return sniff2kGame(os.path.split(path)[0])
    return False

@sniffer(TransLoc)
def sniffTransLoc(path):
    """Sniffer for a game translated by RPGMaker Trans"""
    req = {'RPG_RT.LDB': False,
           'RPGMKTRANSPATCH': True,
           'RPGMKTRANSLATED': False, }
    return checkForFiles(path, req)

@sniffer(TransLoc)
def sniffTransLocFile(path):
    """Sniffer for a game translated by RPGMaker Trans, given
    RPG_RT.EXE file"""
    if os.path.isfile(path) and path.upper().endswith('RPG_RT.EXE'):
        return sniffTransLoc(os.path.split(path)[0])
    return False

@sniffer(NewDirTransLoc)
def sniffNewDirTransLoc(path):
    """Sniffer for a new directory"""
    if ((os.path.isdir(path) and len(os.listdir(path)) == 0) or
        (not os.path.exists(path))):
        return path
    return False

def sniff(path, positives=None, negatives=None, conflicts=None):
    """Run all sniffers on a given path"""
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
            if result:
                return []
        elif sniffer.maintype in positives:
            result = sniffer(path)
            if result is not False:
                results[sniffer.maintype].append(result)
    for maintype in conflicts:
        if maintype in results:
            delBases = [x.canonicalpath for x in results[maintype]]
            for conflicttype in conflicts[maintype]:
                results[conflicttype] = [
                    x for x in results[conflicttype] if x.canonicalpath not in delBases]
    return list(itertools.chain.from_iterable(list(results.values())))

def sniffAll(path):
    """Run all sniffers on given path; if directory, everything in directory"""
    if os.path.isdir(path):
        pathsToSniff = [sniff(path2) for path2 in
                        (os.path.join(path, fn) for fn in os.listdir(path))]
        return list(itertools.chain.from_iterable(pathsToSniff))
    elif os.path.isfile(path):
        return sniff(path)
    else:
        return []

if __name__ == '__main__':
    import sys
    print(','.join(str(x) for x in sniff(sys.argv[-1])))
