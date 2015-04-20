"""
rpgmakertrans
*************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

A simple bootstrap script which runs the patcher, with support for
freezing.

NOTE: This is a workaround script for the deadlock experienced in
Windows if using python -m gui
"""

from multiprocessing import freeze_support
from gui.guicontroller import launchGUI
    
if __name__ == '__main__':
    freeze_support()
    launchGUI()
    
