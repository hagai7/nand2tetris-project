"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.output_stream = output_stream
        self.input_stream = input_stream
        self.shifting = 0

    def general_write(self, token):
        to_write = "<" + token + ">\n"
        self.output_stream.write(to_write)

    def start_compile(self, type_str):
        for i in range(self.shifting):
            self.output_stream.write("  ")
        self.shifting += 1
        self.general_write(type_str)

    def end_compile(self, type_str):
        self.shifting -= 1
        for i in range(self.shifting):
            self.output_stream.write("  ")
        self.general_write("/" + type_str)

    def general_compile(self):
        for i in range(self.shifting):
            self.output_stream.write("  ")
        current = self.input_stream.cur_tok
        token_type = self.input_stream.token_type().lower()
        if token_type == "int_const":
            token_type = "integerConstant"
        if token_type == "string_const":
            token_type = "stringConstant"
            current = current[1:-1]
        if token_type == "symbol":
            current = self.input_stream.symbol()
        self.output_stream.write("<" + token_type + "> " + current + " </" + token_type + ">\n")
        self.input_stream.advance()

    def compile_conditions(self):
        self.general_compile()
        self.general_compile()
        self.compile_expression()
        self.general_compile()
        self.general_compile()
        self.compile_statements()
        self.general_compile()

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.general_write("class")
        self.shifting += 1
        for i in range(3):
            self.general_compile()
        self.compile_class_var_dec()
        self.compile_subroutine()
        self.general_compile()
        self.shifting -= 1
        self.general_write("/class")

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        while self.input_stream.tokens[-1] == ";":
            self.start_compile("classVarDec")
            while self.input_stream.token_type() in ["KEYWORD", "IDENTIFIER"]:
                self.general_compile()
            while self.input_stream.cur_tok != ";":
                self.general_compile()
                self.general_compile()
            self.general_compile()
            self.end_compile("classVarDec")

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        while self.input_stream.cur_tok != "}":
            self.start_compile("subroutineDec")
            for i in range(4):
                self.general_compile()
            self.compile_parameter_list()
            self.general_compile()
            self.start_compile("subroutineBody")
            self.general_compile()
            while self.input_stream.cur_tok == "var":
                self.compile_var_dec()
            self.compile_statements()
            self.general_compile()
            self.end_compile("subroutineBody")
            self.end_compile("subroutineDec")

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        self.start_compile("parameterList")
        while self.input_stream.cur_tok != ")":
            self.general_compile()
        self.end_compile("parameterList")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.start_compile("varDec")
        for i in range(3):
            self.general_compile()
        while self.input_stream.cur_tok != ";":
            self.general_compile()
            self.general_compile()
        self.general_compile()
        self.end_compile("varDec")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        """
        self.start_compile("statements")
        while self.input_stream.cur_tok in {"do", "let", "while", "return", "if"}:
            if self.input_stream.keyword() == "do":
                self.compile_do()
            elif self.input_stream.keyword() == "let":
                self.compile_let()
            elif self.input_stream.keyword() == "while":
                self.compile_while()
            elif self.input_stream.keyword() == "return":
                self.compile_return()
            elif self.input_stream.keyword() == "if":
                self.compile_if()
        self.end_compile("statements")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.start_compile("doStatement")
        self.general_compile()
        self.general_compile()
        if self.input_stream.cur_tok == ".":
            self.general_compile()
            self.general_compile()
        self.general_compile()
        self.compile_expression_list()
        self.general_compile()
        self.general_compile()
        self.end_compile("doStatement")

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.start_compile("letStatement")
        self.general_compile()
        self.general_compile()
        if self.input_stream.cur_tok == "[":
            self.general_compile()
            self.compile_expression()
            self.general_compile()
        self.general_compile()
        self.compile_expression()
        self.general_compile()
        self.end_compile("letStatement")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.start_compile("whileStatement")
        self.compile_conditions()
        self.end_compile("whileStatement")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.start_compile("returnStatement")
        self.general_compile()
        if self.input_stream.cur_tok != ';':
            self.compile_expression()
        self.general_compile()
        self.end_compile("returnStatement")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.start_compile("ifStatement")
        self.compile_conditions()
        if self.input_stream.cur_tok == "else":
            self.general_compile()
            self.general_compile()
            self.compile_statements()
            self.general_compile()
        self.end_compile("ifStatement")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.start_compile("expression")
        self.compile_term()
        while self.input_stream.cur_tok in {'+', '-', '*', '/', '&', '|', '<', '>', '=', '~', '^', '#'}:
            self.general_compile()
            self.compile_term()
        self.end_compile("expression")

    def compile_term(self) -> None:
        """Compiles a term.
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        self.start_compile("term")
        if self.input_stream.token_type() == "KEYWORD" or self.input_stream.token_type() == "INT_CONST"\
                or self.input_stream.token_type() == "STRING_CONST":
            self.general_compile()
        elif self.input_stream.cur_tok == "(":
            self.general_compile()
            self.compile_expression()
            self.general_compile()
        elif self.input_stream.token_type() == "SYMBOL":
            if self.input_stream.cur_tok in {'-', '~', '^', '#'}:
                self.general_compile()
                self.compile_term()
            else:
                self.general_compile()
        elif self.input_stream.token_type() == "IDENTIFIER":
            next_symbol = ""
            if self.input_stream.next_word < len(self.input_stream.tokens):
                next_symbol = self.input_stream.tokens[self.input_stream.next_word]
            if next_symbol == "[":
                self.general_compile()
                self.general_compile()
                self.compile_expression()
                self.general_compile()
            elif next_symbol == "(" or next_symbol == ".":
                self.general_compile()
                if self.input_stream.cur_tok == ".":
                    self.general_compile()
                    self.general_compile()
                self.general_compile()
                self.compile_expression_list()
                self.general_compile()
            else:
                self.general_compile()
        self.end_compile("term")

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.start_compile("expressionList")
        while self.input_stream.cur_tok != ")":
            self.compile_expression()
            if self.input_stream.cur_tok == ",":
                self.general_compile()
        self.end_compile("expressionList")
