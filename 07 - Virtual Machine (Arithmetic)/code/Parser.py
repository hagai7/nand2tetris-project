"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient
    access to their components.
    In addition, it removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        # A good place to start is:
        # input_lines = input_file.read().splitlines()
        self.input_lines = input_file.read().splitlines()
        self.num_of_commands = len(self.input_lines)
        self.index_next_commands = 0
        self.current_command = None
        self.arith_dict = {"add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not", "shiftleft", "shiftright"}

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        # Your code goes here!
        return self.index_next_commands < self.num_of_commands

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        # Your code goes here!
        if self.has_more_commands():
            self.current_command = self.input_lines[self.index_next_commands]
            self.index_next_commands += 1
            while (self.current_command.startswith("//") or self.current_command == "") and self.has_more_commands():
                self.current_command = self.input_lines[self.index_next_commands]
                self.index_next_commands += 1
            if "//" in self.current_command:
                self.current_command = self.current_command.split("//")[0]
            self.current_command = self.current_command.split()

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        # Your code goes here!
        if self.current_command[0] == "push":
            return "C_PUSH"
        elif self.current_command[0] == "pop":
            return "C_POP"
        elif self.current_command[0] == "label":
            return "C_LABEL"
        elif self.current_command[0] == "goto":
            return "C_GOTO"
        elif self.current_command[0] == "if-goto":
            return "C_IF"
        elif self.current_command[0] == "function":
            return "C_FUNCTION"
        elif self.current_command[0] == "call":
            return "C_CALL"
        elif self.current_command[0] == "return":
            return "C_RETURN"
        elif self.current_command[0] in self.arith_dict:
            return "C_ARITHMETIC"

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned.
            Should not be called if the current command is "C_RETURN".
        """
        if self.command_type() == "C_ARITHMETIC":
            return self.current_command[0]
        else:
            return self.current_command[1]

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP",
            "C_FUNCTION" or "C_CALL".
        """
        return int(self.current_command[2])
