'''
successor
*********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Provides the functionality to handle the various succession rules.
'''
from collections import defaultdict

class Successors(type):
    __successors = defaultdict(set)
    
    @classmethod
    def register(mcs, subcls, succ):
        mcs.__successors[subcls].add(succ)
    
    @classmethod
    def _get(mcs, subcls):
        return mcs.__successors[subcls]
    
class FormatSuccessor(Successors):
    def __init__(cls, name, bases, dict_):
        super().__init__(name, bases, dict_)
        Successors.register(FormatSuccessor, cls)
    
    @classmethod
    def get(cls):
        return Successors._get(FormatSuccessor)
        
class BaseSuccessor(Successors):
    def __init__(cls, name, bases, dict_):
        super().__init__(name, bases, dict_)
        type(cls).register(BaseSuccessor, cls)
        
    @classmethod
    def get(cls):
        return Successors._get(BaseSuccessor)
        
class FormatBaseSuccessor(FormatSuccessor, BaseSuccessor): pass