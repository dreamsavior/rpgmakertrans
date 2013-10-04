import os.path
import filepatcher
import zippatcher
from basepatcher import PatchManager, makeTranslator, writeTranslator, REGISTRY

DEFAULT = 'FilePatcherv2'

def getPatcher(manager, path, coms):
    for x in REGISTRY:
        if x(path):
            return getattr(manager, REGISTRY[x])(path, coms)
    if not os.path.exists(path):
        os.mkdir(path)
    return getattr(manager, DEFAULT)(path, coms)

def isPatcher(path):
    for x in REGISTRY:
        if x(path):
            return True
    return False

def doFullPatches(patcher, outdir, translator, mtimes, newmtimes, coms):
    patcher.doFullPatches(outdir, translator, mtimes, newmtimes)
    coms.send('trigger', 'fullPatchesDone')