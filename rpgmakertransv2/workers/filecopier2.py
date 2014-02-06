'''
Created on 3 Sep 2013

@author: habisain
'''


import os.path, shutil
from .fileops import (getmtime, pathexists, isfile, remove, mkdir, walk, WinOpen, copy)
from ..errorhook import ErrorMeta, errorWrap

class FileCopier(object, metaclass=ErrorMeta):
    """Handles copying files from orig directory to target. Does *not* copy patch files."""
    def __init__(self, indir, outdir,
                 ignoredirs, ignoreexts, ignorefiles, 
                 comsout, translator, mtimes, newmtimes,
                 progresssig, dirssig, *args, **kwargs):
        super(FileCopier, self).__init__(*args, **kwargs)
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
        self.progresssig = progresssig
        self.dirssig = dirssig
        
    def doCopyDirs(self):
        for directory in self.dirs:
            if pathexists(directory):
                if isfile(directory):
                    remove(directory)
            mkdir(directory)
        
    def run(self):
        self.getLists()
        if not pathexists(self.outdir):
            mkdir(self.outdir)
        patchmarkerfn = os.path.join(self.outdir, 'rpgmktranslated')
        if not pathexists(patchmarkerfn):
            with WinOpen(patchmarkerfn, 'w') as f:
                f.write('RPGMaker Trans Patched Game. Not for redistribution.\n\n- Habisain')
        self.doCopyDirs()
        if self.dirssig: 
            self.comsout.send('trigger', self.dirssig)
        if self.progresssig: 
            self.comsout.send('setProgressDiv', self.progresssig, len(self.files))
        for fid, infn, outfn in self.files:
            self.doCopyFile(fid, infn, outfn)
            if self.progresssig: 
                self.comsout.send('incProgress', self.progresssig)
            
    def doCopyFile(self, fid, infn, outfn):
        infnmtime = getmtime(infn)
        #self.testFile(infn)
        outfnmtime = self.mtimes.get(outfn, None)
        if infnmtime != outfnmtime:
            try:
                copy(infn, outfn)
            except IOError:
                raise Exception('Could not copy %s to %s' % (infn, outfn))
        self.newmtimes[outfn] = infnmtime

    def changeDir(self, path, partA, partB): 
        if path.startswith(partA):
            path = path.replace(partA, partB, 1)
        else:
            raise Exception('Could not change directory of %s from %s to %s' % (path, partA, partB))
        return path
            
    def getLists(self):
        indir, outdir = self.indir, self.outdir
        
        for path, subdirs, files in walk(indir):
            for rm in self.ignoredirs:
                if rm in subdirs: subdirs.remove(rm)
            
            for subdir in subdirs:
                dirname = os.path.normcase(os.path.join(path, subdir))
                transdirname = self.changeDir(dirname, indir, outdir)
                if not pathexists(transdirname): 
                    self.dirs.append(transdirname)
            for fname in files:
                origfile = os.path.normcase(os.path.join(path, fname))
                fid = origfile.replace(indir + os.path.sep, '', 1)
                transfile = self.changeDir(origfile, indir, outdir)
                ext = os.path.splitext(fname)[1]
                if not (fid in self.ignorefiles or ext in self.ignoreexts):
                    self.files.append((fid, origfile, transfile))
@errorWrap
def copyfilesAndTrigger(indir, outdir,
              ignoredirs, ignoreexts, ignorefiles, 
              comsout, translator, mtimes, newmtimes,
              progresssig, dirssig):
    copyfiles(indir, outdir,
              ignoredirs, ignoreexts, ignorefiles, 
              comsout, translator, mtimes, newmtimes,
              progresssig, dirssig)
    comsout.send('trigger', 'fileCopyDone')

@errorWrap      
def copyfiles(indir, outdir,
              ignoredirs, ignoreexts, ignorefiles, 
              comsout, translator, mtimes, newmtimes,
              progresssig, dirssig):
    x = FileCopier(indir, outdir,
                 ignoredirs, ignoreexts, ignorefiles, 
                 comsout, translator, mtimes, newmtimes,
                 progresssig, dirssig)
    x.run()
                
            
