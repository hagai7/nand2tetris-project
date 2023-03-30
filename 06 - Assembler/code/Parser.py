"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

def clean_line(line):
    line = line.replace(' ', '')
    for i in range(len(line)-1):
        if line[i] == '/' and line[i+1] == '/':
            line = line[:i]
            break
    return line.strip()


class Parser:
    """Encapsulates access to the input code. Reads an assembly program
    by reading each command line-by-line, parses the current command,
    and provides convenient access to the commands components (fields
    and symbols). In addition, removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        # A good place to start is to read all the lines of the input:
        # input_lines = input_file.read().splitlines()
        self.input_lines = input_file.read().splitlines()
        self.command_lines = []
        for line in self.input_lines:
            if len(line) != 0 and (line[0] != '/' and line[1] != '/'):
                line = clean_line(line)
                self.command_lines.append(line)
        self.cur_index = 0
        self.len_command_lines = len(self.command_lines)

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self.cur_index < self.len_command_lines

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        self.cur_index += 1

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        first_elem = self.command_lines[self.cur_index][0]
        if first_elem == '@':
            return 'A_COMMAND'
        if first_elem == '(':
            return 'L_COMMAND'
        return 'C_COMMAND'

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        first_elem = self.command_lines[self.cur_index][0]
        if first_elem == '(':
            return self.command_lines[self.cur_index][1:-1]
        return self.command_lines[self.cur_index][1:]

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        cur_command = self.command_lines[self.cur_index]
        for i in range(len(cur_command)):
            if cur_command[i] == '=':
                return cur_command[:i]

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        equal_index = 0
        comma_index = 0
        cur_command = self.command_lines[self.cur_index]
        for i in range(len(cur_command)):
            if cur_command[i] == '=':
                equal_index = i
            if cur_command[i] == ';':
                comma_index = i
        if equal_index and comma_index:
            return cur_command[equal_index + 1:comma_index]
        if equal_index:
            return cur_command[equal_index + 1:]
        return cur_command[:comma_index]

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        cur_command = self.command_lines[self.cur_index]
        for i in range(len(cur_command)):
            if cur_command[i] == ';':
                return cur_command[i+1:]

