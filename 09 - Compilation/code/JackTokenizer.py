"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.

    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters,
    and comments, which are ignored. There are three possible comment formats:
    /* comment until closing */ , /** API comment until closing */ , and
    // comment until the line’s end.

    - ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’).
    - xxx: regular typeface is used for names of language constructs
           (‘non-terminals’).
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' |
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' |
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' |
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate
    file. A compilation unit is a single class. A class is a sequence of tokens
    structured according to the following context free syntax:

    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type)
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement |
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{'
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions

    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName |
            varName '['expression']' | subroutineCall | '(' expression ')' |
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className |
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'

    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        self.input = input_stream.read().splitlines()
        self.token_lines = []
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

    def parse_comment(self, line, is_comment, is_next_line_comment):
        new_ind1 = line.find("//")
        new_ind2 = line.find("*/")
        new_ind3 = line.find("/*")
        if new_ind1 != -1:
            line = line[:new_ind1]
        elif new_ind2 != -1 and is_next_line_comment == True:
            line = line[new_ind2 + 2:]
            is_next_line_comment = False
        elif new_ind3 != -1:
            if new_ind2 == -1:
                line = line[:new_ind3]
                is_next_line_comment = True
                is_comment = False
                if line != "":
                    self.token_lines.append(line)
            else:
                line = line[:new_ind3] + line[new_ind2 + 2:]
        else:
            is_comment = False
            line = line.strip()
        return line, is_comment, is_next_line_comment

    def parse_lines(self):
        is_next_line_comment = False
        for line in self.input:
            is_comment = True
            while is_comment:
                line, is_comment, is_next_line_comment = self.parse_comment(line, is_comment, is_next_line_comment)
            if line != "" and is_next_line_comment == False:
                self.token_lines.append(line)

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
