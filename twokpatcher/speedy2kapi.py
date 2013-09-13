import os

from speedy2k import TwoKRPGFile

def process2kfile(inFileName, outFileName, mtimes, translator, dbgid=None):
    # Args: inFileName: input file name
    # outFileName: output file name
    # mtimes: the mtimes dictionary    
    name = os.path.split(inFileName)[1].rpartition('.')[0].upper()
    ret = (os.path.getmtime(inFileName), translator.mtime)
    needOutput = (mtimes.get(name, None) != ret) or not os.path.exists(outFileName)
    if needOutput:
        rpgfile = TwoKRPGFile(name, inFileName, translator)
        rpgfile.parse()
        rpgfile.outputfile(outFileName)            
    if dbgid:
        return ret, dbgid
    else:
        return ret
