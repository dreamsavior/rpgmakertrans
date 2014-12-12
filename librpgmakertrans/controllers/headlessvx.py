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

from .headless import Headless

class HeadlessVX(Headless):
    processGameFunc = None
    copyIgnoreExts = ['.rvdata', '.rvdata2', '.rxdata']