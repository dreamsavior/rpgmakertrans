"""
basepatcher
***********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Contains the shared methods/interfaces of the patcher classes.
"""
from ...metamanager import CustomManager, MetaCustomManager
from ..translator import TranslatorManager


class PatchManager(CustomManager):
    pass


class PatchMeta(MetaCustomManager):
    customManagerClass = PatchManager


class BasePatch(metaclass=PatchMeta):

    def __init__(self, path, coms, errout):
        self.path = path
        self.coms = coms
        self.categorisePatchFiles()
        self.translatorManager = TranslatorManager()
        self.translatorManager.start(errout)

    def quit(self):
        self.translatorManager.shutdown()

    def tryDecodePatchFile(self, header, data, errors='strict'):
        for encoding in 'utf-8', 'utf-8-sig':
            try:
                decoded = data.decode(encoding, errors=errors)
                if decoded.startswith(header):
                    return True, decoded
            except UnicodeError:
                pass
        return False, data

    def setPath(self, path):
        self.path = path

    def patchIsWriteable(self):
        return True

    def loadPatchData(self):
        raise Exception('loading patch data not implemented')

    def writePatchData(self, data, encoding='utf-8'):
        raise Exception('Writing patch data not implemented')

    def categorisePatchFiles(self):
        raise Exception('This method must be overridden')

    def writeTranslator(self, translator, encoding):
        if self.patchIsWriteable():
            data = translator.getPatchData()
            self.writePatchData(data, encoding)

    def makeTranslator(self, coms):
        data, mtime = self.loadPatchData()
        translatorClass = getattr(self.translatorManager,
                                  type(self).translatorClass) 
        return translatorClass(data, mtime=mtime, coms=coms)

    def getAssetFiles(self):
        return self.assetFiles

    def getDataFiles(self):
        return self.patchDataFiles

    def getAssetNames(self):
        raise Exception('getAssetNames not implemented')

    def doFullPatches(self, outpath, translator, mtimes, newmtimes):
        raise Exception('FullPatching not implemented')


def makeTranslator(patcher, coms):
    ret = patcher.makeTranslator(coms)
    coms.send('trigger', 'translatorReady')
    return ret


def writeTranslator(patcher, translator, useBOM, coms):
    encoding = 'utf-8-sig' if useBOM else 'utf-8'
    patcher.writeTranslator(translator, encoding)
    coms.send('trigger', 'translatorWritten')
