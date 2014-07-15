"""
persistpatcher
**************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Interface using the persistant Ruby process based patcher. 

TODO: Check to see that everything still works using RVM etc.
"""

import subprocess
from .newtranslator import Translator
import sys
import os.path
import os
import tempfile
import time

class VXRubyPatcher(object):
    def __init__(self):
        if os.name == 'posix':
            homedir = os.path.expanduser('~')
            rubyexecutable = os.path.join(homedir, '.rvm', 'rubies', 'ruby-1.8.7-p374', 'bin', 'ruby')
            cmd = [rubyexecutable, os.path.join('rbscripts', 'persist.rb')]
        elif os.name == 'nt':
            if os.path.isfile('tvx.exe'):
                cmd = ['tvx.exe']
            else:
                cmd = ['ruby.exe', 'persist.rb']
        else:
            print('Unknown Operating System - exiting')
            sys.exit(0)
            
        self.ruby = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.active = True
        
    def __del__(self):
        if self.active:
            self.command(['QUIT'])
            
    def command(self, commands, dbg=False):
        if dbg:
            print('send ' + ' '.join(commands))
        for command in commands:
            self.ruby.stdin.write('%s\n' % command)
            self.ruby.stdin.flush()
        if commands[0] != 'QUIT':
            while self.ruby.stdout.readline().strip() != 'Ready':
                time.sleep(0.1)
        else:
            self.active = False
    
if __name__ == '__main__':
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
    ruby = VXRubyPatcher()
    for x in os.listdir(transdir):
        if x.endswith('.txt'):
            fn = os.path.join(transdir, x)
            translator.loadFile(fn)
    
    KEEP_TEMP = False
        
    rbf = os.path.join(tempdir, 'translations.rbf')
    translator.exportToRubyFragment(rbf)
    translator.exportToRubyFragment('translations.rbf')
    ruby.command(['IMPORT', rbf])
    contexts = []
    
    for x in sorted(os.listdir(indata)):
        context = x.partition('.')[0]
        contexts.append(context)
        infn = os.path.join(indata, x)
        outfn = os.path.join(outdata, x)
        ruby.command(['PATCH', infn, outfn, context])

    pyf = os.path.join(tempdir, 'translations.pyf')
    ruby.command(['EXPORT', pyf])
    translator.mergeFromFile(pyf)
    ruby.command(['QUIT'])
    sys.exit()
        
    translator.patchFiles(contexts, transdir)
    if not KEEP_TEMP:
        os.remove(rbf)
        os.rmdir(tempdir)