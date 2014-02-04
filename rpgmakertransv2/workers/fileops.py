'''
fileops

Abstraction of file manipulation functions that deals with
accursed Windows long paths.
'''

import os.path
import sys

LONGPATH = '\\\\?\\'

def winescape(path):
    if sys.platform == 'win32':
        abspath = os.path.abspath(path)
        return '\\\\?\\%s' % abspath
    else:
        return path

def getmtime(path): return os.path.getmtime(winescape(path))
def pathexists(path): return os.path.exists(winescape(path))
def isfile(path): return os.path.isfile(winescape(path))
def mkdir(path): os.mkdir(winescape(path))
def remove(path): os.remove(winescape(path))
def isdir(path): return os.path.isdir(winescape(path))
def listdir(path): return os.listdir(winescape(path))
def walk(path): return os.walk(winescape(path))

class WinOpen:
    """A minimal replacement for builtin open which escapes the filename
    appropriately"""
    def __init__(self, file, mode='r', buffering=-1, encoding=None, 
                 errors=None, newline=None, closefd=True, opener=None):
        self.__file = open(winescape(file), mode, buffering, encoding, 
                           errors, newline, closefd, opener)
        
    def __enter__(self):
        return self.__file.__enter__()
    
    def __exit__(self, *args, **kwargs):
        return self.__file.__exit__(*args, **kwargs)
    
    def __getattr__(self, key):
        return getattr(self.__file, key)
