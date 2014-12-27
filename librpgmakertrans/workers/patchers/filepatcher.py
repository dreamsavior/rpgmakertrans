"""
filepatcher
***********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Provides a patcher for a patch contained in a directory.
"""

import os
from .basepatcher import BasePatch
from ..filecopier2 import copyfiles
from .registry import patcherSniffer, FilePatchv2, FilePatchv3


class FilePatcher(BasePatch):

    def __init__(self, path, *args, **kwargs):
        super(FilePatcher, self).__init__(path, *args, **kwargs)
        if os.path.isfile(self.path):
            self.path = os.path.split(path)[0]

    def loadPatchData(self):
        data = {}
        mtime = 0
        for fn in self.patchDataFiles:
            name = os.path.split(fn)[1].rpartition('.')[0].lower()
            mtime = max(mtime, os.path.getmtime(fn))
            with open(fn, 'rb') as f:
                raw = f.read()
                matched, decoded = self.tryDecodePatchFile(
                    type(self).header, raw)
                if not matched:
                    raise Exception('Could not decode file %s' % fn)
                data[name] = decoded
        self.originalData = data.copy()
        return data, mtime
    
    def patchMarkerText(self):
        return ''

    def writePatchData(self, data, encoding='utf-8'):
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        patchmarkerfn = os.path.join(self.path, 'RPGMKTRANSPATCH')
        if not os.path.exists(patchmarkerfn):
            if os.path.isdir(patchmarkerfn):
                raise Exception(
                    'Can\'t create patch marker file due to directory name conflict')
            with open(patchmarkerfn, 'w') as f:
                f.write(self.patchMarkerText())
        for name in data:
            if data[name] != self.originalData.get(name.lower(), None):
                fn = name + '.txt'
                fullfn = os.path.join(self.path, fn)
                with open(fullfn, 'w', encoding=encoding) as f:
                    f.write(data[name])

    def allPaths(self):
        for dr, _, files in os.walk(self.path):
            if dr != self.path:
                yield dr
            for fn in files:
                if not fn.upper().endswith('RPGMKTRANSPATCH'):
                    fpath = os.path.normcase(os.path.join(dr, fn))
                    yield fpath

    def fileDirs(self):
        for dr, _, _ in os.walk(self.path):
            yield dr

    def getAssetNames(self):
        return [os.path.relpath(fn, self.path) for fn in self.assetFiles]

    def getNonCopyNames(self):
        return [os.path.relpath(fn, self.path) for fn in 
                self.patchDataFiles] + ['RPGMKTRANSPATCH']

    def doFullPatches(self, outpath, translator, mtimes, newmtimes):
        self.coms.send('waitUntil', 'dirsCopied', 'copier', copyfiles,
                       indir=self.path, outdir=outpath, ignoredirs=[],
                       ignoreexts=[], ignorefiles=self.getNonCopyNames(),
                       comsout='outputcoms', translator=translator,
                       mtimes=mtimes, newmtimes=newmtimes,
                       progresssig='patchdata', dirssig=None)


class FilePatcherv2(FilePatcher):
    translatorClass = 'Translator2kv2'
    header = '# RPGMAKER TRANS PATCH'

    def categorisePatchFiles(self):
        """Work out if a file is an asset or patch data"""
        self.assetFiles = []
        self.patchDataFiles = []
        rootls = set(os.listdir(self.path))
        for fn in self.allPaths():
            if fn.lower().endswith('.txt') and os.path.normcase(
                    os.path.split(fn)[1]) in rootls and os.path.isfile(fn):
                header = type(self).header
                with open(fn, 'rb') as f:
                    data = f.read(len(header) + 3)
                matched, _ = self.tryDecodePatchFile(header, data, 'ignore')
                if matched:
                    self.patchDataFiles.append(fn)
                else:
                    self.assetFiles.append(fn)
            else:
                if not fn.upper().endswith('RPGMKTRANSPATCH'):
                    self.assetFiles.append(fn)
                    
class FilePatcherv3(FilePatcher):
    translatorClass = 'Translator3'
    header = '> RPGMAKER TRANS PATCH'
    
    def patchMarkerText(self):
        return '> RPGMAKER TRANS PATCH V3'
    
    def categorisePatchFiles(self):
        """Work out if a file is an asset or patch data"""
        self.assetFiles = []
        self.patchDataFiles = []
        rootls = set(os.listdir(self.path))
        for fn in self.allPaths():
            if (fn.lower().endswith('.txt') and 
            os.path.normcase(os.path.split(fn)[1]) in rootls
            and os.path.isfile(fn)):
                header = type(self).header
                with open(fn, 'rb') as f:
                    data = f.read(len(header) + 3)
                matched, _ = self.tryDecodePatchFile(header, data, 'ignore')
                if matched:
                    self.patchDataFiles.append(fn)
                else:
                    self.assetFiles.append(fn)
            else:
                if not fn.upper().endswith('RPGMKTRANSPATCH'):
                    self.assetFiles.append(fn)

@patcherSniffer(FilePatchv2, 'FilePatcherv2')
def sniffv2(path):
    if os.path.isdir(path):
        cands = [x for x in os.listdir(path) if x.lower() == 'rpgmktranspatch']
        if len(cands) == 1:
            path = os.path.join(path, cands[0])
    elif not path.lower().endswith('rpgmktranspatch'):
        return False
    if os.path.isfile(path):
        with open(path, 'r') as f:
            versionString = f.read()
        if not versionString.strip():
            return os.path.split(path)[0]
    return False

@patcherSniffer(FilePatchv3, 'FilePatcherv3')
def sniffv3(path):
    if os.path.isdir(path):
        cands = [x for x in os.listdir(path) if x.lower() == 'rpgmktranspatch']
        if len(cands) == 1:
            path = os.path.join(path, cands[0])
    elif not path.lower().endswith('rpgmktranspatch'):
        return False
    if os.path.isfile(path):
        with open(path, 'r') as f:
            versionString = f.read()
        if versionString.strip() == '> RPGMAKER TRANS PATCH V3':
            return os.path.split(path)[0]
    return False