"""
build
*****

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2015
:license: GNU Public License version 3

A simple cx_freeze build script.
"""

import sys
import os
from cx_Freeze import setup, Executable
from librpgmakertrans.version import version

base = None
includeFiles = ['README.txt', 'LICENSE.txt']

if sys.platform == 'win32':
    includeFiles.extend([(os.path.join('..', 'librpgmakertrans', 'workers', 'rbpatcher', 'pruby'),
                          'pruby'),
                         (os.path.join('..', 'librpgmakertrans', 'workers', 'rbpatcher', 'rubyscripts'),
                          'rubyscripts'), ])
    base = "Win32GUI"
    icoext = '.ico'
else:
    base = None
    icoext = '.svg'

build_exe_options = {"include_files": includeFiles}

build_exe_options['icon'] = os.path.abspath('rpgtranslogo%s' % icoext)

setup(
    name= "RPGMaker Trans %s" % version,
    version= str(version),
    description="Translation tool for RPGMaker games",
    executables=[Executable("__main__.py", base="base", targetName="RPGMakerTrans")],
    options={'build_exe': build_exe_options},
)


