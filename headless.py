from patchers import getPatcher
from filecopier2 import copyfiles
import multiprocessing
from sender import SenderManager

from twokpatcher import TwoKGame

def patch(indir, patchpath, outdir):
    x = SenderManager()
    x.start()
    dummycoms = x.Sender()
    patcher = getPatcher(patchpath)
    translator = patcher.makeTranslator()
    dontcopy = patcher.getNonPatchedList()
    fileCopyPool = multiprocessing.Pool()
    r = fileCopyPool.apply_async(copyfiles, kwds={'indir': indir, 'outdir': outdir,
              'ignoredirs': [], 'ignoreexts':['.lmu', '.ldb', '.lsd'], 'ignorefiles': dontcopy, 
              'comsout': dummycoms, 'translator': translator, 'mtimes': {}, 'newmtimes': {}})
    fileCopyPool.close()
    fileCopyPool.join()
    r.get()
    game = TwoKGame(indir, outdir, translator, mtimes = {}, newmtimes = {}, comsout=dummycoms)
    game.run()
    patcher.writeTranslator(translator, path=patchpath + '_2')
    
    

if __name__ == '__main__':
    indir = '/home/habisain/tr/cr'
    patchpath = '/home/habisain/tr/cr_p'
    outdir = '/home/habisain/tr/cr_t'
    patch(indir, patchpath, outdir)
    
     