'''
headlessvxarc
*************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

A Headless implementation to unpack VX archives
'''
import os

from .headless import HeadlessUtils
from ..workers.vxunpacker import unpackFile, unpackData
from ..workers.sniffers import sniffer, SniffedType

def unpackDataAndNotify(fileName, key, data, outputComs):
    """Unpacks data and notify on the given coms channel"""
    unpackData(fileName, key, data)
    outputComs.send('incProgress', 'unpacking')

class HeadlessVXArc(HeadlessUtils):
    """Headless implementation to unpack an encrypted game"""

    arcName = 'Game.rgss2a'

    def __init__(self, *args, **kwargs):
        """Initialise the task counter"""
        super().__init__(*args, **kwargs)
        self.tasks = 0

    def unpackData(self, fileName, key, data):
        """Submit an unpackData job"""
        self.tasks += 1
        self.submit('unpack', unpackDataAndNotify,
                    fileName, key, data, self.inputcoms)

    def go(self, gamePath, patchPath, transPath, useBOM):
        """Start decryption"""
        self.setupPool('unpack')
        # Slightly strange way to find something that's ultimately
        # case insensitive on potentially case sensitive file systems
        arcNameLS = [x for x in os.listdir(gamePath)
                     if x.upper() == type(self).arcName.upper()]
        if arcNameLS:
            arcFileName = os.path.join(gamePath, arcNameLS[0])
            self.displayMessage('Reading Archive Structure')
            unpackFile(arcFileName, self.unpackData)
            self.setProgressDiv('unpacking', self.tasks)
            self.setProgressCompleteTrigger('unpacking', 'finish')
            self.localWaitUntil('finish', self.finish, arcFileName)
        else:
            raise Exception('Could not determine archive name')

    def finish(self, arcFileName):
        """Finish the unpacking process.
        TODO: I need to work out how to handle the fact that this normally
        needs to chain onto HeadlessVX, but not necessarily. At present,
        it issues the finishedPatching command and does nothing
        FIXME"""
        self.outputcoms.send('finishedPatching')
        self.displayMessage('Deleting original archive')
        self.shutdown(['unpack'])
        os.remove(arcFileName)
        self.going = False

class RPGVXPacked(SniffedType):
    """Sniffed type for an untranslated packed VX game"""
    maintype, subtypes = 'GAME', ['VX', 'ARC']
    headlessClass = HeadlessVXArc

@sniffer(RPGVXPacked)
def sniffVXEncryptedGame(path):
    """Sniffer for encrypted VX games"""
    if os.path.isfile(path):
        return sniffVXEncryptedGame(os.path.split(path)[0])
    elif os.path.isdir(path):
        pathContents = os.listdir(path)
        if any(x.upper().endswith('GAME.RGSS2A') for x in pathContents):
            return path
        else:
            return False
    else:
        return False