'''
scripttranslator
****************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Provides the functionality to translate scripts.
'''
from .parser import RubyParserState, RubyParserException

import pygments.lexers.ruby
import pygments.token

Token = pygments.token.Token


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


def translate_ruby(ruby):
    lexer = pygments.lexers.ruby.RubyLexer()
    tokens = iter(lexer.get_tokens_unprocessed(ruby))
    newline_count = 0
    current_string = []
    debug_strings = []
    output = []
    heredoc_mode = False
    heredoc_name = ''
    for index, token_type, token in tokens: # NOTE: Can manually advance by calling next(tokens)
        print(token_type, repr(token))
        if token_type in Token.Literal.String and token_type not in Token.Literal.String.Symbol:
            current_string = []
            while token_type in Token.Literal.String and token_type not in Token.Literal.String.Symbol:
                current_string.append(token)
                old_token_type = token_type
                index, token_type, token = next(tokens, (None, None, ''))
                if token_type in Token.Name.Constant and old_token_type in Token.Literal.String.Heredoc:
                    heredoc_mode = True
                    heredoc_name = token.strip()
                    index, token_type, token = next(tokens, (None, None, ''))
            actual_string = ''.join(current_string)
            if heredoc_mode:
                if actual_string:
                    # TODO: Translation of heredoc name... how? Or should I automate?
                    # TODO: Get the actual heredoc and it's indent size
                    actual_string = "%s: %s" % (heredoc_name, actual_string)
                else:
                    pass  # TODO: Possible change of Heredoc name? Would need different handling here.
                heredoc_mode = False
            if actual_string:
                debug_strings.append(actual_string)
        # TODO: Get Regexs
        newline_count += token.count('\n')

    return debug_strings


def translateRuby(string, filename, translationHandler, errorComs,
                  scriptTranslator=None, inline=False, verbose=False):
    """Translate a ruby string"""
    print(repr(string))
    print(translate_ruby(string))
    if scriptTranslator is None:
        scriptTranslator = ScriptTranslator(string, translationHandler,
                                            errorComs, inline=inline)
    state = RubyParserState(string, filename, scriptTranslator, 0, [],
                            verbose)
    state.parse()

    if translationHandler is False:
        return True
    output, debug_output = scriptTranslator.translate(debug_output=True)
    print(debug_output)
    return filename, output


def checkRuby(string):
    """Simply parse a ruby string, without doing any translator stuff to it."""
    try:
        return translateRuby(string, '', False, ScriptTranslator.dummy())
    except RubyParserException:
        return False
