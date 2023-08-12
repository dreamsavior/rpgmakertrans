"""
makefastunpack
**************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2015
:license: GNU Public License version 3

Quick script that makes a fast unpacker module from fastunpack.c
"""

import cffi
import os
import shutil

with open(os.path.join(os.path.dirname(__file__), 'fastunpack.c')) as f:
    csrc = f.read()
    
cdef, cfunc = csrc.split('# DEF')
modName = '_fastunpack'
ffi = cffi.FFI()
ffi.set_source(modName, cfunc)
ffi.cdef(cdef)
ffi.compile()
for mod in [fn for fn in os.listdir() if fn.startswith(modName)]:
    shutil.move(mod, os.path.join(os.path.dirname(__file__), mod))