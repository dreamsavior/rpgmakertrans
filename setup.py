"""
build
*****

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

A simple cx_freeze build script.

TODO: Check to see if this works with the icon, or if it needs extra stuff,
or if I should embed the SVG into a Python file or something.
"""

import sys
import os
from cx_Freeze import setup, Executable
from librpgmakertrans.version import version

base = None
includeFiles = ['README.txt', 'LICENSE.txt']

if sys.platform == 'win32':
    includeFiles.extend([(os.path.join('librpgmakertrans', 'workers', 'rbpatcher', 'pruby'),
                          'pruby'),
                         (os.path.join('librpgmakertrans', 'workers', 'rbpatcher', 'rubyscripts'),
                          'rubyscripts'), ])

build_exe_options = {"include_files": includeFiles}

icoext = '.ico' if sys.platform == 'win32' else '.svg'

if '--cli' in sys.argv:
    sys.argv.remove('--cli')
    baseScript = "rpgmakertrans_cli.py"
    name = "RPGMaker Trans CLI %s"
    build_exe_options['icon'] = os.path.abspath(os.path.join('icons', 'rpgtranslogocli%s' % icoext))

else:
    baseScript = "rpgmakertrans_gui.py"
    if sys.platform == "win32":
        base = "Win32GUI"
    name = "RPGMaker Trans %s"
    build_exe_options['icon'] = os.path.abspath(os.path.join('icons', 'rpgtranslogo%s' % icoext))

setup(
    name= name % version,
    version= str(version),
    description="Translation tool for RPGMaker games",
    executables=[Executable(baseScript, base=base)],
    options={'build_exe': build_exe_options},
)


