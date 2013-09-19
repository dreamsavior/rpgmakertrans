'''
Created on 10 Apr 2013

@author: habisain
'''
from errorhook import ErrorMeta

class Resource(object):
    __metaclass__ = ErrorMeta
    @staticmethod
    def sniff(path):
        raise Exception('Sniffing not implemented')
    
class BaseGame(Resource):
    @staticmethod
    def patch(indir, outdir, translator):
        raise Exception('Patching not implemented')


    