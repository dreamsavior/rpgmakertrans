"""
setup
*****

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2015
:license: GNU Public License version 3

A simple cx_freeze build script for the CLI.
"""

import sys
import os
from cx_Freeze import setup, Executable
from librpgmakertrans.version import version

includeFiles = ['README.txt', 'LICENSE.txt']

if sys.platform == 'win32':
    includeFiles.extend([(os.path.join('..', 'librpgmakertrans', 'workers', 'rbpatcher', 'pruby'),
                          'pruby'),
                         (os.path.join('..', 'librpgmakertrans', 'workers', 'rbpatcher', 'rubyscripts'),
                          'rubyscripts'), ])
    icoext = '.ico'
    ext = '.exe'
else:
    ext = ''
    icoext = '.svg'

build_exe_options = {"include_files": includeFiles}

build_exe_options['icon'] = os.path.abspath('rpgtranslogocli%s' % icoext)

setup(
    name= "RPGMaker Trans CLI %s" % version,
    version= str(version),
    description="Translation tool for RPGMaker games, CLI Version",
    executables=[Executable('__main__.py', base=None, targetName='rpgmt%s' % ext)],
    options={'build_exe': build_exe_options},
)


