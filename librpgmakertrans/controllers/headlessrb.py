"""
headlessvx
**********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2015
:license: GNU Public License version 3

HeadlessVX is the blind patching engine for RPGMaker VX games. It
communicates progress/errors to an interface and coordinates
progress/errors to an interface and coordinates worker progress
(including Ruby processes by RBComms).
"""

import os

from .headless import Headless
from ..workers.rbpatcher import startRBComms, patchGameIni
from ..workers.rubyparse import rbOneOffTranslation
from ..workers.sniffers import sniffer, SniffedType, translatedSniffer

class HeadlessRB(Headless):
    """Headless specialised for Ruby based games.
    Needs further specialisation"""
    
    defaultPatchVersion = 3
    minPatcherProcesses = 2

    def makeFilesToProcess(self, indir, outdir):
        """Make the list of files to process."""
        files = {}
        indir = os.path.normcase(indir)
        dataExt = type(self).dataExtension
        for fn in os.listdir(indir):
            if fn.lower().endswith(dataExt): 
                mapTo = (os.path.join(outdir, fn),
                         fn.lower().rpartition(dataExt)[0].title())
                files[os.path.join(indir, os.path.normcase(fn))] = mapTo 
        return files
    
    def translateScript(self, scriptName, script, translator, outputComs, errorComs):
        """Submit a script for translation"""
        self.submit('patcher', rbOneOffTranslation, outputComs, errorComs, scriptName,
                    script, translator)

    def processGame(self, indir, outdir, translator, mtimes, newmtimes,
                    config):
        """Process a VX game"""
        rbCommsIn = self.senderManager.Sender()
        self.registerSender(rbCommsIn)
        inifn = os.path.normcase(os.path.join(indir, 'Game.ini'))
        if os.path.isfile(inifn):
            self.submit('patcher', patchGameIni, inifn,
                        os.path.join(outdir, 'Game.ini'), translator,
                        self.outputcoms)
        else:
            self.outputcoms.send('nonfatalError',
                                 'Could not find Game.ini file')
        indir = os.path.join(indir, 'Data')
        outdir = os.path.join(outdir, 'Data')
        filesToProcess = self.makeFilesToProcess(indir, outdir)
        self.submit('patcher', startRBComms, filesToProcess,
                    translator, mtimes=mtimes, newmtimes=newmtimes,
                    outputComs=self.inputcoms, inputComs=rbCommsIn,
                    socket=config.socket, rpgversion=type(self).rpgversion)
              
class HeadlessXP(HeadlessRB):
    """Headless specialised for XP games."""
    copyIgnoreExts = ['.rxdata']
    dataExtension = '.rxdata'
    rpgversion = 'xp'
    arcName = 'Game.rgssad'
    
class HeadlessVX(HeadlessRB):
    """Headless specialised for VX games."""
    copyIgnoreExts = ['.rvdata']
    dataExtension = '.rvdata'
    rpgversion = 'vx'
    arcName = 'Game.rgss2a'
    
class HeadlessVXAce(HeadlessRB):
    """Headless specialised for VX games."""
    copyIgnoreExts = ['.rvdata2']
    dataExtension = '.rvdata2'
    rpgversion = 'vxace'
    arcName = 'Game.rgss3a'

class RPGXPUnpacked(SniffedType):
    """Sniffed type for an untranslated unpacked VX game"""
    maintype, subtypes = 'GAME', ['XP']
    headlessClass = HeadlessXP

class RPGXPUnpackedTranslated(SniffedType):
    """Sniffed type for an untranslated unpacked VX game"""
    maintype, subtypes = 'TRANS', ['XP', 'update']

class RPGVXUnpacked(SniffedType):
    """Sniffed type for an untranslated unpacked VX game"""
    maintype, subtypes = 'GAME', ['VX']
    headlessClass = HeadlessVX

class RPGVXUnpackedTranslated(SniffedType):
    """Sniffed type for an untranslated unpacked VX game"""
    maintype, subtypes = 'TRANS', ['VX', 'update']

class RPGVXAceUnpacked(SniffedType):
    """Sniffed type for an untranslated unpacked VX game"""
    maintype, subtypes = 'GAME', ['VXAce']
    headlessClass = HeadlessVXAce

class RPGVXAceUnpackedTranslated(SniffedType):
    """Sniffed type for an untranslated unpacked VX game"""
    maintype, subtypes = 'TRANS', ['VXAce', 'update']

def sniffUnpackedRBGame(path, headlessClass):
    """Sniff an unpacked RB Game"""
    if os.path.isfile(path) and path.upper().endswith('GAME.EXE'):
        return sniffUnpackedRBGame(os.path.split(path)[0], headlessClass)
    elif os.path.isdir(path):
        contents = os.listdir(path)
        arcName = headlessClass.arcName.upper()
        if any(x.upper() == arcName for x in contents):
            return False
        dataDir = os.path.join(path, 'Data')
        dataExt = headlessClass.dataExtension.upper()
        if os.path.isdir(dataDir):
            dataDirContents = os.listdir(dataDir)
            if any(x.upper().endswith(dataExt) for x in dataDirContents):
                return path
    return False

@sniffer(RPGXPUnpacked)
def sniffXPUnpackedGame(path):
    """Sniffer for unpacked VX games"""
    return sniffUnpackedRBGame(path, HeadlessXP)

@sniffer(RPGVXUnpacked)
def sniffVXUnpackedGame(path):
    """Sniffer for unpacked VX games"""
    return sniffUnpackedRBGame(path, HeadlessVX)

@sniffer(RPGVXAceUnpacked)
def sniffVXAceUnpackedGame(path):
    """Sniffer for unpacked VX games"""
    return sniffUnpackedRBGame(path, HeadlessVXAce)

translatedSniffer(RPGXPUnpackedTranslated, sniffXPUnpackedGame)
translatedSniffer(RPGVXUnpackedTranslated, sniffVXUnpackedGame)
translatedSniffer(RPGVXAceUnpackedTranslated, sniffVXAceUnpackedGame)
