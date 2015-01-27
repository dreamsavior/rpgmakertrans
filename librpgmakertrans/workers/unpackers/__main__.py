"""
unpacker.__main__
*****************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2015
:license: GNU Public License version 3

Very simple module running behaviour for testing purposes.
Simply unpack the RGSS archive on command line.
"""

import sys

from .common import mpunpackFile

mpunpackFile(sys.argv[1])
