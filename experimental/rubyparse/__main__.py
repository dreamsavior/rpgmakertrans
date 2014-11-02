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
 
dt = DummyTranslator()       
#RubyParser('x = "abc%s" % "a"\n"Test 2"\n\'Another test\'\n\'Test4\' % \'Hi\'\n', dt
#RubyParser('"%s" % @varName\n', dt
#RubyParser('"%s, %s" % (@varName, otherName)\n', dt # Problem - something isn't matching correctly.
#RubyParser('/\//\n', dt
RubyParser('("Hello")', dt)