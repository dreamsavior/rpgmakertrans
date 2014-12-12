'''
rubyparse_main
**************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

A simple test runner for the ruby parser.
'''

import os
import sys
from .parser import translateRuby, RubyParserException
from .customdelimiters import HereDocError

class DummyTranslator:
    def translate(self, string, context):
        if '-p' in sys.argv:
            print('C::' + context)
            print('S::' + string)
        return string
 
dt = DummyTranslator()

def test(string, verbose = None, filename = '', succeeds = True):
    if verbose is None:
        verbose = '-v' in sys.argv
    if verbose:
        print(string + ' ' +  str(succeeds))
    errored = False
    try:
        outscript = translateRuby(string, dt, filename = filename, verbose = verbose)
        assert outscript == string, 'Did not get same string back with no translations'
    except (RubyParserException, HereDocError):
        errored = True
        if succeeds is True:
            raise Exception()
    if succeeds is False and errored is False:
        raise Exception('Succeeded when should have failed')

test('')       
test('x = "abc%s" % "a"\n"Test 2"\n\'Another test\'\n\'Test4\' % \'Hi\'\n')
test('"%s" % @varName\n')
test('"%s, %s" % (@varName, otherName)\n')
test('/\//\n')
test('("Hello")')
test('# "Not Actually A String"\n')
test('( # Tricky one this)\n', succeeds = False)
test('print << "yo"')
test('print <<END\nHeredoc\nEND', succeeds = False)
test('print <<-END\nHeredoc\nEND', succeeds = False)
test('x /x')
test('x/x\nx /x')
test('%q[Hello2]')
test('"#{""}"')
test('"#{\'\'}"')
test('a/a "Hello"')
#for filename in os.listdir('testdata'):
#    if filename.endswith('.rb'):
#        with open(os.path.join('testdata', filename), 'r', encoding='utf-8') as f:
#            print(filename)
#            test(f.read(), filename = filename)