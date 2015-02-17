"""
zippatcher
**********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Provides a patcher for patches contained in a zip file.
"""

from .basepatcher import BasePatch, BasePatcherV2, BasePatcherV3
import zipfile
import os.path
from .registry import patcherSniffer, ZipPatchv2, ZipPatchv3

class ZIPPatcher(BasePatch):
    """Provides a patch loader for ZIP based patches"""
    def __init__(self, path, *args, **kwargs):
        """Initialise the patch loader"""
        self.zip = zipfile.ZipFile(path)
        self.mtime = os.path.getmtime(path)
        self.root = self.getPatchRoot()
        super(ZIPPatcher, self).__init__(path, *args, **kwargs)

    @property
    def assetRoot(self):
        """Get the asset root"""
        return self.root

    @property
    def patchRoot(self):
        """Get the patch root"""
        return self.root

    def patchIsWritable(self):
        """Return false as Zip patches are read only"""
        return False

    def loadPatchData(self):
        """Load the patch data"""
        data = {}
        for fn in self.patchDataFiles:
            zfile = self.zip.open(fn)
            raw = zfile.read(2 ** 22)
            dec = self.tryDecodePatchFile(raw)[1]
            name = (fn.partition(self.root)[2].strip('/').rpartition('.')[0])
            data[name] = dec
        return data, self.mtime

    def writePatchData(self, data, encoding='utf-8'):
        """Dummy write patch data"""

    def toOSFileStyle(self, path):
        """Convert all a zip path to OS style seperators, as
        in a zip file they are always UNIX style"""
        return os.path.join(*path.split('/'))

    def getAssetNames(self):
        """Get the names of the asset files"""
        return [self.toAssetName(x) for x in self.assetFiles]

    def toAssetName(self, string):
        """Convert a zip name to an name for use on file system"""
        name = string.partition(self.assetRoot)[2].strip('/')
        return self.toOSFileStyle(name)

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
        """Conditional iteration with a beginning for the path"""
        for name in self.zip.namelist():
            print(name, directory)
            if (name.startswith(directory) and condition(name)):
                yield name

    def iterDirs(self, directory):
        """Iterate over directories beginning with a directory"""
        condition = lambda x: x.endswith('/')
        return self.__citer(directory, condition)

    def iterFiles(self, directory):
        """Iterate over files beginning with a directory"""
        condition = lambda x: not x.endswith('/')
        return self.__citer(directory, condition)

    def iterPatchFiles(self, directory):
        condition = lambda x: (not x.endswith('/')) and self.categorisePatchFile(x)
        return self.__citer(directory, condition)

    def isPatchMarker(self, name):
        """Determine if a file name is a patch marker"""
        if name.endswith('RPGMKTRANSPATCH'):
            try:
                with self.zip.open(name) as z:
                    data = z.read(len(type(self).patchMarkerID)).decode('utf-8')
                return type(self).matchPatchMarker(data)
            except UnicodeDecodeError:
                return False
        else:
            return False

    def getPatchRoot(self):
        """Get the root of the patch. If there's more than one,
        error."""
        markers = [x.rpartition('RPGMKTRANSPATCH')[0]
                   for x in self.__citer('', self.isPatchMarker)]
        if len(markers) != 1:
            raise Exception('Wrong number of roots in zip file')
        return markers[0]

    def categorisePatchFile(self, name):
        """Categorise a single file based on if it is a given directory
        and if it has a given header when decoded with utf-8"""
        if name.lower().endswith('.txt'):
            with self.zip.open(name) as f:
                data = f.read(len(type(self).header) + 3)
            return self.tryDecodePatchFile(data, 'ignore')[0]


class ZIPPatcherv2(ZIPPatcher, BasePatcherV2):
    """Provides a ZIP patch loader specialised for v2 Patches"""

    def categorisePatchFiles(self):
        """Categorise the patch files"""
        patchfiles = list(self.iterFiles(self.root))
        self.patchdirs = list(self.iterDirs(self.root))

        if self.root.strip():
            rootfiles = [x for x in patchfiles if '/' not in x.partition(self.root)[2]]
        else:
            rootfiles = [x for x in patchfiles if '/' not in x]

        self.assetFiles = []
        self.patchDataFiles = []
        for fn in patchfiles:
            if fn.lower().endswith('.txt') and fn in rootfiles:
                matched = False
                z = self.zip.open(fn)
                raw = z.read(2 ** 22)
                matched = self.tryDecodePatchFile(raw, errors='ignore')[0]
                if matched:
                    self.patchDataFiles.append(fn)
                else:
                    self.assetFiles.append(fn)
            else:
                if not fn.endswith('RPGMKTRANSPATCH'):
                    self.assetFiles.append(fn)

class ZIPPatcherv3(ZIPPatcher, BasePatcherV3):
    """ZIP Patcher for patch version v3"""

    @property
    def assetRoot(self):
        """Get the asset root"""
        subdir = 'Assets/' if self.root.endswith('/') else '/Assets/'
        return self.root + subdir

    @property
    def patchRoot(self):
        """Get the patch root"""
        subdir = 'Patch/' if self.root.endswith('/') else '/Patch/'
        return self.root + subdir

    def categorisePatchFiles(self):
        """Categorise the patch files"""
        self.patchdirs = list(self.iterDirs(self.root))
        self.assetFiles = list(self.iterFiles(self.assetRoot))
        self.patchDataFiles = list(self.iterPatchFiles(self.patchRoot))
        #print(self.assetFiles)
        #print(self.patchDataFiles)

def sniffZip(path, matchfunc):
    """A sniffer for Zipped Patches"""
    if os.path.isfile(path) and zipfile.is_zipfile(path):
        z = zipfile.ZipFile(path)
        contents = z.namelist()
        transpatches = [x for x in contents if x.endswith('RPGMKTRANSPATCH')]
        if len(transpatches) == 1:
            f = z.open(transpatches[0])
            x = f.read().decode('utf-8')
            if matchfunc(x):
                return path
    return False

@patcherSniffer(ZipPatchv2, 'ZIPPatcherv2')
def sniffzipv2(path):
    """Sniffer for Zipv2 patches"""
    return sniffZip(path, ZIPPatcherv2.matchPatchMarker)

@patcherSniffer(ZipPatchv3, 'ZIPPatcherv3')
def sniffzipv3(path):
    """Sniffer for Zipv3 patches"""
    return sniffZip(path, ZIPPatcherv3.matchPatchMarker)
