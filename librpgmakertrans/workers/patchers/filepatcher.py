"""
filepatcher
***********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2015
:license: GNU Public License version 3

Provides a patcher for a patch contained in a directory.
"""

import os
from .basepatcher import BasePatch, BasePatcherV2, BasePatcherV3
from ..filecopier2 import copyfiles
from .registry import patcherSniffer, FilePatchv2, FilePatchv3


class FilePatcher(BasePatch):
    """A Patch which is just a directory on the file system"""
    def __init__(self, path, *args, **kwargs):
        """Initialise the file patcher; corrects paths if necessary"""
        path = os.path.normcase(path)
        super(FilePatcher, self).__init__(path, *args, **kwargs)
        if os.path.isfile(self.path):
            self.path = os.path.split(path)[0]

    @property
    def patchPath(self):
        """Return the patch path"""
        return self.path

    @property
    def assetPath(self):
        """Return the asset path"""
        return self.path

    def loadPatchData(self):
        """Load patch data from files"""
        data = {}
        mtime = 0
        for fn in self.patchDataFiles:
            name = os.path.split(fn)[1].rpartition('.')[0]
            mtime = max(mtime, os.path.getmtime(fn))
            with open(fn, 'rb') as f:
                raw = f.read()
                matched, decoded = self.tryDecodePatchFile(raw)
                if not matched:
                    raise Exception('Could not decode file %s' % fn)
                data[name] = decoded
        self.originalData = data.copy()
        return data, mtime

    def writePatchData(self, data, encoding='utf-8'):
        """Write patch data to files"""
        for directory in (self.path, self.patchPath, self.assetPath):
            if not os.path.exists(directory):
                os.mkdir(directory)
        patchmarkerfn = os.path.join(self.path, 'RPGMKTRANSPATCH')
        if not os.path.exists(patchmarkerfn):
            if os.path.isdir(patchmarkerfn):
                raise Exception(
                    'Can\'t create patch marker file due to directory name conflict')
            with open(patchmarkerfn, 'w') as f:
                f.write(self.patchMarker)
        for name in data:
            if data[name] != self.originalData.get(name.lower(), None):
                fn = name + '.txt'
                fullfn = os.path.join(self.patchPath, fn)
                with open(fullfn, 'w', encoding=encoding) as f:
                    f.write(data[name])

    def allPaths(self):
        """Get all paths of files in patch"""
        for dr, _, files in os.walk(self.path):
            if dr != self.path:
                yield dr
            for fn in files:
                if not fn.upper().endswith('RPGMKTRANSPATCH'):
                    fpath = os.path.normcase(os.path.join(dr, fn))
                    yield fpath

    def fileDirs(self):
        """Get directories of files in patch"""
        for dr, _, _ in os.walk(self.path):
            yield dr

    def getAssetNames(self):
        """Get names of assets in patch; so that files which are replaced
        are not copied."""
        return [os.path.relpath(fn, self.assetPath) for fn in self.assetFiles]

    def getNonCopyNames(self):
        """Get names of files not to copy in patch"""
        return [os.path.relpath(fn, self.assetPath) for fn in
                self.patchDataFiles] + ['RPGMKTRANSPATCH']

    def doFullPatches(self, outpath, translator, mtimes, newmtimes):
        """Do full file patches using a filecopier"""
        self.coms.send('waitUntil', 'dirsCopied', 'copier', copyfiles,
                       indir=self.assetPath, outdir=outpath, ignoredirs=[],
                       ignoreexts=[], ignorefiles=self.getNonCopyNames(),
                       comsout=self.coms, translator=translator,
                       mtimes=mtimes, newmtimes=newmtimes,
                       progresssig='patchdata', dirssig=None)

    def categorisePatchFile(self, header, filename):
        """Categorise a single file based on if it is a given directory
        and if it has a given header when decoded with utf-8"""
        if filename.lower().endswith('.txt') and os.path.isfile(filename):
            with open(filename, 'rb') as f:
                data = f.read(len(header) + 3)
            return self.tryDecodePatchFile(data, 'ignore')[0]

class FilePatcherv2(FilePatcher, BasePatcherV2):
    """A file based patcher for v2 patches"""

    def categorisePatchFiles(self):
        """Work out if a file is an asset or patch data"""
        self.assetFiles = []
        self.patchDataFiles = []
        rootls = set(os.path.normcase(x) for x in os.listdir(self.path))
        for fn in self.allPaths():
            if os.path.normcase(os.path.split(fn)[1]) in rootls:
                if self.categorisePatchFile(type(self).header, fn):
                    self.patchDataFiles.append(fn)
                else:
                    self.assetFiles.append(fn)
            else:
                if not fn.upper().endswith('RPGMKTRANSPATCH'):
                    self.assetFiles.append(fn)

class FilePatcherv3(FilePatcher, BasePatcherV3):
    """A file patcher for v3 based patches"""

    @property
    def patchPath(self):
        """Return the patch path"""
        return os.path.normcase(os.path.join(self.path, 'Patch')) + os.path.sep

    @property
    def assetPath(self):
        """Return the asset path"""
        return os.path.normcase(os.path.join(self.path, 'Assets')) + os.path.sep

    def isSubDir(self, base, subdir):
        """A very primitive check to see if a file/directory is in a
        sub directory"""
        return subdir.startswith(base)

    def categorisePatchFiles(self):
        """Work out if a file is an asset or patch data"""
        self.assetFiles = []
        self.patchDataFiles = []
        for fn in self.allPaths():
            fn = os.path.normcase(fn)
            if self.isSubDir(self.patchPath, fn):
                if self.categorisePatchFile(type(self).header, fn):
                    self.patchDataFiles.append(fn)
            elif self.isSubDir(self.assetPath, fn):
                self.assetFiles.append(fn)


@patcherSniffer(FilePatchv2, 'FilePatcherv2')
def sniffv2(path):
    """Sniffer for v2 file patches"""
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
    """Sniffer for v3 file patches"""
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