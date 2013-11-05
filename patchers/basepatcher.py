'''
Created on 19 Sep 2013

@author: habisain
'''
from metamanager import CustomManager, MetaCustomManager
from translator import TranslatorManager

class PatchManager(CustomManager): pass
class PatchMeta(MetaCustomManager): customManagerClass = PatchManager

class BasePatch(object, metaclass=PatchMeta):
    def __init__(self, path, coms, errout):
        self.path = path
        self.coms = coms
        self.categorisePatchFiles()
        self.translatorManager = TranslatorManager()
        self.translatorManager.start(errout)
        
    def setPath(self, path):
        self.path = path
        
    def patchIsWriteable(self):
        return True
    
    def loadPatchData(self):
        raise Exception('loading patch data not implemented')
    
    def writePatchData(self, data):
        raise Exception('Writing patch data not implemented')
    
    def categorisePatchFiles(self):
        raise Exception('This method must be overridden')

    def writeTranslator(self, translator):
        if self.patchIsWriteable():
            data = translator.getPatchData()
            self.writePatchData(data)
        
    def makeTranslator(self):
        data, mtime = self.loadPatchData()
        return getattr(self.translatorManager, type(self).translatorClass)(data, mtime)
    
    def getAssetFiles(self):
        return self.assetFiles
    
    def getDataFiles(self):
        return self.patchDataFiles
    
    def getAssetNames(self):
        raise Exception('getAssetNames not implemented')
    
    def doFullPatches(self, outpath, translator, mtimes, newmtimes):
        raise Exception('FullPatching not implemented')
    
def makeTranslator(patcher, coms):
    ret = patcher.makeTranslator()
    coms.send('trigger', 'translatorReady')
    return ret
    
def writeTranslator(patcher, translator, coms):
    patcher.writeTranslator(translator)
    coms.send('trigger', 'translatorWritten')
        