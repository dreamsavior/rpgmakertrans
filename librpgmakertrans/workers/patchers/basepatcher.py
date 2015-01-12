"""
basepatcher
***********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2015
:license: GNU Public License version 3

Contains the shared methods/interfaces of the patcher classes.
"""
from ...metamanager import CustomManager, MetaCustomManager
from ..translator import TranslatorManager
from ...errorhook import ErrorMeta

class PatchManager(CustomManager):
    """Custom Manager for Patch handlers"""

class PatchMeta(MetaCustomManager, ErrorMeta):
    """Patch meta class"""
    customManagerClass = PatchManager

class BasePatch(metaclass=PatchMeta):
    """The basic class for Patch objects"""
    def __init__(self, path, coms, errout):
        """Initialise the patch"""
        self.path = path
        self.coms = coms
        self.categorisePatchFiles()
        self.translatorManager = TranslatorManager()
        self.translatorManager.start(errout)

    def quit(self):
        """Stop the associated translator manager"""
        self.translatorManager.shutdown()

    def tryDecodePatchFile(self, header, data, errors='strict'):
        """Try to decode a file using utf-8 or utf-8-sig. If possible
        return the decoded string"""
        for encoding in 'utf-8', 'utf-8-sig':
            try:
                decoded = data.decode(encoding, errors=errors)
                if decoded.startswith(header):
                    return True, decoded
            except UnicodeError:
                pass
        return False, data

    def setPath(self, path):
        """Set the path of the patch"""
        self.path = path

    def patchIsWriteable(self):
        """Return if the patch is writeable"""
        return True

    def loadPatchData(self):
        """Load data from the patch; needs implementing"""
        raise NotImplementedError('loading patch data not implemented')

    def writePatchData(self, data, encoding='utf-8'):
        """Write data to the patch"""
        raise NotImplementedError('Writing patch data not implemented')

    def categorisePatchFiles(self):
        """Categorise files in the patch"""
        raise NotImplementedError('This method must be overridden')

    def writeTranslator(self, translator, encoding):
        """Write a translator to the patch"""
        if self.patchIsWriteable():
            data = translator.getPatchData()
            self.writePatchData(data, encoding)

    def makeTranslator(self, coms):
        """Make a translator object from this patch"""
        data, mtime = self.loadPatchData()
        translatorClass = getattr(self.translatorManager,
                                  type(self).translatorClass)
        return translatorClass(data, mtime=mtime, coms=coms)

    def getAssetFiles(self):
        """Get asset files for this patch"""
        return self.assetFiles

    def getDataFiles(self):
        """Get the patch data files for this patch"""
        return self.patchDataFiles

    def getAssetNames(self):
        """Get the names of Assets of this patch"""
        raise NotImplementedError('getAssetNames not implemented')

    def doFullPatches(self, outpath, translator, mtimes, newmtimes):
        """Do the full file patches for this patch"""
        raise NotImplementedError('FullPatching not implemented')

    @property
    def patchMarkerID(self):
        """Return the patch marker ID, which is the first line of
        the patchMarker text. This should be constant for a patch
        version"""
        return type(self).patchMarker.partition('\n')[0]

class BasePatcherV2(BasePatch):
    """Contains information for v2 patches"""
    translatorClass = 'Translator2kv2'
    header = '# RPGMAKER TRANS PATCH'
    patchMarker = ''

class BasePatcherV3(BasePatch):
    """Contains information for v3 patches"""
    translatorClass = 'Translator3'
    header = '> RPGMAKER TRANS PATCH'
    patchMarker = '> RPGMAKER TRANS PATCH V3'

def makeTranslator(patcher, coms):
    """Make a translator from this patch"""
    ret = patcher.makeTranslator(coms)
    coms.send('trigger', 'translatorReady')
    return ret

def writeTranslator(patcher, translator, useBOM, coms):
    """Write a translator for the patch"""
    encoding = 'utf-8-sig' if useBOM else 'utf-8'
    patcher.writeTranslator(translator, encoding)
    coms.send('trigger', 'translatorWritten')
