"""
vxunpacker
**********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2015
:license: GNU Public License version 3

Provides the functions to unpack an RPGMaker VX file. Would also work on XP.
"""

import struct

from .common import keyGen, Splitter

@Splitter(1)
def rgssadSplitter(rgssadData):
    """Given the contents of an rgssad file, extract the appropriate
    parameters for use in unpacking the file"""
    pos = 8
    keys = keyGen(0xDEADCAFE)
    next(keys) # Start the generator
    while pos < len(rgssadData):
        fileNameSize = (struct.unpack('I', rgssadData[pos:pos+4])[0]
                        ^ keys.send(True)) # Do not advance at this stage
        pos += 4
        fileNameBytes = bytes((rgssadData[pos+x] ^ next(keys)) & 0xFF
                              for x in range(fileNameSize))
        fileName = fileNameBytes.decode('utf-8')
        pos += fileNameSize
        fileSize = struct.unpack('I', rgssadData[pos:pos+4])[0] ^ next(keys)
        pos += 4
        fileKey = next(keys)
        yield (fileName, fileKey, rgssadData[pos:pos+fileSize])
        pos += fileSize

