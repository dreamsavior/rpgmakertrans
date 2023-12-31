'''
rubyparse_main
**************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2015
:license: GNU Public License version 3

A simple test runner for the ruby parser.
'''

import os
import sys
from .parser import RubyParserException
from .scripttranslator import translateRuby
from .customdelimiters import HereDocError
from ...controllers.sender import ErrorSender

class DummyTranslator:
    def translate(self, string, context):
        if DUMP:
            print('C::' + context)
            print('S::' + string)
        return string

dt = DummyTranslator()
VERBOSE = '-v' in sys.argv
DUMP = '-p' in sys.argv

if '-v' in sys.argv:
    sys.argv.remove('-v')
if '-p' in sys.argv:
    sys.argv.remove('-p')
    
def test(string, verbose = None, filename = '', succeeds = True, errout=ErrorSender()):
    assert isinstance(string, str)
    if DUMP: print('FULL STRING: %s' % string)
    if verbose is None:
        verbose = VERBOSE
    if verbose:
        print(string + ' ' +  str(succeeds))
    errored = False
    try:
        fn, outscript = translateRuby(string, filename = filename,
                                  translationHandler = dt, errorComs=errout, 
                                  verbose = verbose)
        assert outscript == string, 'Did not get same string back with no translations'
    except (RubyParserException, HereDocError):
        errored = True
        if succeeds is True:
            raise Exception()
    if succeeds is False and errored is False:
        raise Exception('Succeeded when should have failed')

heredoc = """
  Content.new(:value => <<-Eos
    Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor
    incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud
    exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute
    irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
    pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia
  Eos
)
"""
if len(sys.argv) == 1:
    #test('')
    test(heredoc, succeeds=False)
    #test('x = "abc%s" % "a"\n"Test 2"\n\'Another test\'\n\'Test4\' % \'Hi\'\n')
    #test('"%s" % @varName\n')
    #test('"%s, %s" % (@varName, otherName)\n')
    #test('/\//\n')
    #test(r'/[\\]/')
    #test('("Hello")')
    #test('# "Not Actually A String"\n')
    #test('( # Tricky one this)\n', succeeds = False)
    #test('print << "yo"')
    #test('print <<END\nHeredoc\nEND', succeeds = False)
    #test('print <<-END\nHeredoc\nEND', succeeds = False)
    #test('x /x')
    #test('x/x\nx /x')
    #test('%q[Hello2]')
    #test('"#{""}"')
    #test('"#{\'\'}"')
    #test('a/a "Hello"')
    #test('/./m()')
    #test('/\\[Vv]\[(\d+)\]/')
    #test('RPG::Cache.windowskin("Letter_"+($1.to_i/16).to_s).width / 4')
else:
    target = sys.argv[1]
    if os.path.isdir(target): fns = sorted([os.path.join(target, fn) for fn in os.listdir(target)])
    else: fns = [target]
    for filename in fns:
        if filename.endswith('.rb'):
            with open(filename, 'r', encoding='utf-8') as f:
                print(filename)
                script = f.read()
                test(script, filename = filename)