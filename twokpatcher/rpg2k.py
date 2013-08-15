'''
Created on 10 Apr 2013

@author: habisain
'''

from errorhook import errorWrap, ErrorClass, ErrorMeta
from resource import BaseGame

import os.path

class RPG2k(ErrorClass, BaseGame):    
    @staticmethod
    def sniff(path):
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        dirls = [os.path.normcase(x) for x in os.listdir(path)]
        return True if ('rpg_rt.ldb' in dirls and 
            'rpgmakertranspatch' not in dirls and
            'rpgmakertranslated' not in dirls) else False
         
    def patch(self, indir, outdir, translator):
        raise Exception('Not implemented')
    