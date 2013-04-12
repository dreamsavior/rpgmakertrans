import os, os.path, shutil
from errorhook import ErrorMeta

FILECOPIER = None
MTIMES = None

def setup(*args):
    global FILECOPIER, BACKEND, MTIMES
    FILECOPIER = FileCopier(*args[0])
    MTIMES = args[1]
    
def copydirectorystructure():
    global FILECOPIER
    FILECOPIER.copydirectorystructure()
    
def copyfiles():
    global FILECOPIER, MTIMES
    return FILECOPIER.copyfiles(MTIMES)
    
class FileCopier(object):
    """Handles copying files from orig directory to target. Does *not* copy patch files"""
    __metaclass__ = ErrorMeta
    
    def __init__(self, indir, outdir, inlocale, outlocale, ignoredirs, ignoreexts, ignorefiles):
        self.inlocale = inlocale
        self.outlocale = outlocale
        self.indir = os.path.normcase(indir)
        self.outdir = os.path.normcase(outdir)
        self.ignoredirs = [os.path.normcase(x) for x in ignoredirs] +  ['.svn', 'cvs', '.git', '.hg', '.bzr']
        self.ignoreexts = [os.path.normcase(x) for x in ignoreexts]
        self.ignorefiles = [os.path.normcase(x) for x in ignorefiles] 

    def changeDir(self, path, partA, partB): 
        if path.startswith(partA):
            path = path.replace(partA, partB, 1)
        else:
            raise Exception('Could not change directory of %s from %s to %s' % (path, partA, partB))
        return path
       
    def copydirectorystructure(self):
        indir, outdir = self.indir, self.outdir
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        for path, subdirs, _ in os.walk(indir):
            for rm in self.ignoredirs:
                if rm in subdirs: subdirs.remove(rm)
            
            for subdir in subdirs:
                dirname = os.path.normcase(os.path.join(path, subdir))
                transdirname = self.changeDir(dirname, indir, outdir)
                if not os.path.exists(transdirname): 
                    os.mkdir(transdirname)
        patchmarkerfn = os.path.join(self.outdir, 'rpgmktranslated')
        if not os.path.exists(patchmarkerfn):
            with open(patchmarkerfn, 'w') as f:
                f.write('RPGMaker Trans Patched Game. Not for redistribution.\n\n- Habisain')
        
    def testFile(self, fn):
        try:
            f = open(fn, 'r')
            f.close()
        except:
            raise Exception('Could not access file %s' % fn)
        
    def doCopyfile(self, fid, infn, outfn, infnmtime, mtimes, newmtimes):
        print fid, self.ignorefiles
        if os.path.splitext(infn)[1] in self.ignoreexts:
            ret = False
        elif fid in self.ignorefiles:
            ret = False
        else:
            self.testFile(infn)
            outfnmtime = mtimes.get(outfn, None)
            if infnmtime == outfnmtime:
                ret = False
            else:
                try:
                    shutil.copy(infn, outfn)
                except IOError:
                    raise Exception('Could not copy %s to %s' % (infn, outfn))
                ret = True
        newmtimes[outfn] = infnmtime
        return ret
            
    def copyfiles(self, mtimes):
        indir, outdir = self.indir, self.outdir
        newmtimes = {}
        for path, subdirs, files in os.walk(indir):
            for rm in self.ignoredirs:
                if rm in subdirs: subdirs.remove(rm)
                
            for fname in files:
                origfile = os.path.normcase(os.path.join(path, fname))
                fid = origfile.replace(indir + os.path.sep, '', 1)
                
                transfile = self.changeDir(origfile, indir, outdir)
                self.doCopyfile(fid, origfile, transfile, os.path.getmtime(origfile), 
                                mtimes, newmtimes)
                
        return newmtimes
        
if __name__ == '__main__':
    gamepath = '/home/habisain/tr/rrpg'
    patchpath = gamepath + '_patch'
    transpath = gamepath + '_translated'
    
    copierargs = [gamepath, transpath, 'cp932', 'cp932', [], ['.ldb', '.lmu'], ['RPG_RT.exe']]
    mtimes = {}
    setup(copierargs, mtimes)
    copydirectorystructure()
    copyfiles()
          
