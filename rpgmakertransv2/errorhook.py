'''
Created on 3 Feb 2013

@author: habisain
'''

import traceback, functools
import sys
import io
import collections
errorOut = None

def setErrorOut(comsout):
    global errorOut
    errorOut = comsout
    if errorOut is None:
        sys.stderr = sys.__stderr__
    else:
        sys.stderr = io.StringIO() 

def errorWrap(func):
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            global errorOut, caught
            if errorOut is not None:
                errorOut.send('ERROR', traceback.format_exc())
            else:
                sys.stderr.write(traceback.format_exc())
                sys.stderr.flush()
            #raise
    return wrap

class ErrorClass(object):
    def __init__(self, *args, **kwargs):
        super(ErrorClass, self).__init__(*args, **kwargs)
        for x in type(self).__dict__:
            f = getattr(self, x)
            if isinstance(f, collections.Callable):
                setattr(self, x, errorWrap(f))
#        print self.__init__
        
class ErrorMeta(type):
    def __init__(cls, a,b,c):
        super(ErrorMeta, cls).__init__(a,b,c)
        for x in cls.__dict__:
            f = getattr(cls, x)
            if isinstance(f, collections.Callable):
#                print f
                setattr(cls, x, errorWrap(f))
@errorWrap  
def testExcept():
    print('called')
    raise Exception('Something went wrong, natch')
    print('hmm')
    
    

    
            