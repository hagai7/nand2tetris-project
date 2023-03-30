import typing


class JackTokenizer:
    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        self.input = input_stream.read().splitlines()
        self.token_lines = []
        self.is_comment, self.is_next_line_comment = True, False
        self.parse_lines()
        self.next_line, self.next_word = 0, 0
        self.sentence, self.cur_tok = "", ""
        self.tokens = []

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        return self.next_word < len(self.tokens) or self.next_line < len(self.token_lines)

    def parse_sentence(self, first, last):
        if self.sentence[first] != "\"":
            while last < len(self.sentence) and self.sentence[last] not in {' ', '\n', '\t'} \
                    and self.sentence[last] \
                    not in {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+',
                            '-', '*', '/', '&', '|', '<', '>', '=', '~', '^', '#'}:
                last += 1
            if first != last:
                self.tokens.append(self.sentence[first:last])
            if self.sentence[last] not in {' ', '\n', '\t'}:
                self.tokens.append(self.sentence[last])
        else:
            last += 1
            while self.sentence[last] != "\"":
                last += 1
            self.tokens.append(self.sentence[first:last + 1])
        last += 1
        return last, last

    def update_comment_state(self):
        self.is_next_line_comment = True
        self.is_comment = False

    def middle_comment_start_line(self, input_line, first_ind, last_ind):
        input_line = input_line[:input_line.index("/*")]
        if "*/" in input_line[:first_ind]:
            second_ind = input_line.index("*/") + 2
            input_line += input_line[second_ind:]
        elif "*/" in input_line[last_ind + 1:]:
            second_ind = input_line.index("*/") + 2 + input_line.index("/*")
            input_line += input_line[second_ind:]
        elif "*/" not in input_line[first_ind:last_ind]:
            self.update_comment_state()

            if input_line.replace(" ", "") != "":
                self.token_lines.append(input_line)
        return input_line


    def middle_comment_end_line(self, input_line, last_ind):
        comment_first = input_line[last_ind + 1:].index("/*") + last_ind + 1
        if "*/" not in input_line[comment_first:]:
            input_line = input_line[:comment_first]
            self.update_comment_state()
            if input_line.replace(" ", "") != "":
                self.token_lines.append(input_line)
        else:
            second_ind = comment_first + input_line[last_ind + 1:].index("*/") + 2
            input_line = input_line[:comment_first] + input_line[second_ind:]
        return input_line

    def end_comment_end_line(self, input_line):
        if "*/" in input_line:
            second_ind = input_line.index("*/") + 2
            input_line = input_line[:input_line.index("/*")] + input_line[second_ind:]
        else:
            input_line = input_line[:input_line.index("/*")]
            self.update_comment_state()
            if input_line and not input_line.isspace():
                self.token_lines.append(input_line)
        return input_line

    def parse_comment(self, input_line, first_ind, last_ind, middle_comment):
        if middle_comment and "//" in input_line[:first_ind]:
            input_line = input_line[:input_line.index("//")]
        elif middle_comment and "//" in input_line[last_ind + 1:]:
            input_line = input_line[:input_line.index("//")]
        elif not middle_comment and "//" in input_line:
            input_line = input_line[:input_line.index("//")]
        elif self.is_next_line_comment and "*/" in input_line and \
                "*/" not in input_line[first_ind:last_ind]:
            input_line = input_line[input_line.index("*/") + 2:]
            self.is_next_line_comment = False
        elif middle_comment and "/*" in input_line[:first_ind]:
            input_line = self.middle_comment_start_line(input_line, first_ind, last_ind)
        elif middle_comment and "/*" in input_line[last_ind + 1:]:
            input_line = self.middle_comment_end_line(input_line, last_ind)
        elif not middle_comment and "/*" in input_line:
            input_line = self.end_comment_end_line(input_line)
        else:
            self.is_comment = False
            input_line = input_line.strip()
        return input_line

    def parse_lines(self):
        i = 0
        while i < len(self.input):
            first_ind, last_ind, self.is_comment = 0, 0, True
            middle_comment = False
            if "\"" in self.input[i]:
                first_ind = self.input[i].index("\"")
                if "\"" in self.input[i][first_ind + 1:]:
                    last_ind = self.input[i][first_ind + 1:].index("\"") + first_ind + 1
                    middle_comment = True
            while self.is_comment:
                self.input[i] = self.parse_comment(self.input[i], first_ind, last_ind, middle_comment)
            if self.input[i].replace(" ", "") != "" and not self.is_next_line_comment:
                self.token_lines.append(self.input[i])
            i += 1

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token.
        This method should be called if has_more_tokens() is true.
        Initially there is no current token.
        """
        if self.has_more_tokens():
            if self.next_word >= len(self.tokens) or not self.cur_tok:
                if self.next_word >= len(self.tokens):
                    self.sentence = self.token_lines[self.next_line]
                    self.next_line += 1
                    self.next_word = 0
                self.tokens = []
                first, last = 0, 0
                while last < len(self.sentence):
                    last, first = self.parse_sentence(first, last)
            self.cur_tok = self.tokens[self.next_word]
            self.next_word += 1

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        if self.cur_tok in {'class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char',
                            'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while',
                            'return'}:
            return "KEYWORD"
        elif self.cur_tok in {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+',
                              '-', '*', '/', '&', '|', '<', '>', '=', '~', '^', '#'}:
            return "SYMBOL"
        elif self.cur_tok[0].isdigit():
            return "INT_CONST"
        elif self.cur_tok[0] == '"':
            return "STRING_CONST"
        else:
            return "IDENTIFIER"

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT",
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO",
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        if self.token_type() == "KEYWORD":
            return self.cur_tok

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' |
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        if self.token_type() == "SYMBOL":
            if self.cur_tok == ">":
                return "&gt;"
            elif self.cur_tok == "<":
                return "&lt;"
            elif self.cur_tok == '"':
                return "&quot;"
            elif self.cur_tok == "&":
                return "&amp;"
            return self.cur_tok

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        if self.token_type() == "IDENTIFIER":
            return self.cur_tok

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        if self.token_type() == "INT_CONST":
            return int(self.cur_tok)

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including
                      double quote or newline '"'
        """
        if self.token_type() == "STRING_CONST":
            return self.cur_tok[1:len(self.cur_tok) - 1]
