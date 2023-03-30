"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""

from SymbolTable import SymbolTable
from VMWriter import VMWriter

OP_DICT = {"+": "add", "-": "sub", "=": "eq", "*": "call Math.multiply 2", "/": "call Math.divide 2",
           "&gt;": "gt", "&lt;": "lt", "&amp;": "and", "|": "or"}

SEG_DICT = {"FIELD": "this", "ARG": "argument", "VAR": "local", "STATIC": "static"}


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
        self.tokenizer = input_stream
        self.vm_writer = VMWriter(output_stream)
        self.table = SymbolTable()
        self.class_name, self.subroutine_name, self.return_type, self.subroutine_type, self.let_type \
            = "", "", "", "", ""
        self.term_args, self.num_if, self.num_while, self.term_args, self.do_args = 0, 0, 0, 0, 0
        self.cur_compile = ""

    def general_compile(self, type):
        self.tokenizer.advance()
        return type

    def sub_routine_compile(self, type):
        self.subroutine_type = type
        if self.subroutine_type == "method":
            self.table.define("this", self.class_name, "ARG")
        self.general_compile(self.tokenizer.keyword())
        if self.tokenizer.cur_tok == "void":
            self.return_type = "void"
        self.tokenizer.advance()
        self.subroutine_name = self.general_compile(self.tokenizer.identifier())
        self.compile_symbol(self.compile_parameter_list)

    def compile_condition(self):
        for i in range(2):
            self.tokenizer.advance()
        self.compile_expression()
        self.tokenizer.advance()


    def compile_symbol(self, middle_op):
        self.general_compile(self.tokenizer.symbol())
        middle_op()
        self.general_compile(self.tokenizer.symbol())

    def term_symbol(self):
        if self.tokenizer.cur_tok in {'-', '~', '^', '#'}:
            operation = self.general_compile(self.tokenizer.symbol())
            self.compile_term()
            if operation == "~":
                operation = "not"
            elif operation == "-":
                operation = "neg"
            self.vm_writer.write_arithmetic(operation)
        else:
            self.general_compile(self.tokenizer.symbol())

    def term_indentifier(self):
        next_tok = ""
        if self.tokenizer.next_word < len(self.tokenizer.tokens):
            next_tok = self.tokenizer.tokens[self.tokenizer.next_word]
        if next_tok == "[":
            indetifier = self.general_compile(self.tokenizer.identifier())
            self.compile_symbol(self.compile_expression)
            self.vm_writer.write_push(SEG_DICT[self.table.kind_of(indetifier)], self.table.index_of(indetifier))
            self.vm_writer.write_arithmetic("add")
            self.vm_writer.write_pop("pointer", 1)
            self.vm_writer.write_push("that", 0)

        elif next_tok == "(" or next_tok == ".":
            self.term_args = 0
            identifier = self.general_compile(self.tokenizer.identifier())
            if self.tokenizer.cur_tok == ".":
                self.general_compile(self.tokenizer.symbol())
                if self.table.kind_of(identifier):
                    self.term_args += 1
                    index = self.table.index_of(identifier)
                    kind = self.table.kind_of(identifier)
                    self.vm_writer.write_push(SEG_DICT[kind], index)
                    identifier = self.table.type_of(identifier)
                identifier += "." + self.general_compile(self.tokenizer.identifier())
            else:
                self.term_args += 1
                identifier = self.class_name + "." + identifier
                self.vm_writer.write_push("pointer", 0)
            self.cur_compile = "term"
            self.compile_symbol(self.compile_expression_list)
            self.vm_writer.write_call(identifier, self.term_args)
        else:
            identifier = self.general_compile(self.tokenizer.identifier())
            i = self.table.index_of(identifier)
            if self.table.kind_of(identifier) == "VAR":
                self.vm_writer.write_push("local", i)
            elif self.table.kind_of(identifier) == "STATIC":
                self.vm_writer.write_push("static", i)
            elif self.table.kind_of(identifier) == "ARG":
                self.vm_writer.write_push("argument", i)
            elif self.table.kind_of(identifier) == "FIELD":
                self.vm_writer.write_push("this", i)
            return identifier

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.tokenizer.advance()
        self.class_name = self.tokenizer.cur_tok
        for i in range(2):
            self.tokenizer.advance()
        self.compile_class_var_dec()
        while self.tokenizer.cur_tok in {"method", "function", "constructor"}:
            self.compile_subroutine()
        self.general_compile(self.tokenizer.symbol())

    def compile_class_var_dec(self) -> None:
        while self.tokenizer.cur_tok == "field" or self.tokenizer.cur_tok == "static":
            """Compiles a static declaration or a field declaration."""
            cur_kind = self.tokenizer.cur_tok.upper()
            self.tokenizer.advance()

            if self.tokenizer.token_type() == "KEYWORD":
                cur_type = self.tokenizer.cur_tok.upper()
            else:
                cur_type = self.tokenizer.cur_tok
            self.tokenizer.advance()
            cur_tok = self.tokenizer.cur_tok
            self.tokenizer.advance()
            self.table.define(cur_tok, cur_type, cur_kind)
            while self.tokenizer.cur_tok != ";":
                self.tokenizer.advance()
                cur_tok = self.tokenizer.cur_tok
                self.tokenizer.advance()
                self.table.define(cur_tok, cur_type, cur_kind)
            self.tokenizer.advance()

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self.table.start_subroutine()
        self.num_if = 0
        self.num_while = 0
        self.sub_routine_compile(self.tokenizer.cur_tok)
        self.tokenizer.advance()
        while self.tokenizer.cur_tok == "var":
            self.compile_var_dec()
        subroutine_name = self.class_name + "." + self.subroutine_name
        self.vm_writer.write_function(subroutine_name, self.table.var_count("VAR"))
        if self.subroutine_type == "constructor":
            self.subroutine_type = ""
            self.vm_writer.write_push("constant", self.table.var_count("FIELD"))
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop("pointer", 0)
        if self.subroutine_type == "method":
            self.subroutine_type = ""
            self.vm_writer.write_push("argument", 0)
            self.vm_writer.write_pop("pointer", 0)
        self.compile_statements()
        self.tokenizer.advance()

    def compile_parameter_list(self):
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        while self.tokenizer.cur_tok != ")":
            type = self.tokenizer.cur_tok
            self.tokenizer.advance()
            name = self.tokenizer.cur_tok
            self.tokenizer.advance()
            self.table.define(name, type, "ARG")
            if self.tokenizer.cur_tok == ",":
                self.general_compile(self.tokenizer.symbol())


    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        cur_tok = self.tokenizer.cur_tok
        self.tokenizer.advance()
        if self.tokenizer.token_type() == "KEYWORD":
            cur_type = self.general_compile(self.tokenizer.keyword())

        else:
            cur_type = self.general_compile(self.tokenizer.identifier())
        cur_name = self.general_compile(self.tokenizer.identifier())
        self.table.define(cur_name, cur_type, cur_tok.upper())
        while self.tokenizer.cur_tok != ";":
            self.tokenizer.advance()
            cur_name = self.tokenizer.cur_tok
            self.tokenizer.advance()
            self.table.define(cur_name, cur_tok, cur_tok.upper())
        self.general_compile(self.tokenizer.symbol())

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        """
        while self.tokenizer.cur_tok in {"let", "do", "if", "while", "return"}:
            if self.tokenizer.keyword() == "let":
                self.compile_let()
            elif self.tokenizer.keyword() == "if":
                self.compile_if()
            elif self.tokenizer.keyword() == "while":
                self.compile_while()
            elif self.tokenizer.keyword() == "do":
                self.compile_do()
            elif self.tokenizer.keyword() == "return":
                self.compile_return()

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.general_compile(self.tokenizer.keyword())
        function_name = self.general_compile(self.tokenizer.identifier())
        self.do_args = 0
        if self.tokenizer.cur_tok == ".":
            self.general_compile(self.tokenizer.symbol())
            if self.table.kind_of(function_name):
                self.do_args += 1
                index = self.table.index_of(function_name)
                kind = self.table.kind_of(function_name)
                self.vm_writer.write_push(SEG_DICT[kind], index)
                function_name = self.table.type_of(function_name)
            function_name += "." + self.general_compile(self.tokenizer.identifier())
        else:
            self.do_args += 1
            function_name = self.class_name + "." + function_name
            self.vm_writer.write_push("pointer", 0)
        self.general_compile(self.tokenizer.symbol())
        self.cur_compile = "do"
        self.compile_expression_list()
        self.general_compile(self.tokenizer.symbol())
        self.vm_writer.write_call(function_name, self.do_args)
        self.vm_writer.write_pop("temp", 0)
        self.general_compile(self.tokenizer.symbol())

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.tokenizer.advance()
        cur_tok = self.tokenizer.cur_tok
        self.tokenizer.advance()

        if self.tokenizer.cur_tok == "[":
            self.let_type = "array"
            self.tokenizer.advance()
            self.compile_expression()
            self.tokenizer.advance()
            self.vm_writer.write_push(SEG_DICT[self.table.kind_of(cur_tok)], self.table.index_of(cur_tok))
            self.vm_writer.write_arithmetic("add")
        self.tokenizer.advance()
        self.compile_expression()
        self.tokenizer.advance()
        if self.let_type == "array":
            self.let_type = ""
            self.vm_writer.write_pop("temp", 0)
            self.vm_writer.write_pop("pointer", 1)
            self.vm_writer.write_push("temp", 0)
            self.vm_writer.write_pop("that", 0)
        else:
            self.vm_writer.write_pop(SEG_DICT[self.table.kind_of(cur_tok)], self.table.index_of(cur_tok))

    def compile_while(self) -> None:
        """Compiles a while statement."""
        index = str(self.num_while)
        self.num_while += 1
        self.vm_writer.write_label("WHILE_EXP" + index)
        self.compile_condition()
        self.vm_writer.write_arithmetic("not")
        self.vm_writer.write_if("WHILE_END" + index)
        self.compile_symbol(self.compile_statements)
        self.vm_writer.write_goto("WHILE_EXP" + index)
        self.vm_writer.write_label("WHILE_END" + index)


    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.tokenizer.advance()
        if self.tokenizer.cur_tok != ';':
            self.compile_expression()
        self.tokenizer.advance()
        if self.return_type == "void":
            self.vm_writer.write_push("constant", 0)
            self.return_type = ""
        self.vm_writer.write_return()

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        index = str(self.num_if)
        self.num_if += 1
        self.compile_condition()
        self.vm_writer.write_if("IF_TRUE" + index)
        self.vm_writer.write_goto("IF_FALSE" + index)
        self.vm_writer.write_label("IF_TRUE" + index)
        self.tokenizer.advance()
        self.compile_statements()
        self.tokenizer.advance()
        if self.tokenizer.cur_tok == "else":
            self.vm_writer.write_goto("IF_END" + index)
            self.vm_writer.write_label("IF_FALSE" + index)
            self.tokenizer.advance()
            self.compile_symbol(self.compile_statements)
            self.vm_writer.write_label("IF_END" + index)
        else:
            self.vm_writer.write_label("IF_FALSE" + index)

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.compile_term()
        if self.tokenizer.cur_tok in {'+', '-', '*', '/', '&', '|', '<', '>', '=', '~', '^', '#'}:
            operator = self.general_compile(self.tokenizer.symbol())
            self.compile_expression()
            self.vm_writer.write_arithmetic(OP_DICT[operator])

    def term_keyword(self):
        keyword = self.general_compile(self.tokenizer.keyword())
        if keyword == "true":
            self.vm_writer.write_push("constant", 0)
            self.vm_writer.write_arithmetic("not")
        elif keyword == "false" or keyword == "null":
            self.vm_writer.write_push("constant", 0)
        elif keyword == "this":
            self.vm_writer.write_push("pointer", 0)

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
        if self.tokenizer.token_type() == "KEYWORD":
            self.term_keyword()
        elif self.tokenizer.token_type() == "INT_CONST":
            constant = self.general_compile(int(self.tokenizer.int_val()))
            self.vm_writer.write_push("constant", constant)
        elif self.tokenizer.token_type() == "STRING_CONST":
            string_val = self.general_compile(self.tokenizer.string_val())
            self.vm_writer.write_push("constant", len(string_val))
            self.vm_writer.write_call("String.new", 1)
            for i in range(len(string_val)):
                self.vm_writer.write_push("constant", ord(string_val[i]))
                self.vm_writer.write_call("String.appendChar", 2)
        elif self.tokenizer.cur_tok == "(":
            self.compile_symbol(self.compile_expression)
        elif self.tokenizer.token_type() == "SYMBOL":
            self.term_symbol()
        elif self.tokenizer.token_type() == "IDENTIFIER":
            self.term_indentifier()

    def compile_expression_list(self):
        """Compiles a (possibly empty) comma-separated list of expressions."""
        while self.tokenizer.cur_tok != ")":
            if self.cur_compile == "term":
                self.term_args += 1
            elif self.cur_compile == "do":
                self.do_args += 1
            self.compile_expression()
            if self.tokenizer.cur_tok == ",":
                self.general_compile(self.tokenizer.symbol())
