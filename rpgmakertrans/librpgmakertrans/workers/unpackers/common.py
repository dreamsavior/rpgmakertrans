"""
common
******

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2015
:license: GNU Public License version 3

Provides the common functions to unpack RPGMaker XP/VX/VX Ace files.
"""

try:
    from . import _fastunpack
except ImportError:
    _fastunpack = None

import multiprocessing
import struct
import os

from concurrent.futures import ThreadPoolExecutor

SPLITTERS = {}

def Splitter(version):
    """Decorator to register a splitter as handling a given RGSSAD verion"""
    def wrap(splitter):
        """Register the splitter"""
        SPLITTERS[version] = splitter
        return splitter
    return wrap

def keyGen(baseKey):
    """Generate keys. Can be communicated to to get a key without advancing"""
    current = baseKey
    while True:
        stay = yield current
        if not stay:
            current = (current * 7 + 3) & 0xFFFFFFFF

if _fastunpack is None:
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
else:
    def unpackData(fileName, key, data):
        """Write unpacked data to the given filename, using key to
        unscramble the given data. This function uses the fast C unpacker"""
        fileSize = len(data)
        padding = b'\x00' * (4 - len(data) % 4)
        data += padding
        ffi = _fastunpack.ffi
        lib = _fastunpack.lib
        cdata = ffi.new('unsigned char[]', data)
        lib.unpackData(key, len(data) // 4, cdata)
        decryptedPacked = ffi.buffer(cdata, fileSize)
        f = open(fileName, 'wb')
        f.write(decryptedPacked)
        f.close()
        
def unpackFile(fileName, unpackFunc=unpackData):
    """Unpack an rgssad file; creates directory structure as needed"""
    with open(fileName, 'rb') as f:
        rgssadData = f.read()
    versionString = rgssadData[0:8]
    if not versionString.startswith(b'RGSSAD\x00'):
        raise ValueError('Game File is corrupt')
    archiveVersion = versionString[-1]
    if archiveVersion in SPLITTERS:
        splitterFunc = SPLITTERS[archiveVersion]
    else:
        raise ValueError('This unpacker does not support RGSSAD Version %s' % archiveVersion)
    gameDirName = os.path.abspath(os.path.dirname(fileName))

    for archiveFileName, fileKey, data in splitterFunc(rgssadData):
        if os.name == 'posix':
            archiveFileName = archiveFileName.replace('\\', '/')
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
    
def threadUnpackFile(fileName):
    """Threading unpacker. Only makes sense to use if using the C unpacker,
    but performance should be significantly better than mpunpack on
    Windows. Again, a test function only."""
    futures = []
    cpus = os.cpu_count()
    with ThreadPoolExecutor(max_workers=cpus) as e:
        threadUnpack = lambda x,y,z: futures.append(e.submit(unpackData, x, y, z))
        unpackFile(fileName, threadUnpack)
    for res in futures:
        res.result()