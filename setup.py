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

build_exe_options = {
"include_files": [(os.path.join('librpgmakertrans', 'workers', 'rbpatcher', 'pruby'),
                   'pruby'),
                  (os.path.join('librpgmakertrans', 'workers', 'rbpatcher', 'rubyscripts'),
                   'rubyscripts'),]
}

build_exe_cli_options = build_exe_options.copy()
icoext = '.ico' if os.name == 'nt' else '.svg'
build_exe_cli_options['icon'] = os.path.abspath(os.path.join('icons', 'rpgtranslogocli%s' % icoext))
build_exe_gui_options = build_exe_options.copy()
build_exe_gui_options['icon'] = os.path.abspath(os.path.join('icons', 'rpgtranslogo%s' % icoext))

setup(
    name="RPGMaker Trans CLI %s" % version,
    version="%s" % version,
    description="Translation tool for RPGMaker games, CLI mode",
    executables=[Executable("rpgmakertrans_cli.py", base=base)],
    options={'build_exe': build_exe_cli_options},
)

if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="RPGMaker Trans %s" % version,
    version="%s" % version,
    description="Translation tool for RPGMaker games",
    executables=[Executable("rpgmakertrans_gui.py", base=base)],
    options={'build_exe': build_exe_gui_options},
)