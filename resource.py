'''
Created on 10 Apr 2013

@author: habisain
'''
from errorhook import ErrorMeta

class Resource(object):
    
    @staticmethod
    def sniff(path):
        raise Exception('Sniffing not implemented')
    
class BaseGame(Resource):
    @staticmethod
    def patch(indir, outdir, translator):
        raise Exception('Patching not implemented')

class BasePatch(Resource):
    __metaclass__ = ErrorMeta
    def __init__(self, path):
        self.path = path
         
    @staticmethod
    def makeTranslator():
        raise Exception('Translator grabbing not implemented')
    
    @staticmethod
    def writePatch(translator):
        return False
    
    @staticmethod
    def getNonPatchedList():
        raise Exception('Nonpatched List not implemented')
    
    @staticmethod
    def doFullPatches(outpath):
        raise Exception('FullPatching not implemented')
    