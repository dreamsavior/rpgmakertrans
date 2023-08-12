"""
gui.__main__
************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

A simple bootstrap script which runs the patcher, with support for
freezing.
"""

from multiprocessing import freeze_support
from .guicontroller import launchGUI
    
if __name__ == '__main__':
    freeze_support()
    launchGUI()
    
