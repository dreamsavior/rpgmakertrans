import os

## BEGIN INLINE BLOCK
from translator import Translator
from speedy2k import TwoKRPGFile
from speedy2kconstants import rtsubsections
## END INLINE BLOCK

def match2k(extension, dir, original):
    return extension.upper() in ('LMU', 'LDB') and os.path.relpath(dir) == os.path.relpath(original)

def processArbitaryFile2k(inFileName, outFileName, mtimes, patchBackend, id=None):
    # Args: inFileName: input file name
    # outFileName: output file name
    # mtimes: the mtimes dictionary
    if inFileName.upper().endswith('RPG_RT.LDB'):
        ## determine max patch
        patchMTimes = []
        for subsection in rtsubsections:
            name = 'RPG_RT_' + subsection.upper()
            patchMTimes.append(patchBackend.getPatchFileMTime(name))
        patchMTimes = [x for x in patchMTimes if x]
        maxMTime = max(patchMTimes) if patchMTimes else None

        ret = (os.path.getmtime(inFileName), maxMTime)
        needOutput = (mtimes.get('RPG_RT', None) != ret) or not os.path.exists(outFileName)
        
        if needOutput:
            # handle RPG_RT file
            rtTranslator = Translator()
            for subsection in rtsubsections:
                name = 'RPG_RT_' + subsection.upper()
                patchData = patchBackend.getPatchFileData(name)
                rtTranslator.loadTranslatables(patchData)
                
            rpgfile = TwoKRPGFile(inFileName, rtTranslator)
            rpgfile.parse()
            rpgfile.outputfile(outFileName)
            
            for subsection in rtsubsections:
                name = 'RPG_RT_' + subsection.upper()
                newPatchData = rtTranslator.dumpTranslatables(contexts=rtsubsections[subsection])
                patchBackend.writePatchFileData(name, newPatchData)
    else:
        # handle LMU file
        name = os.path.split(inFileName)[1].rpartition('.')[0]
        ret = (os.path.getmtime(inFileName), patchBackend.getPatchFileMTime(name))
        needOutput = (mtimes.get(name, None) != ret) or not os.path.exists(outFileName)
        if needOutput:
            rtTranslator = Translator()
            patchData = patchBackend.getPatchFileData(name)
            rtTranslator.loadTranslatables(patchData)
            rpgfile = TwoKRPGFile(inFileName, rtTranslator)
            rpgfile.parse()
            rpgfile.outputfile(outFileName)
            newPatchData = rtTranslator.dumpTranslatables()
            patchBackend.writePatchFileData(name, newPatchData)
            
    if id:
        return ret, id
    else:
        return ret

if __name__ == '__main__':
    from patchbackend import PatchFileBackEnd
    origdir = 'blankblankgirl'
    patchDir = 'blankblankgirl_patch'
    transdir = 'blankblankgirl_trans'
    backend = PatchFileBackEnd(origdir, patchDir, transdir, 'RPG2k', True)
    infileName = 'blankblankgirl/RPG_RT.ldb'
    mtimes = {} # {'blankblankgirl/Map0001.lmu': (1294705073.0, 1299240878.587328)}
    ret = processArbitaryFile2k(infileName, 'outputtest.ldb', mtimes, backend)
    mtimes[infileName] = ret
    print mtimes
