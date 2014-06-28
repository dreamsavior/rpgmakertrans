"""
parser
******

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Implementation of the Ruby Parser.
"""


class RubyParser:

    def __init__(self):
        self.string = None
        self.index = None
        self.matchers = []
        self.escapeRules = []

    def parse(self, string):
        self.string = string
        self.index = 0
        while self.index < len(self.string):

            self.index += 1
        self.string = None
        self.index = None
