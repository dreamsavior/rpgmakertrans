import os.path
import filepatcher
import zippatcher
from basepatcher import PatchManager, makeTranslator, writeTranslator
from registry import getClassName
DEFAULT = 'FilePatcherv2'

def getPatcher(manager, path, coms):
    className = getClassName(path)
    if className is None:
        if not os.path.exists(path):
            os.mkdir(path)
        elif not os.path.isdir(path):
            raise Exception('Not a patcher!') 
        className = DEFAULT
    return getattr(manager, className)(path, coms)

def doFullPatches(patcher, outdir, translator, mtimes, newmtimes, coms):
    patcher.doFullPatches(outdir, translator, mtimes, newmtimes)
    coms.send('trigger', 'fullPatchesDone')