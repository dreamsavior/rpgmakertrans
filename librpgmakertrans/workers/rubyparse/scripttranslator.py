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
import random
import string

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
    def __init__(self, context, heredoc_indent_mode):
        self.lines = []
        self.context = context
        self.heredoc_mode = False
        self.__heredoc_id = None
        self.heredoc_indent_mode = heredoc_indent_mode
        self.__heredoc_line_whitespace = ''
        self.__final = False
        self.__string = ''
        self.__just_id = None

    @property
    def string(self):
        assert self.__final
        return self.__string

    @string.setter
    def string(self, value):
        assert self.__final
        self.__string = value

    def finalise(self):
        self.__string = '\n'.join(line.rstrip() for line in self.lines)
        self.__final = True

    def append(self, item):
        assert not self.__final
        if item:
            self.lines.append(item)

    @property
    def heredoc_id(self):
        assert self.heredoc_mode
        return self.__heredoc_id

    @heredoc_id.setter
    def heredoc_id(self, value):
        self.__heredoc_id = value

    @property
    def just_id(self):
        if self.__just_id is None:
            self.__just_id = len(self.lines) == 1 and self.heredoc_mode
        return self.__just_id

    def infer_heredoc_id(self, unclaimed_heredoc_ids, heredoc_id_map):
        assert self.heredoc_mode
        assert self.__heredoc_id is None
        assert not self.__final
        if self.just_id:
            self.__heredoc_id = self.lines.pop()
            unclaimed_heredoc_ids[self.heredoc_id] = self
        else:
            heredoc_id_line = self.lines.pop()
            if heredoc_id_line.rstrip() in unclaimed_heredoc_ids:
                self.__heredoc_id = heredoc_id_line.rstrip()
            elif heredoc_id_line.strip() in unclaimed_heredoc_ids and self.heredoc_indent_mode:
                self.__heredoc_id = heredoc_id_line.strip()
                self.__heredoc_line_whitespace = heredoc_id_line[:heredoc_id_line.index(self.__heredoc_id)]
            heredoc_id_map[self] = unclaimed_heredoc_ids.pop(self.__heredoc_id)

    def ruby_string(self):
        assert self.__final
        if not self.heredoc_mode:
            return self.__string
        elif self.just_id:
            return self.heredoc_id
        else:
            assert self.heredoc_id is not None
            return '%s\n%s%s\n' % (self.__string, self.__heredoc_line_whitespace, self.heredoc_id)

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
    heredoc_indent_mode = False
    unclaimed_heredoc_ids = {}
    heredoc_id_map = {}

    # TODO: Perhaps make Regex's only in verbose mode? Not sure.
    for index, token_type, token in tokens: # NOTE: Can manually advance by calling next(tokens)
        if token_type in Token.Literal.String and token_type not in Token.Literal.String.Symbol:
            line, col = newline_count, index - newline_pos
            context = 'Scripts/%s/%s:%s' % (context_base, line, col)
            current_string = RString(context, heredoc_indent_mode)
            intermediate.append(current_string)
            while token_type in Token.Literal.String and token_type not in Token.Literal.String.Symbol:
                current_string.append(token)
                old_token_type = token_type
                index, token_type, token = next(tokens, (None, None, ''))
                if token_type in Token.Name.Constant and old_token_type in Token.Literal.String.Heredoc:
                    current_string.heredoc_mode = True
                    current_string.append(token)
                    index, token_type, token = next(tokens, (None, None, ''))
            if current_string.just_id:
                heredoc_ids.append(current_string)
                current_string.infer_heredoc_id(unclaimed_heredoc_ids, heredoc_id_map)
            else:
                heredoc_strings.append(current_string)
                current_string.infer_heredoc_id(unclaimed_heredoc_ids, heredoc_id_map)
            current_string.finalise()
            current_string.string = translator.translate(current_string.string, context)
        elif token == '<<-':
            heredoc_indent_mode = True
        else:
            heredoc_indent_mode = False
        intermediate.append(token)
        if '\n' in token:
            newline_count += token.count('\n')
            newline_pos = index + token.rindex('\n')

    for heredoc, heredoc_id in heredoc_id_map.items():
        if heredoc.heredoc_id in heredoc.string:
            length = 4
            new_id = ''.join(random.choice(string.ascii_lowercase) for _ in range(length))
            while new_id in heredoc.string:
                length += 1
                new_id = ''.join(random.choice(string.ascii_lowercase) for _ in range(length))
            heredoc_id.heredoc_id = new_id
            heredoc.heredoc_id = new_id

    output = []
    for indx, part in enumerate(intermediate):
    #    print(indx, repr(part))
        if isinstance(part, RString):
            output_string = part.ruby_string()
            debug_strings.append(output_string)
            output.append(output_string)
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
