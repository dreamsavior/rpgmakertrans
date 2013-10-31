'''
Created on 29 Sep 2013

@author: habisain
'''

import sys

from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
        name = "RPGMaker Trans v2.0",
        version = "2.0",
        description = "Translation tool for RPGMaker games",
        executables = [Executable("rpgmakertransmain.py", base = base)])