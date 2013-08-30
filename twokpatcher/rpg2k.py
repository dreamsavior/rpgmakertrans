'''
Created on 10 Apr 2013

@author: habisain
'''
from __future__ import division
from errorhook import errorWrap, ErrorClass, ErrorMeta
from resource import BaseGame

import os.path
import cPickle
from gamepatcher import Patcher

class RPG2k(ErrorClass, BaseGame):    
    @staticmethod
    def sniff(path):
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        dirls = [os.path.normcase(x) for x in os.listdir(path)]
        return True if ('rpg_rt.ldb' in dirls and 
            'rpgmakertranspatch' not in dirls and
            'rpgmakertranslated' not in dirls) else False
    
    @staticmethod
    def patch(indir, outdir, translator):
        if not RPG2k.sniff(indir):
            raise Exception('Not a valid RPGMaker 2k Game')
        outdirls = [os.path.normcase(x) for x in os.listdir(outdir)]
        if 'mtimes' in outdirls: 
            mtimes = cPickle.load(os.path.join(outdir, 'mtimes'))
        else:
            mtimes = {}
        jobfnnames = [x for x in (y.lower() for y in os.listdir(indir)) 
                      if x.rpartition('.')[2] in ('ldb', 'lmu')]
        
        
            
            
    