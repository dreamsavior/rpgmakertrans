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


class RString:
    def __init__(self, context):
        self.lines = []
        self.context = context
        self.heredoc_mode = False
        self.__heredoc_id = None

    def append(self, item):
        if item:
            self.lines.append(item)

    @property
    def heredoc_id(self):
        if self.__heredoc_id is None:
            self.__heredoc_id = self.lines[-1]
        return self.__heredoc_id

    @heredoc_id.setter
    def heredoc_id(self, value):
        self.__heredoc_id = value

    @property
    def just_id(self):
        return len(self.lines) == 1

    @property
    def string(self):
        lines = self.lines[:]
        if self.heredoc_mode:
            lines.pop()
            if lines:
                indent = []
                for char in lines[0]:
                    if char.isspace():
                        indent.append(char)
                    else:
                        break
                indent = ''.join(indent)
                lines = [line.replace(indent, '', 1) for line in lines]
        return ''.join(lines)

    def __iter__(self):
        return iter(self.lines)

    def __repr__(self):
        return 'RString(%r, %r, %r)' % (self.context, ''.join(self.lines), self.heredoc_mode)

    def __str__(self):
        return ''.join(self.lines)


def translate_ruby(ruby, translator, inline, context_base):
    lexer = pygments.lexers.ruby.RubyLexer()
    tokens = iter(lexer.get_tokens_unprocessed(ruby))
    newline_count = 0
    debug_strings = []
    newline_pos = 0

    intermediate = []
    heredoc_ids = []
    heredoc_strings = []

    # TODO: Perhaps make Regex's only in verbose mode? Not sure.
    for index, token_type, token in tokens: # NOTE: Can manually advance by calling next(tokens)
        if token_type in Token.Literal.String and token_type not in Token.Literal.String.Symbol:
            line, col = newline_count, index - newline_pos
            context = 'Scripts/%s/%s:%s' % (context_base, line, col)
            current_string = RString(context)
            intermediate.append(current_string)
            while token_type in Token.Literal.String and token_type not in Token.Literal.String.Symbol:
                current_string.append(token)
                old_token_type = token_type
                index, token_type, token = next(tokens, (None, None, ''))
                if token_type in Token.Name.Constant and old_token_type in Token.Literal.String.Heredoc:
                    current_string.heredoc_mode = True
                    current_string.append(token)
                    index, token_type, token = next(tokens, (None, None, ''))
            if current_string.just_id():
                heredoc_ids.append(current_string)
            else:
                heredoc_strings.append(current_string)

        intermediate.append(token)
        if '\n' in token:
            newline_count += token.count('\n')
            newline_pos = index + token.rindex('\n')

    output = []
    for indx, part in enumerate(intermediate):
    #    print(indx, repr(part))
        if isinstance(part, RString):
            print('RRR', part.string)
            debug_strings.append(str(part))
            output.append(str(part))
        else:
            output.append(part)

    return ''.join(output), debug_strings


def translateRuby(string, filename, translationHandler, errorComs,
                  scriptTranslator=None, inline=False, verbose=False):
    """Translate a ruby string"""
    print(repr(string))
    print('---->NEW_TRANSLATOR')
    print(repr(translate_ruby(string, translationHandler, inline, filename)[0]))
    print('---->OLD_TRANSLATOR')
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
