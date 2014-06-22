"""
rpgmakertransmain
*****************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

A simple bootstrap script which runs the patcher, with support for
freezing.
"""

from multiprocessing import freeze_support
from rpgmakertransv2.interface.guicontroller import GUIController
from rpgmakertransv2.controllers.coreprotocol import CoreRunner
from rpgmakertransv2.interface.cli import useCLIBackend, CLIBackend

if __name__ == '__main__':
    freeze_support()
    runner = CoreRunner()
    if useCLIBackend():
        CLIBackend(runner)
    else:
        runner.initialise(GUIController)
    runner.run()
