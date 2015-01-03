"""
vxunpacker
**********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2015
:license: GNU Public License version 3

Provides the functions to unpack an RPGMaker VX file. Would also work on XP.
"""

import os
import struct
import multiprocessing

def keyGen(baseKey):
    """Generate keys. Can be communicated to to get a key without advancing"""
    current = baseKey
    while True:
        stay = yield current
        if not stay:
            current = (current * 7 + 3) & 0xFFFFFFFF

def unpackData(fileName, key, data):
    """Write unpacked data to the given filename, using key to
    unscramble the given data"""
    fileSize = len(data)
    padding = b'\x00' * (4 - len(data) % 4)
    data += padding
    frmt = 'I' * (len(data) // 4)
    unpacked = struct.unpack(frmt, data)
    decrypted = [x ^ k for x, k in zip(unpacked, keyGen(key))]
    decryptedPacked = struct.pack(frmt, *decrypted)[:fileSize]
    f = open(fileName, 'wb')
    f.write(decryptedPacked)
    f.close()

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
        if os.name == 'posix':
            fileName = fileName.replace('\\', '/')
        yield (fileName, fileKey, rgssadData[pos:pos+fileSize])
        pos += fileSize

def unpackFile(fileName, unpackFunc=unpackData):
    """Unpack an rgssad file; creates directory structure as needed"""
    with open(fileName, 'rb') as f:
        rgssadData = f.read()
    flag1, flag2 = struct.unpack('II', rgssadData[0:8])
    if flag1 != 0x53534752 or flag2 != 0x01004441:
        raise ValueError('Game File is corrupt')

    gameDirName = os.path.abspath(os.path.dirname(fileName))

    for archiveFileName, fileKey, data in rgssadSplitter(rgssadData):
        fileName = os.path.join(gameDirName, archiveFileName)
        dirName = os.path.dirname(fileName)
        if not os.path.exists(dirName):
            os.makedirs(dirName)
        unpackFunc(fileName, fileKey, data)

def mpunpackFile(fileName):
    """Multiprocessing version of unpackFile to test flexibility
    of the unpackFunc parameter in unpackFile"""
    pool = multiprocessing.Pool()
    mpunpack = lambda x,y,z: pool.apply_async(unpackData, [x,y,z])
    unpackFile(fileName, mpunpack)
    pool.close()
    pool.join()

if __name__ == '__main__':
    mpunpackFile('/home/habisain/workspace/liliumunion/Game.rgss2a')