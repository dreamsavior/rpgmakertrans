"""
cli.__main__
************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

A simple bootstrap script which runs the patcher in CLI mode.
"""

from multiprocessing import freeze_support
from librpgmakertrans.controllers.coreprotocol import CoreRunner
from .cli import CLIBackend

import sys, os
if os.path.split(sys.argv[0])[1] == '__main__.py':
    sys.argv[0] = 'rpgmakertrans.cli'
    
if __name__ == '__main__':
    freeze_support()
    runner = CoreRunner()
    CLIBackend(runner)
    runner.run()
