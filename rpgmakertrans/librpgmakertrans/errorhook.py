"""
errorhook
*********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Various tools to assist getting an error message with traceback string through
multiprocessing. This is problematic because normally Python does not give
this.
"""

import traceback
import functools
import sys
import io
import collections

from .version import debug

errorOut = None


def setErrorOut(outputComs):
    """Set the error output. If debug is defined in version file,
    always print to stderr, otherwise suppress if applicable."""
    global errorOut
    errorOut = outputComs
    if not debug:
        if errorOut is None:
            sys.stderr = sys.__stderr__
        else:
            sys.stderr = io.StringIO()

def handleError():
    """Handle an error either by putting it onto the error
    sender or writing it to stderr."""
    global errorOut, caught
    if errorOut is not None:
        errorOut.send('ERROR', traceback.format_exc())
    else:
        sys.stderr.write(traceback.format_exc())
        sys.stderr.flush()

def errorWrap(func):
    """Wrap a function for multiprocess error handling."""
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            handleError()
    return wrap


try:
    # For Python 3.10 and above
    from collections.abc import Callable as ABCCallable
except ImportError:
    # For Python versions prior to 3.10
    ABCCallable = collections.Callable

class ErrorMeta(type):
    """A metaclass which automatically applies ErrorWrap to all
    methods on the class"""
    def __init__(cls, name, bases, dict_):
        super().__init__(name, bases, dict_)
        for x in cls.__dict__:
            f = getattr(cls, x)
            if isinstance(f, ABCCallable):
                setattr(cls, x, errorWrap(f))
