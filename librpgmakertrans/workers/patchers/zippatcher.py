"""
zippatcher
**********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Provides a patcher for patches contained in a zip file.
"""

from .basepatcher import BasePatch, BasePatcherV2
import zipfile
import os.path
from .registry import patcherSniffer, ZipPatchv2

SEPERATORS = '\\/'


class ZIPPatcher(BasePatch):
    """Provides a patch loader for ZIP based patches"""
    def __init__(self, path, *args, **kwargs):
        """Initialise the patch loader"""
        self.zip = zipfile.ZipFile(path)
        self.mtime = os.path.getmtime(path)
        super(ZIPPatcher, self).__init__(path, *args, **kwargs)

    def patchIsWritable(self):
        """Return false as Zip patches are read only"""
        return False

    def loadPatchData(self):
        """Load the patch data"""
        data = {}
        for fn in self.patchDataFiles:
            zfile = self.zip.open(fn)
            raw = zfile.read(2 ** 22)
            dec = self.tryDecodePatchFile(type(self).header, raw)[1]
            name = (fn.partition(self.root)[2].strip(
                    SEPERATORS).rpartition('.')[0])
            data[name] = dec
        return data, self.mtime

    def writePatchData(self, data, encoding='utf-8'):
        """Dummy write patch data"""

    def toOSFileStyle(self, path):
        """Convert all possible separators to OS style seperators, as
        in a zip file they are always UNIX style"""
        for sep in SEPERATORS:
            path = path.replace(sep, os.path.sep)
        return path

    def getAssetNames(self):
        """Get the names of the asset files"""
        return [self.toAssetName(x) for x in self.assetFiles]

    def toAssetName(self, string):
        """Convert a zip name to an name for use on file system"""
        return self.toOSFileStyle(
                    string.partition(self.root)[2].strip(SEPERATORS))

    def makeDir(self, dirname):
        """Make a directory"""
        if os.path.exists(dirname):
            if os.path.isfile(dirname):
                raise Exception('Directory name conflicts with existing'
                                'file name')
        else:
            os.makedirs(dirname)

    def doFullPatches(self, outpath, translator, mtimes, newmtimes):
        """Perform all full file patches"""
        for d in self.patchdirs:
            outdir = os.path.join(outpath, self.toAssetName(d))
            self.makeDir(outdir)
        for fn in self.assetFiles:
            outfn = os.path.join(outpath, self.toAssetName(fn))
            outfntime = mtimes.get(outfn, None)
            if outfntime != self.mtime:
                dirname = os.path.split(outfn)[0]
                self.makeDir(dirname)
                z = self.zip.open(fn)
                data = z.read(2 ** 22)
                with open(outfn, 'wb') as f:
                    while data:
                        f.write(data)
                        data = z.read(2 ** 20)
            newmtimes[outfn] = self.mtime

    def __citer(self, directory, condition = lambda x: True):
        for name in self.zip.namelist():
            if (name.startswith(directory) and condition(name)):
                yield name

    def iterDirs(self, directory):
        condition = lambda x: any(x.endswith(sep) for sep in SEPERATORS)
        return self.__citer(directory, condition)

    def iterFiles(self, directory):
        condition = lambda x: not any(x.endswith(sep) for sep in SEPERATORS)
        return self.__citer(directory, condition)

    def isPatchMarker(self, name):
        if name.endswith('RPGMKTRANSPATCH'):
            with self.zip.open(name) as z:
                data = z.read(len(self.patchMarkerText()))
            return data == self.patchMarkerText()
        else:
            return False

    def patchRoots(self):
        return [x.rpartition('RPGMKTRANSPATCH')[0]
                for x in self.__citer('', self.isPatchMarker)]

    def categorisePatchFile(self, header, name):
        """Categorise a single file based on if it is a given directory
        and if it has a given header when decoded with utf-8"""
        if name.lower().endswith('.txt'):
            with self.zip.open(name, 'rb') as f:
                data = f.read(len(header) + 3)
            return self.tryDecodePatchFile(header, data, 'ignore')[0]


class ZIPPatcherv2(ZIPPatcher, BasePatcherV2):
    """Provides a ZIP patch loader specialised for v2 Patches"""

    def categorisePatchFiles(self):
        """Categorise the patch files"""
        roots = self.patchRoots()
        if len(roots) > 1:
            raise Exception('ZIP file contains more than one'
                            'RPGMKTRANSPATCH file; cannot determine root')
        self.root = roots[0]
        patchfiles = list(self.iterFiles(self.root))
        self.patchdirs = list(self.iterDirs(self.root))

        if self.root.strip():
            rootfiles = [x for x in patchfiles
                        if all([y not in x.partition(self.root)[2]
                                for y in SEPERATORS])]
        else:
            rootfiles = [x for x in patchfiles
                         if all(sep not in x for sep in SEPERATORS)]

        self.assetFiles = []
        self.patchDataFiles = []
        for fn in patchfiles:
            if fn.lower().endswith('.txt') and fn in rootfiles:
                matched = False
                header = type(self).header
                z = self.zip.open(fn)
                raw = z.read(2 ** 22)
                matched = self.tryDecodePatchFile(header, raw,
                                                  errors='ignore')[0]
                if matched:
                    self.patchDataFiles.append(fn)
                else:
                    self.assetFiles.append(fn)
            else:
                if not fn.endswith('RPGMKTRANSPATCH'):
                    self.assetFiles.append(fn)


@patcherSniffer(ZipPatchv2, 'ZIPPatcherv2')
def sniffzipv2(path):
    """A sniffer for V2 Zipped Patches"""
    if os.path.isfile(path) and zipfile.is_zipfile(path):
        z = zipfile.ZipFile(path)
        contents = z.namelist()
        transpatches = [x for x in contents if x.endswith('RPGMKTRANSPATCH')]
        if len(transpatches) == 1:
            f = z.open(transpatches[0])
            x = f.read()
            if not x.strip():
                return path
    return False
