"""
metamanager
***********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

A special multiprocessing manager which takes care of some things
automatically.
"""
from multiprocessing.managers import BaseManager
from .errorhook import ErrorMeta, setErrorOut


class CustomManager(BaseManager):

    def start(self, errout=None):
        if errout is None:
            raise Exception('Starting a %s without an errout' %
                            type(self).__name__)
        super(CustomManager,self).start(initializer=setErrorOut,
                                        initargs=[errout])


class MetaCustomManager(ErrorMeta):
    customManagerClass = None

    def __init__(cls, a, b, c):
        super(MetaCustomManager, cls).__init__(a, b, c)
        type(cls).customManagerClass.register(cls.__name__, cls)
