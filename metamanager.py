'''
Created on 20 Sep 2013

@author: habisain
'''
from multiprocessing.managers import BaseManager
from errorhook import ErrorMeta, setErrorOut

def makeMetaManager(name, metainherit=type):
    class CustomManager(BaseManager):
        def start(self, errout=None):
            if errout is None:
                raise Exception('Starting a %s without an errout' % type(self).__name__)
            super(CustomManager, self).start(initializer=setErrorOut, initargs=[errout])
    
    class MetaCustomManager(metainherit):
        def __init__(cls, a, b, c):
            super(MetaCustomManager, cls).__init__(a, b, c)
            CustomManager.register(cls.__name__, cls)
    CustomManager.__name__ = '%sManager' % name
    MetaCustomManager.__name__ = '%sMetaManager' % name
    return CustomManager, MetaCustomManager
            
    