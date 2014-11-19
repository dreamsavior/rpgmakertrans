'''
rubyparse_main
**************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

A simple test runner for the experimental ruby parser.
'''

from .parser import parseRuby, RubyParserException
from .customdelimiters import HereDocError

class DummyTranslator:
    def translate(self, string):
        pass#print('S::' + string)
 
dt = DummyTranslator()

def test(string, verbose = False, succeeds = True):
    if verbose:
        print(string + ' ' +  str(succeeds))
    errored = False
    try:
        parseRuby(string, dt, verbose = verbose)
    except (RubyParserException, HereDocError):
        errored = True
        if succeeds is True:
            raise Exception()
    if succeeds is False and errored is False:
        raise Exception('Succeeded when should have failed')
        
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