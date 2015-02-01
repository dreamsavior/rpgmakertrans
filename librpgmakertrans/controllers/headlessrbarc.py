'''
headlessvxarc
*************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

A Headless implementation to unpack packed archives
'''
import os

from .headless import HeadlessUtils
from .headlessvx import HeadlessXP, HeadlessVX, HeadlessVXAce
from ..workers.unpackers import unpackFile, unpackData
from ..workers.sniffers import sniffer, SniffedType

def unpackDataAndNotify(fileName, key, data, outputComs):
    """Unpacks data and notify on the given coms channel"""
    unpackData(fileName, key, data)
    outputComs.send('incProgress', 'unpacking')

class HeadlessArc(HeadlessUtils):
    """Headless implementation to unpack a packed game. Must be
    specialised."""
    
    def __init__(self, *args, **kwargs):
        """Initialise the task counter"""
        super().__init__(*args, **kwargs)
        self.tasks = 0

    def unpackData(self, fileName, key, data):
        """Submit an unpackData job"""
        self.tasks += 1
        self.submit('unpack', unpackDataAndNotify,
                    fileName, key, data, self.inputcoms)

    def go(self, indir, patchPath, outdir, useBOM):
        """Start decryption"""
        self.setupPool('unpack')
        # Slightly strange way to find something that's ultimately
        # case insensitive on potentially case sensitive file systems
        arcNameLS = [x for x in os.listdir(indir)
                     if x.upper() == type(self).arcName.upper()]
        if arcNameLS:
            arcFileName = os.path.join(indir, arcNameLS[0])
            self.setMessage('Reading Archive Structure')
            unpackFile(arcFileName, self.unpackData)
            self.setMessage('Unpacking Archive')
            self.setProgressDiv('unpacking', self.tasks)
            self.setProgressCompleteTrigger('unpacking', 'finish')
            self.localWaitUntil('finish', self.finish, arcFileName)
        else:
            raise Exception('Could not determine archive name')

    def finish(self, arcFileName):
        """Finish the unpacking process."""
        self.displayMessage('Finished Unpacking - Deleting original archive')
        self.resniffInput()
        self.setMessage('')
        self.shutdown(['unpack'])
        os.remove(arcFileName)
        self.going = False

class HeadlessXPArc(HeadlessArc):
    arcName = 'Game.rgssad'
    
class HeadlessVXArc(HeadlessArc):
    arcName = 'Game.rgss2a'

class HeadlessVXAceArc(HeadlessArc):
    arcName = 'Game.rgss3a'

class RPGXPPacked(SniffedType):
    """Sniffed type for an untranslated packed VX game - set to chain
    directly onto a VX game."""
    maintype, subtypes = 'GAME', ['XP', 'ARC']
    headlessClass = (HeadlessXPArc, HeadlessXP)

class RPGVXPacked(SniffedType):
    """Sniffed type for an untranslated packed VX game - set to chain
    directly onto a VX game."""
    maintype, subtypes = 'GAME', ['VX', 'ARC']
    headlessClass = (HeadlessVXArc, HeadlessVX)

class RPGVXAcePacked(SniffedType):
    """Sniffed type for an untranslated packed VX game - set to chain
    directly onto a VX game."""
    maintype, subtypes = 'GAME', ['VXAce', 'ARC']
    headlessClass = (HeadlessVXAceArc, HeadlessVXAce)

def sniffPackedGame(path, unpackClass):
    """Sniffer for packed games"""
    if os.path.isfile(path):
        return sniffPackedGame(os.path.split(path)[0], unpackClass)
    elif os.path.isdir(path):
        arcName = unpackClass.arcName.upper()
        pathContents = os.listdir(path)
        if any(x.upper().endswith(arcName) for x in pathContents):
            return path
        else:
            return False
    else:
        return False

@sniffer(RPGVXPacked)
def sniffXPPackedGame(path):
    """Sniffer for packed XP games"""
    return sniffPackedGame(path, HeadlessXPArc)
    
@sniffer(RPGVXPacked)
def sniffVXPackedGame(path):
    """Sniffer for packed VX games"""
    return sniffPackedGame(path, HeadlessVXArc)

@sniffer(RPGVXAcePacked)
def sniffVXAcePackedGame(path):
    """Sniffer for packed VX games"""
    return sniffPackedGame(path, HeadlessVXAceArc)
