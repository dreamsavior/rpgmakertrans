"""
errorhook
*********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Various tools to assist getting an error message with traceback string through
multiprocessing. This is problematic because normally Python does not give
this.

TODO: Test if it is sufficient to just use setErrorOut and errorWrap on the API
entry. If it is, this would be more beneficial than using the stuff like
metaclasses etc, because I'd be able to put in additional hooks to get things
like arguments passed into the API.
"""

import traceback
import functools
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

def handleError():
    global errorOut, caught
    if errorOut is not None:
        errorOut.send('ERROR', traceback.format_exc())
    else:
        sys.stderr.write(traceback.format_exc())
        sys.stderr.flush()
    
def errorWrap(func):
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            handleError()
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

    def __init__(cls, a, b, c):
        super(ErrorMeta, cls).__init__(a, b, c)
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
