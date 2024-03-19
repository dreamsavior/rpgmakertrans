"""
filecopier2
***********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

A file copier, to be used whenever it is necessary to copy a filtered
list of files from one directory to another. Supports progress bars etc.
"""


import os.path
import shutil
from ..errorhook import ErrorMeta, errorWrap


class FileCopier(object, metaclass=ErrorMeta):

    """Handles copying files from orig directory to target. Does *not* copy patch files."""

    def __init__(self, indir, outdir, ignoredirs, ignoreexts, ignorefiles,
                 comsout, translator, mtimes, newmtimes, progresssig,
                 dirssig, *args, **kwargs):
        super(FileCopier, self).__init__(*args, **kwargs)
        self.indir = indir
        self.outdir = outdir
        versioningDirs = ['.svn', 'cvs', '.git', '.hg', '.bzr']
        self.ignoredirs = [os.path.normcase(x) for x in ignoredirs]
        self.ignoredirs += versioningDirs
        self.ignoreexts = [os.path.normcase(x) for x in ignoreexts]
        self.ignorefiles = [os.path.normcase(x) for x in ignorefiles]
        self.dirs = []
        self.files = []
        self.comsout = comsout
        self.translator = translator  # For future compatibility
        self.mtimes = mtimes
        self.newmtimes = newmtimes
        self.progresssig = progresssig
        self.dirssig = dirssig

    def doCopyDirs(self):
        print("Copying directory", self.dirs)

        for directory in self.dirs:
            self.comsout.send('displayMessage', "Copying directory "+directory)

            if os.path.exists(directory):
                if os.path.isfile(directory):
                    os.remove(directory)
            os.mkdir(directory)

    def run(self):
        self.getLists()
        if not os.path.exists(self.outdir):
            os.mkdir(self.outdir)
        # patchmarkerfn = os.path.join(self.outdir, 'rpgmktranslated')
        # if not os.path.exists(patchmarkerfn):
        #     with open(patchmarkerfn, 'w') as f:
        #         f.write(
        #             'RPGMaker Trans Patched Game. Not for redistribution.\n\n- Habisain')
        self.doCopyDirs()
        if self.dirssig:
            self.comsout.send('trigger', self.dirssig)
        if self.progresssig:
            self.comsout.send('setProgressDiv', self.progresssig,
                              len(self.files))
        for fid, infn, outfn in self.files:
            self.doCopyFile(fid, infn, outfn)
            if self.progresssig:
                self.comsout.send('incProgress', self.progresssig)

    # def doCopyFile(self, fid, infn, outfn):
    #     infnmtime = os.path.getmtime(infn)
    #     outfnmtime = self.mtimes.get(outfn, (None, None))[0]
    #     if infnmtime != outfnmtime:
    #         try:
    #             self.comsout.send('displayMessage', "Copying file "+str(infn))
    #             shutil.copy2(infn, outfn)
    #             self.newmtimes[outfn] = infnmtime
    #         except FileNotFoundError:
    #             self.comsout.send('nonfatalError',
    #                               'Could not copy %s to %s' % (infn, outfn))
    #     else:
    #         self.newmtimes[outfn] = infnmtime


    def doCopyFile(self, fid, infn, outfn):
        # Check if the file has one of the required extensions
        if infn.lower().endswith(('.rvdata2', '.rvdata', '.rxdata', '.ini')):
            infnmtime = os.path.getmtime(infn)
            outfnmtime = self.mtimes.get(outfn, (None, None))[0]
            if infnmtime != outfnmtime:
                try:
                    self.comsout.send('displayMessage', "Copying file "+str(infn))
                    shutil.copy2(infn, outfn)
                    self.newmtimes[outfn] = infnmtime
                except FileNotFoundError:
                    self.comsout.send('nonfatalError',
                                    'Could not copy %s to %s' % (infn, outfn))
            else:
                self.newmtimes[outfn] = infnmtime
        # else:
        #     self.comsout.send('displayMessage', "Skipping file "+str(infn)+" due to unsupported extension")


    def changeDir(self, path, partA, partB):
        if partA.endswith(os.sep):
            partA = partA.rstrip(os.sep)
        if partB.endswith(os.sep):
            partB = partB.rstrip(os.sep)
        if path.startswith(partA):
            path = path.replace(partA, partB, 1)
        else:
            raise Exception('Could not change directory of %s from %s to %s' %
                            (path, partA, partB))
        return path

    def getLists(self):
        indir, outdir = self.indir, self.outdir

        for path, subdirs, files in os.walk(indir):
            for rm in self.ignoredirs:
                if os.path.normcase(rm) in subdirs:
                    subdirs.remove(rm)

            for subdir in subdirs:
                dirname = os.path.join(path, subdir)
                transdirname = self.changeDir(dirname, indir, outdir)
                if not os.path.exists(transdirname):
                    self.dirs.append(transdirname)
            for fname in files:
                origfile = os.path.join(path, fname)
                fid = origfile.replace(indir + os.path.sep, '', 1)
                transfile = self.changeDir(origfile, indir, outdir)
                ext = os.path.splitext(fname)[1]
                if not (os.path.normcase(fid) in self.ignorefiles or os.path.normcase(ext) in self.ignoreexts):
                    self.files.append((fid, origfile, transfile))


@errorWrap
def copyfilesAndTrigger(indir, outdir, ignoredirs, ignoreexts, ignorefiles,
                        comsout, translator, mtimes, newmtimes, progresssig,
                        dirssig):
    copyfiles(indir, outdir, ignoredirs, ignoreexts, ignorefiles,
              comsout, translator, mtimes, newmtimes, progresssig, dirssig)
    comsout.send('trigger', 'fileCopyDone')


@errorWrap
def copyfiles(indir, outdir, ignoredirs, ignoreexts, ignorefiles, comsout,
              translator, mtimes, newmtimes, progresssig, dirssig):
    x = FileCopier(indir, outdir, ignoredirs, ignoreexts, ignorefiles,
                   comsout, translator, mtimes, newmtimes, progresssig,
                   dirssig)
    x.run()
