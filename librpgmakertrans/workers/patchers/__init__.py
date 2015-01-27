"""
patchers
********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2015
:license: GNU Public License version 3

Contains an interface onto the various kinds of patch managers
(File-based, Zip-based).
"""

import os.path
from . import filepatcher
from . import zippatcher
from .basepatcher import PatchManager, makeTranslator, writeTranslator
from .registry import getClassName


def getPatcher(manager, path, coms, errout, defaultVersion=2):
    """Get a patcher"""
    className = getClassName(path)
    if className is None:
        if not os.path.exists(path):
            os.mkdir(path)
        elif not os.path.isdir(path):
            raise Exception('Not a patcher!')
        if defaultVersion == 2:
            className = 'FilePatcherv2'
        elif defaultVersion == 3:
            className = 'FilePatcherv3'
        else:
            raise Exception('Bad Patch Version')
    return getattr(manager, className)(path, coms, errout)


def doFullPatches(patcher, outdir, translator, mtimes, newmtimes, coms):
    """Perform all full file patches with a given translator"""
    patcher.doFullPatches(outdir, translator, mtimes, newmtimes)
    coms.send('trigger', 'fullPatchesDone')
