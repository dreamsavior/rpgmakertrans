"""
rpgmt
*****

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

A simple bootstrap script which runs the patcher in CLI mode.

NOTE: This is a workaround script for the deadlock experienced in
Windows if using python -m cli
"""

from multiprocessing import freeze_support
from cli.cli import launchCLI
    
if __name__ == '__main__':
    freeze_support()
    launchCLI()

