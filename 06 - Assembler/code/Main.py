"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code


def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    # A good place to start is to initialize a new Parser object:
    # parser = Parser(input_file)
    # Note that you can write to output_file like so:
    # output_file.write("Hello world! \n")

    rom_address = 0
    parser = Parser(input_file)
    symbol_table = SymbolTable()
    code = Code()
    #first pass
    while parser.has_more_commands():
        if parser.command_type() == 'L_COMMAND':
            symbol_table.add_entry(parser.symbol(), rom_address)
        else:
            rom_address += 1
        parser.advance()

    #second pass
    parser.cur_index = 0
    ram_address = 16
    while parser.has_more_commands():
        if parser.command_type() == 'A_COMMAND':
            if parser.symbol().isnumeric():
                binary = '{0:016b}'.format(int(parser.symbol()))
            elif symbol_table.contains(parser.symbol()):
                binary = '{0:016b}'.format(symbol_table.get_address(parser.symbol()))
                # ram_address += 1
            else:
                symbol_table.add_entry(parser.symbol(), ram_address)
                binary = '{0:016b}'.format(ram_address)
                ram_address += 1
            output_file.write(binary+'\n')
        elif parser.command_type() == 'C_COMMAND':
            comp = code.comp(parser.comp())
            dest = code.dest(parser.dest())
            jump = code.jump(parser.jump())
            if '<<' in parser.command_lines[parser.cur_index] or '>>' in parser.command_lines[parser.cur_index]:
                output_file.write('101'+comp+dest+jump+'\n')
            else:
                output_file.write('111'+comp+dest+jump+'\n')
        parser.advance()


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
