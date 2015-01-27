"""
rpgmakertrans_gui
*****************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

A simple bootstrap script which runs the patcher, with support for
freezing.
"""
import sys
import itertools
from multiprocessing import freeze_support
from librpgmakertrans.interface.guicontroller import GUIController
from librpgmakertrans.controllers.coreprotocol import CoreRunner
from librpgmakertrans.workers.sniffers import sniff

if __name__ == '__main__':
    freeze_support()
    runner = CoreRunner()
    guicontroller = runner.initialise(GUIController)
    sniffedData = itertools.chain.from_iterable([sniff(path) for path in sys.argv[1:]])
    if sniffedData:
        guicontroller.setUpSniffedData(sniffedData)
    runner.run()
