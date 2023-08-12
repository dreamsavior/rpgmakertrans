"""
sniffers
********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2015
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
    subtypes = []

    def __init__(self, canonicalpath=None):
        """Initialise the SniffedType"""
        if isinstance(canonicalpath, type(self)):
            self.canonicalpath = canonicalpath.canonicalpath
        elif isinstance(canonicalpath, str):
            self.canonicalpath = canonicalpath
        else:
            raise Exception('Could not work out sniffed type data from a %s' %
                            str(type(canonicalpath)))
        if self.canonicalpath.endswith(os.path.sep):
            self.canonicalpath = self.canonicalpath.rstrip(os.path.sep)
        self.extraData = {}

    def __str__(self):
        """Return a string representation"""
        return '%s(%s)' % (type(self).__name__, self.canonicalpath)

    def __hash__(self):
        """Hash for sniffedtype"""
        return hash((type(self), self.canonicalpath))

    def __eq__(self, other):
        """Equality for sniffedTypes"""
        return (type(self) == type(other) and
                self.canonicalpath == other.canonicalpath)

    def __getitem__(self, item):
        """Tuple type access"""
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

class NewDirTransLoc(SniffedType):
    """Sniffed Type for a new directory"""
    maintype, subtypes = 'TRANS', ['create']

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

def translatedSniffer(translatedSniffedType, baseSniffer):
    """A hack-ish method to create a translated sniffer from a base sniffer"""
    def ret(path):
        if (baseSniffer(path) and os.path.isdir(path) and
            'RPGMKTRANSLATED' in (x.upper() for x in os.listdir(path))):
            return translatedSniffedType(path)
        else:
            return False
    ret.maintype = translatedSniffedType.maintype
    SNIFFERS.add(ret)
    return ret

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
        conflicts = {'TRANS': ['GAME']} # A Translation overrides a Game
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
                results[conflicttype] = [x for x in results[conflicttype]
                                         if x.canonicalpath not in delBases]
    return list(itertools.chain.from_iterable(results.values()))

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
