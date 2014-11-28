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
    
    @classmethod
    def get(cls):
        return set()
    
class FormatSuccessor(Successors):
    def __init__(cls, name, bases, dict_):
        super().__init__(name, bases, dict_)
        Successors.register(FormatSuccessor, cls)
    
    @classmethod
    def get(cls):
        return Successors._get(FormatSuccessor).union(super().get())
        
class BaseSuccessor(Successors):
    def __init__(cls, name, bases, dict_):
        super().__init__(name, bases, dict_)
        Successors.register(BaseSuccessor, cls)
        
    @classmethod
    def get(cls):
        return Successors._get(BaseSuccessor).union(super().get())
    
class FormatBaseSuccessor(FormatSuccessor, BaseSuccessor): pass

class CodeSuccessor(Successors):
    def __init__(cls, name, bases, dict_):
        super().__init__(name, bases, dict_)
        Successors.register(CodeSuccessor, cls)

    @classmethod
    def get(cls):
        return Successors._get(CodeSuccessor).union(super().get())
        
class AllCodeSuccessor(FormatBaseSuccessor, CodeSuccessor): pass
