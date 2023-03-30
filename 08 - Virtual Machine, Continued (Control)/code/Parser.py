"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """
    # Parser
    
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.

    ## VM Language Specification

    A .vm file is a stream of characters. If the file represents a
    valid program, it can be translated into a stream of valid assembly 
    commands. VM commands may be separated by an arbitrary number of whitespace
    characters and comments, which are ignored. Comments begin with "//" and
    last until the line’s end.
    The different parts of each VM command may also be separated by an arbitrary
    number of non-newline whitespace characters.

    - Arithmetic commands:
      - add, sub, and, or, eq, gt, lt
      - neg, not, shiftleft, shiftright
    - Memory segment manipulation:
      - push <segment> <number>
      - pop <segment that is not constant> <number>
      - <segment> can be any of: argument, local, static, constant, this, that, 
                                 pointer, temp
    - Branching (only relevant for project 8):
      - label <label-name>
      - if-goto <label-name>
      - goto <label-name>
      - <label-name> can be any combination of non-whitespace characters.
    - Functions (only relevant for project 8):
      - call <function-name> <n-args>
      - function <function-name> <n-vars>
      - return
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        self.input_lines = input_file.read().splitlines()
        self.len_command_lines = len(self.input_lines)

        self.cur_command = ""
        self.cur_index = 0

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self.cur_index < self.len_command_lines

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """

        if self.has_more_commands():
            self.cur_command = self.input_lines[self.cur_index]
            self.cur_index += 1
            while self.has_more_commands():
                if (len(self.cur_command) == 0 or (self.cur_command[0] == "/" and self.cur_command[1] == "/")):
                    self.cur_command = self.input_lines[self.cur_index]
                else:
                    break
                self.cur_index += 1
            for i in range(len(self.cur_command) - 1):
                if self.cur_command[i] == "/" and self.cur_command[i + 1] == "/":
                    self.cur_command = self.cur_command[:i]
                    break
            self.cur_command = self.cur_command.split()


    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        cur_command = self.cur_command
        if cur_command[0] in {"add", "sub", "neg", "not", "eq", "gt", "lt", "and", "or", "shiftright", "shiftleft"}:
            return "C_ARITHMETIC"
        elif cur_command[0] == "push":
            return "C_PUSH"
        elif cur_command[0] == "pop":
            return "C_POP"
        elif cur_command[0] == "label":
            return "C_LABEL"
        elif cur_command[0] == "goto":
            return "C_GOTO"
        elif cur_command[0] == "if-goto":
            return "C_IF"
        elif cur_command[0] == "call":
            return "C_CALL"
        elif cur_command[0] == "function":
            return "C_FUNCTION"
        elif cur_command[0] == "return":
            return "C_RETURN"

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        if self.command_type() == "C_ARITHMETIC":
            return self.cur_command[0]
        return self.cur_command[1]


    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        return int(self.cur_command[2])