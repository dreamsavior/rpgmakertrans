"""
headlessvx
**********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

HeadlessVX is the blind patching engine for RPGMaker VX games. It
communicates progress/errors to an interface and coordinates
progress/errors to an interface and coordinates worker progress
(including Ruby processes by RBComms).
"""

import os

from .headless import Headless
from ..workers.rbpatcher import startRBComms
from ..workers.rubyparse import rbOneOffTranslation

class HeadlessVX(Headless):
    """Headless specialised for VX games."""

    copyIgnoreExts = ['.rvdata', '.rvdata2', '.rxdata']

    defaultPatchVersion = 3
    minPatcherProcesses = 2

    def translateScript(self, scriptName, script, translator, outputComs):
        """Submit a script for translation"""
        self.submit('patcher', rbOneOffTranslation, outputComs, scriptName,
                    script, translator)

    def processGame(self, indir, outdir, translator, mtimes, newmtimes):
        """Process a VX game"""
        rbCommsIn = self.senderManager.Sender()
        self.registerSender(rbCommsIn)
        indir = os.path.join(indir, 'Data')
        outdir = os.path.join(outdir, 'Data')
        self.submit('patcher', startRBComms, indir, outdir,
                    translator, mtimes=mtimes, newmtimes=newmtimes,
                    outputComs=self.inputcoms, inputComs=rbCommsIn)
