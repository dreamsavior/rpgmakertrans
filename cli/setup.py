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
    includeFiles.extend([(os.path.join('librpgmakertrans', 'workers', 'rbpatcher', 'pruby'),
                          'pruby'),
                         (os.path.join('librpgmakertrans', 'workers', 'rbpatcher', 'rubyscripts'),
                          'rubyscripts'), ])
    icopath = os.path.join('cli', 'rpgtranslogocli.ico')
    ext = '.exe'
    mainscript = 'rpgmt.py'
    paths = [os.path.dirname(__file__)]
else:
    ext = ''
    icoext = '.svg'
    mainscript = '__main__.py'
    paths = []

build_exe_options = {"include_files": includeFiles}
build_exe_options['icon'] = os.path.abspath(icopath)
build_exe_options['build_exe'] = 'rpgmt_cli_v%s' % version

setup(
    name= "RPGMaker Trans CLI %s" % version,
    version= str(version),
    description="Translation tool for RPGMaker games, CLI Version",
    executables=[Executable(mainscript, base=None, path=paths, targetName='rpgmt%s' % ext)],
    options={'build_exe': build_exe_options},
)


