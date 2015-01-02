"""
headless2k
**********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2015
:license: GNU Public License version 3

Headless specialised for 2k Games
"""
import os

from ..workers.twokpatcher import process2kgame
from ..workers.sniffers import sniffer, SniffedType, checkForFiles
from .headless import Headless

class Headless2k(Headless):
    """Headless specialised for 2k games"""
    copyIgnoreExts = ['.lmu', '.ldb', '.lsd']

    def processGame(self, indir, outdir, translator, mtimes, newmtimes):
        self.submit('patcher', process2kgame, indir, outdir,
                    translator, mtimes=mtimes, newmtimes=newmtimes,
                    comsout=self.inputcoms)

class RPG2k(SniffedType):
    """Sniffed type for an untranslated 2k game"""
    maintype, subtypes = 'GAME', ['2k']
    headlessClass = Headless2k

@sniffer(RPG2k)
def sniff2kGame(path):
    """Sniffer for 2k games"""
    req = {'RPG_RT.LDB': False,
           'RPGMKTRANSPATCH': True,
           'RPGMKTRANSLATED': True, }
    return checkForFiles(path, req)

@sniffer(RPG2k)
def sniff2kGameFile(path):
    """Sniffer for 2k games, given a RPG_RT.EXE file"""
    if os.path.isfile(path) and path.upper().endswith('RPG_RT.EXE'):
        return sniff2kGame(os.path.split(path)[0])
    return False