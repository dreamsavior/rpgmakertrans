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

from cx_Freeze import setup, Executable
from rpgmakertransv2.version import version

base = None
setup(
    name="RPGMaker Trans CLI" % version,
    version="%s" % version,
    description="Translation tool for RPGMaker games, CLI mode",
    executables=[Executable("rpgmakertrans_cli.py", base=base)])

if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="RPGMaker Trans" % version,
    version="%s" version,
    description="Translation tool for RPGMaker games",
    executables=[Executable("rpgmakertrans_gui.py", base=base)])
