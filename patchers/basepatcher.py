'''
Created on 19 Sep 2013

@author: habisain
'''

from resources import Resource

class BasePatch(Resource):
    
    def __init__(self, path, coms):
        self.path = path
        self.coms = coms
        self.categorisePatchFiles()
    
    def loadPatchData(self):
        raise Exception('loading patch data not implemented')
    
    def writePatchData(self, data, path=None):
        raise Exception('Writing patch data not implemented')
    
    def categorisePatchFiles(self):
        raise Exception('This method must be overridden')

    def writeTranslator(self, translator, path=None):
        data = translator.getPatchData()
        self.writePatchData(data, path)
        
    def makeTranslator(self):
        data, mtime = self.loadPatchData()
        return getattr(self.translatorManager, type(self).translatorClass)(data, mtime)
    
    def getAssetFiles(self):
        return self.assetFiles
    
    def getDataFiles(self):
        return self.patchDataFiles
    
    def getAssetNames(self):
        raise Exception('getAssetNames not implemented')
    
    def doFullPatches(self):
        raise Exception('FullPatching not implemented')
    