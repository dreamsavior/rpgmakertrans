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

class HeadlessVX(Headless):
    """Headless specialised for VX games."""

    copyIgnoreExts = ['.rvdata', '.rvdata2', '.rxdata']

    defaultPatchVersion = 3
    minPatcherProcesses = 2

    def translateScript(self, scriptName, script, translator, outputComs, errorComs):
        """Submit a script for translation"""
        self.submit('patcher', rbOneOffTranslation, outputComs, errorComs, scriptName,
                    script, translator)

    def processGame(self, indir, outdir, translator, mtimes, newmtimes,
                    config):
        """Process a VX game"""
        rbCommsIn = self.senderManager.Sender()
        self.registerSender(rbCommsIn)
        inifn = os.path.join(indir, 'Game.ini')
        if os.path.isfile(inifn):
            self.submit('patcher', patchGameIni, inifn,
                        os.path.join(outdir, 'Game.ini'), translator,
                        self.outputcoms)
        else:
            self.outputcoms.send('nonfatalError',
                                 'Could not find Game.ini file')
        indir = os.path.join(indir, 'Data')
        outdir = os.path.join(outdir, 'Data')
        self.submit('patcher', startRBComms, indir, outdir,
                    translator, mtimes=mtimes, newmtimes=newmtimes,
                    outputComs=self.inputcoms, inputComs=rbCommsIn,
                    socket=config.socket)

class RPGVXUnencrypted(SniffedType):
    """Sniffed type for an untranslated unencrypted VX game"""
    maintype, subtypes = 'GAME', ['VX']
    headlessClass = HeadlessVX

class RPGVXUnencryptedTranslated(SniffedType):
    """Sniffed type for an untranslated unencrypted VX game"""
    maintype, subtypes = 'TRANS', ['VX', 'update']

@sniffer(RPGVXUnencrypted)
def sniffVXUnencryptedGame(path):
    """Sniffer for unencrypted VX games"""
    if os.path.isfile(path) and path.upper().endswith('GAME.EXE'):
        return sniffVXUnencryptedGame(os.path.split(path)[0])
    elif os.path.isdir(path):
        contents = os.listdir(path)
        if any(x.upper() == 'GAME.RGSS2A' for x in contents):
            return False
        dataDir = os.path.join(path, 'Data')
        if os.path.isdir(dataDir):
            dataDirContents = os.listdir(dataDir)
            if any(x.upper().endswith('.RVDATA') for x in dataDirContents):
                return path
    return False

translatedSniffer(RPGVXUnencryptedTranslated, sniffVXUnencryptedGame)