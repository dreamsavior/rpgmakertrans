"""
headlessvx
**********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

HeadlessVX is the blind patching engine for RPGMaker VX games. As
with Headless (for 2k games), it communicates progress/errors to an
interface and coordinates progress/errors to an interface and
coordinates worker progress (including Ruby processes by Sockets).
"""

import os

from .headless import Headless
from ..workers.rbpatcher import startRBComms
from ..workers.rubyparse import rbOneOffTranslation

# TODO: Work out if I should force patcher to have more than 2 processes
# or alternatively some other pool?

class HeadlessVX(Headless):
    copyIgnoreExts = ['.rvdata', '.rvdata2', '.rxdata']
    
    def translateScript(self, scriptName, script, translator, outputComs):
        self.submit('patcher', rbOneOffTranslation, outputComs, scriptName,
                    script, translator)
            
    def processGame(self, indir, outdir, translator, mtimes, newmtimes):
        rbCommsIn = self.senderManager.Sender()
        indir = os.path.join(indir, 'Data')
        self.submit('patcher', startRBComms, indir, outdir, 
                    translator, mtimes=mtimes, newmtimes=newmtimes, 
                    outputComs=self.inputcoms, inputComs=rbCommsIn)
