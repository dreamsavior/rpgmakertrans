"""
common
******

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2015
:license: GNU Public License version 3

Provides the common functions to unpack RPGMaker XP/VX/VX Ace files.
"""

import struct
import os

def unpackFile(fileName, splitterFunc, unpackFunc):
    """Unpack an rgssad file; creates directory structure as needed"""
    with open(fileName, 'rb') as f:
        rgssadData = f.read()
    flag1, flag2 = struct.unpack('II', rgssadData[0:8])
    if flag1 != 0x53534752 or flag2 != 0x01004441:
        raise ValueError('Game File is corrupt')

    gameDirName = os.path.abspath(os.path.dirname(fileName))

    for archiveFileName, fileKey, data in splitterFunc(rgssadData):
        fileName = os.path.join(gameDirName, archiveFileName)
        dirName = os.path.dirname(fileName)
        if not os.path.exists(dirName):
            os.makedirs(dirName)
        unpackFunc(fileName, fileKey, data)