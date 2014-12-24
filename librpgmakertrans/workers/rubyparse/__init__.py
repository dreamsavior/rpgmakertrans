"""
rubyparse
*********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

The Ruby parser. This is written in Python because Ruby1.8 lacks
string encoding awareness. As Ruby scripts can have 1 of 4 encodings, this
creates substantial problems for parsing Ruby in Ruby.
"""
 
from .parser import translateRuby
from .server import rbTranslationServer