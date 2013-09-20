'''
Created on 20 Sep 2013

@author: habisain
'''
from multiprocessing.managers import BaseManager

def makeMetaManager(self, name, metainherit=type):
    class CustomManager(BaseManager):
        pass
    
    class MetaCustomManager(metainherit):
        def __init__(cls, a, b, c):
            super(MetaCustomManager, cls).__init__(a, b, c)
            CustomManager.register(cls.__name__, cls)
    CustomManager.__name__ = '%sManager' % name
    MetaCustomManager.__name__ = '%sMetaManager' % name
    return CustomManager, MetaCustomManager
            
    