'''
rubyparse_main
**************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

A simple test runner for the experimental ruby parser.
'''

from .parser import RubyParser

class DummyTranslator:
    def translate(self, string):
        print(string)
        
#RubyParser('x = "abc%s" % "a"\n"Test 2"\n\'Another test\'\n\'Test4\' % \'Hi\'\n', DummyTranslator())
#RubyParser('"%s" % @varName\n', DummyTranslator())
#'RubyParser('"%s, %s" % (@varName, otherName)\n', DummyTranslator())
RubyParser('/\//\n', DummyTranslator())