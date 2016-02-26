"""
rubyparse2
**********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2015
:license: GNU Public License version 3

The new version of the Ruby parser. Most of the parsing is done by
the Pygments library - the translate_ruby function handles working
out what needs to be translated, how it should be translated, and
does the translating.
"""
import pygments.lexers.ruby
import pygments.token
import random
import string

Token = pygments.token.Token


class RString:
    """Abstraction of a Ruby string. Handles Heredoc abstraction.
    Will eventually handle other things. Use append to add data
    to the string, then finalise it."""
    def __init__(self, context):
        """Initialise the RString.
        Args:
            context: Context of the RString"""
        self.lines = []
        self.context = context
        self.heredoc_mode = False
        self.__heredoc_id = None
        self.__heredoc_line_whitespace = ''
        self.__final = False
        self.__string = ''
        self.__just_id = None

    @property
    def string(self):
        """Get the raw string that can be fed to translator"""
        assert self.__final
        return self.__string

    @string.setter
    def string(self, value):
        """Set the raw string"""
        assert self.__final
        self.__string = value

    def finalise(self):
        """Finalise the RString"""
        self.__string = '\n'.join(line.rstrip() for line in self.lines)
        self.__final = True

    def append(self, item):
        """Append more data to the RString"""
        assert not self.__final
        if item:
            self.lines.append(item)

    @property
    def heredoc_id(self):
        """Get the Heredoc ID"""
        assert self.heredoc_mode
        return self.__heredoc_id

    @heredoc_id.setter
    def heredoc_id(self, value):
        """Set the Heredoc ID"""
        self.__heredoc_id = value

    @property
    def just_id(self):
        """Determine if something is just an ID or not"""
        if self.__just_id is None:
            self.__just_id = len(self.lines) == 1 and self.heredoc_mode
        return self.__just_id

    def infer_heredoc_id(self, unclaimed_heredoc_ids, heredoc_id_map):
        """Infer the Heredoc ID"""
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
            elif heredoc_id_line.strip() in unclaimed_heredoc_ids:
                self.__heredoc_id = heredoc_id_line.strip()
                self.__heredoc_line_whitespace = heredoc_id_line[:heredoc_id_line.index(self.__heredoc_id)]
            heredoc_id_map[self] = unclaimed_heredoc_ids.pop(self.__heredoc_id)

    def ruby_string(self):
        """Get the Ruby string for RString"""
        assert self.__final
        if not self.heredoc_mode:
            return self.__string
        elif self.just_id:
            return self.heredoc_id
        else:
            assert self.heredoc_id is not None
            return '%s\n%s%s\n' % (self.__string, self.__heredoc_line_whitespace, self.heredoc_id)


def translate_ruby(ruby, translator, inline, context_base):
    """Translate strings in Ruby
    Args:
        ruby: Ruby program
        translator: Translator object
        inline: If the script is inline or not
        context_base: Base of the context"""
    lexer = pygments.lexers.ruby.RubyLexer()
    tokens = iter(lexer.get_tokens_unprocessed(ruby))
    newline_count = 0
    newline_pos = 0

    intermediate = []
    heredoc_ids = []
    heredoc_strings = []
    unclaimed_heredoc_ids = {}
    heredoc_id_map = {}

    # TODO: Perhaps make Regex's only in verbose mode? Not sure.
    for index, token_type, token in tokens:  # NOTE: Can manually advance by calling next(tokens)
        if token_type in Token.Literal.String and token_type not in Token.Literal.String.Symbol:
            line, col = newline_count, index - newline_pos
            if inline:
                base = context_base if context_base.endswith('/') else context_base + '/'
                context = '%s%s:%s' % (base, line, col)
            else:
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
            if current_string.just_id:
                heredoc_ids.append(current_string)
                current_string.infer_heredoc_id(unclaimed_heredoc_ids, heredoc_id_map)
            else:
                heredoc_strings.append(current_string)
                current_string.infer_heredoc_id(unclaimed_heredoc_ids, heredoc_id_map)
            current_string.finalise()
            current_string.string = translator.translate(current_string.string, context)
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
    for index, part in enumerate(intermediate):
        if isinstance(part, RString):
            output_string = part.ruby_string()
            output.append(output_string)
        else:
            output.append(part)

    return ''.join(output)