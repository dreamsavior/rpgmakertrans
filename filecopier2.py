'''
Created on 3 Sep 2013

@author: habisain
'''

import os.path, shutil
from errorhook import ErrorMeta

class FileCopier(object):
    """Handles copying files from orig directory to target. Does *not* copy patch files."""
    __metaclass__ = ErrorMeta
    
    def __init__(self, indir, outdir,
                 ignoredirs, ignoreexts, ignorefiles, 
                 comsout, translator, mtimes, newmtimes):
        self.indir = os.path.normcase(indir)
        self.outdir = os.path.normcase(outdir)
        self.ignoredirs = [os.path.normcase(x) for x in ignoredirs] +  ['.svn', 'cvs', '.git', '.hg', '.bzr']
        self.ignoreexts = [os.path.normcase(x) for x in ignoreexts]
        self.ignorefiles = [os.path.normcase(x) for x in ignorefiles] 
        self.dirs = []
        self.files = []
        self.comsout = comsout
        self.translator = translator # For future compatibility
        self.mtimes = mtimes
        self.newmtimes = newmtimes
        
    def run(self):
        self.getLists()
        if not os.path.exists(self.outdir):
            os.mkdir(self.outdir)
        patchmarkerfn = os.path.join(self.outdir, 'rpgmktranslated')
        if not os.path.exists(patchmarkerfn):
            with open(patchmarkerfn, 'w') as f:
                f.write('RPGMaker Trans Patched Game. Not for redistribution.\n\n- Habisain')
        for directory in self.dirs:
            os.mkdir(directory)
        copied = 0
        for fid, infn, outfn in self.files:
            self.doCopyFile(fid, infn, outfn)
            copied += 1
            self.comsout.setProgress('copying', copied / len(self.files))
            
    def doCopyFile(self, fid, infn, outfn):
        if os.path.splitext(infn)[1] in self.ignoreexts:
            ret = False
        elif fid in self.ignorefiles:
            ret = False
        else:
            infnmtime = os.path.getmtime(infn)
            self.testFile(infn)
            outfnmtime = self.mtimes.get(outfn, None)
            if infnmtime == outfnmtime:
                ret = False
            else:
                try:
                    shutil.copy(infn, outfn)
                except IOError:
                    raise Exception('Could not copy %s to %s' % (infn, outfn))
                ret = True
        self.newmtimes[outfn] = infnmtime
        return ret

    def changeDir(self, path, partA, partB): 
        if path.startswith(partA):
            path = path.replace(partA, partB, 1)
        else:
            raise Exception('Could not change directory of %s from %s to %s' % (path, partA, partB))
        return path
            
    def getLists(self):
        indir, outdir = self.indir, self.outdir
        
        for path, subdirs, files in os.walk(indir):
            for rm in self.ignoredirs:
                if rm in subdirs: subdirs.remove(rm)
            
            for subdir in subdirs:
                dirname = os.path.normcase(os.path.join(path, subdir))
                transdirname = self.changeDir(dirname, indir, outdir)
                if not os.path.exists(transdirname): 
                    self.dirs.append(transdirname)
                                    
            for fname in files:
                origfile = os.path.normcase(os.path.join(path, fname))
                fid = origfile.replace(indir + os.path.sep, '', 1)
                transfile = self.changeDir(origfile, indir, outdir)
                self.files.append((fid, origfile, transfile))
                
def copyfiles(indir, outdir,
              ignoredirs, ignoreexts, ignorefiles, 
              comsout, translator, mtimes, newmtimes):
    x = FileCopier(indir, outdir,
                 ignoredirs, ignoreexts, ignorefiles, 
                 comsout, translator, mtimes, newmtimes)
    x.run()
                
            
