"""
aceunpacker
***********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2015
:license: GNU Public License version 3

Provides the functions to unpack an RPGMaker VX Ace file.
"""

import struct

from .common import Splitter

def infIter(iterable):
    """Iterate over an iterable forever"""
    while True:
        yield from iterable

@Splitter(3)
def rgss3aSplitter(rgss3aData):
    """Splitter for rgss3a files."""
    pos = 8
    key = struct.unpack('I', rgss3aData[pos:pos+4])[0] * 9 + 3
    keyBytes = struct.pack('I', key)
    pos += 4
    offset, size, fkey, fileNameLength = [n ^ key for n in struct.unpack('IIII', rgss3aData[pos:pos+16])]
    while offset != 0:
        pos += 16
        fileNameBytes = bytes(rgss3aData[pos+x] ^ j for x, j in zip(range(fileNameLength), infIter(keyBytes)))
        fileName = fileNameBytes.decode('utf-8')
        pos += fileNameLength
        yield fileName, fkey, rgss3aData[offset:offset+size]
        offset, size, fkey, fileNameLength = [n ^ key for n in struct.unpack('IIII', rgss3aData[pos:pos+16])]
