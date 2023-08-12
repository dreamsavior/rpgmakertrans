'''
scripttranslator
****************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Provides the functionality to translate scripts.
'''
from .parser import RubyParserState, RubyParserException

class ScriptTranslator:
    def __init__(self, string, translationHandler, errorComs, inline=False):
        self.string = string
        self.output = None
        self.inline = inline
        self.errorComs = errorComs
        self.translationIndices = []
        self.translationHandler = translationHandler

    @classmethod
    def dummy(cls):
        if not hasattr(cls, '__dummy'):
            cls.__dummy = ('', None)
        return cls.__dummy

    def addIndicies(self, indicies):
        self.translationIndices.append(indicies)

    def rollback(self, index):
        self.translationIndices = [indices for indices in self.translationIndices if indices[0] < index]

    def translate(self, debug_output=False):
        lastIndex = 0
        output = []
        debug = []
        for indices in self.translationIndices:
            if not self.inline:
                context = 'Scripts/%s/%s:%s' % (indices.file, indices.line, indices.char)
            else:
                base = indices.file if indices.file.endswith('/') else indices.file + '/'
                context = '%s%s:%s' % (base, indices.line, indices.char)
            output.append(self.string[lastIndex:indices[0]])
            original = self.string[indices[0]:indices[1]]
            debug.append(original)
            translation = self.translationHandler.translate(original, context)
            if checkRuby(translation):
                output.append(translation)
            else:
                self.errorComs.send('nonfatalError', 'Could not parse the following script translation: %s->%s' % (
                original, translation))
                output.append(self.string[indices[0]:indices[1]])
            lastIndex = indices[1]
        output.append(self.string[lastIndex:])
        if debug_output:
            return ''.join(output), debug
        else:
            return ''.join(output)


def translateRuby(string, filename, translationHandler, errorComs,
                  scriptTranslator=None, inline=False, verbose=False):
    """Translate a ruby string"""
    if scriptTranslator is None:
        scriptTranslator = ScriptTranslator(string, translationHandler,
                                            errorComs, inline=inline)
    state = RubyParserState(string, filename, scriptTranslator, 0, [],
                            verbose)
    state.parse()

    if translationHandler is False:
        return True
    output, debug_output = scriptTranslator.translate(debug_output=True)
    return filename, output


def checkRuby(string):
    """Simply parse a ruby string, without doing any translator stuff to it."""
    try:
        return translateRuby(string, '', False, ScriptTranslator.dummy())
    except RubyParserException:
        return False
