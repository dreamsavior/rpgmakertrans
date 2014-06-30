"""
basicpatcher
************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Basic Ruby patcher using pure CLI mode. Not fast, only for debug.

TODO: Update to use rbscripts directory
"""

import subprocess
from newtranslator import Translator
import sys
import os.path
import os
import tempfile

if len(sys.argv) != 4:
    raise Exception('Wrong number of arguments')

indata, outdata, transdir = sys.argv[1:]
tempdir = tempfile.mkdtemp()
print(tempdir)
translator = Translator()

if not os.path.exists(outdata):
    os.mkdir(outdata)
if not os.path.exists(transdir):
    os.mkdir(transdir)
if not os.path.exists(indata):
    raise Exception('Indata directory does not exist')

for x in os.listdir(transdir):
    if x.endswith('.txt'):
        fn = os.path.join(transdir, x)
        translator.loadFile(fn)

KEEP_TEMP = False
    
rbf = os.path.join(tempdir, 'translations.rbf')
translator.exportToRubyFragment(rbf)
contexts = []

for x in os.listdir(indata):
    context = x.partition('.')[0]
    contexts.append(context)
    infn = os.path.join(indata, x)
    outfn = os.path.join(outdata, x)
    pyf = os.path.join(tempdir, context + '.pyf')
    if os.name == 'posix':
        rubyexecutable = 'ruby1.8'
    else:
        rubyexecutable = 'ruby.exe'
    try:
        cmd = [rubyexecutable, 'cmdline.rb', infn, outfn, context, rbf, pyf]
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        print('Ruby failed')
        print('Command line')
        print(' '.join(['\'%s\'' % c for c in cmd]))
        sys.exit(1)
        
        
    translator.mergeFromFile(pyf)
    if not KEEP_TEMP:
        os.remove(pyf)
    #os.remove(pyf)
    
translator.patchFiles(contexts, transdir)
if not KEEP_TEMP:
    os.remove(rbf)
    os.rmdir(tempdir)