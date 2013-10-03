import os.path
from filepatcher import filePatchers
from basepatcher import PatchManager, makeTranslator, writeTranslator

DEFAULT = 'FilePatcherv2'

def getPatcher(manager, path, coms):
    for x in filePatchers:
        if x(path):
            return getattr(manager, filePatchers[x])(path, coms)
    if not os.path.exists(path):
        os.mkdir(path)
    return getattr(manager, DEFAULT)(path, coms)

def doFullPatches(patcher, outdir, translator, mtimes, newmtimes, coms):
    patcher.doFullPatches(outdir, translator, mtimes, newmtimes)
    coms.send('trigger', 'fullPatchesDone')