"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

ADD = "add"
SUB = "sub"
NOT = "not"
NEG = "neg"
AND = "and"
OR = "or"
S_RIGHT = "shiftright"
S_LEFT = "shiftleft"
EQ = "eq"
GT = "gt"
LT = "lt"
CONST = "constant"
STATIC = "static"
LCL = "local"
ARG = "argument"
THIS = "this"
THAT = "that"
POINT = "pointer"
TEMP = "temp"

POS_LCL = 1
POS_ARG = 2
POS_THIS = 3
POS_THAT = 4
POS_TEMP = 5

C_PUSH = "C_PUSH"
C_POP = "C_POP"


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.output_file = output_stream
        self.count = 0
        self.name = ""
        self.start = False

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        # This function is useful when translating code that handles the
        # static segment. For example, in order to prevent collisions between two
        # .vm files which push/pop to the static segment, one can use the current
        # file's name in the assembly variable's name and thus differentiate between
        # static variables belonging to different files.
        # To avoid problems with Linux/Windows/MacOS differences with regards
        # to filenames and paths, you are advised to parse the filename in
        # the function "translate_file" in Main.py using python's os library,
        # For example, using code similar to:
        # input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))

        self.name = filename
        self.start = True

    def wrapper_arithmetic(self):
        return "@SP" + "\n" + "M=M-1\n" + "A=M\n" + "D=M\n" + \
             "@SP\n" + "M=M-1\n" + "A=M\n"

    def add_sub(self, type):
        return self.wrapper_arithmetic() + "M=M"+type+"D\n" + "@SP\n" + "M=M+1\n"

    def neg_not(self, type):
        return "@SP\n" + "M=M-1\n" + "A=M\n" + "M="+type+"M\n" \
                + "@SP\n" + "M=M+1\n"

    def and_or(self, type):
        return self.wrapper_arithmetic() + "M=M" + type + "D\n" + "@SP\n" + "M=M+1\n"

    def shift(self, type):
        return "@SP\n" + "A=M-1\n" + "M=M" + type + "\n"

    def comp(self, command):
        if command == EQ:
            command = "JEQ"
        elif command == GT:
            command = "JGT"
        elif command == LT:
            command = "JLT"
        label1 = "LABEL_" + str(self.count) + self.name
        label2 = "LABEL_" + str(self.count + 1) + self.name
        self.count += 2
        return "@" + "SP" + "\n" + "M=M-1\n"+ "A=M\n" + "D" + "=M\n" \
                  + "@" + "SP" + "\n" + "M=M-1\n" +"A=M\n" \
                  + "A" + "=M\n" + "D=A-D\n" + "@" + label1 + "\n" \
                  + "D;" + command + "\n" + "@" + "SP" + "\n" \
                  + "A=M\n" + "M=0\n" + "@" + label2 + "\n" + "0;JMP\n" \
                  + "(" + label1 + ")\n" + "@" + "SP" + "\n" + "A=M" + "\n" \
                  + "M=-1" + "\n" + "(" + label2 + ")" + "\n" +\
                  "@" + "SP" + "\n" + 'M=M+1\n'


    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        assembly_command = ""
        if command == ADD:
            assembly_command = self.add_sub("+")
        if command == SUB:
            assembly_command = self.add_sub("-")
        if command == NEG:
            assembly_command = self.neg_not("-")
        if command == NOT:
            assembly_command = self.neg_not("!")
        if command == OR:
            assembly_command = self.and_or("|")
        if command == AND:
            assembly_command = self.and_or("&")
        if command == S_RIGHT:
            assembly_command = self.shift(">>")
        if command == S_LEFT:
            assembly_command = self.shift("<<")
        if command == EQ :
            assembly_command = self.comp(command)
        if command == LT :
            assembly_command = self.comp(command)
        if command == GT:
            assembly_command = self.comp(command)
        self.output_file.write(assembly_command)

    def wrapper_push(self):
        return "@" + "SP\n" + "A=M\n" + "M=D\n" + "@" + "SP\n" + "M=M+1\n"

    def push_seg(self, segment, index):
        assembly_segment = ""
        if segment == LCL:
            assembly_segment = POS_LCL
        if segment == ARG:
            assembly_segment = POS_ARG
        if segment == THIS:
            assembly_segment = POS_THIS
        if segment == THAT:
            assembly_segment = POS_THAT
        return "@" + str(index) + "\n" + "D=A\n" + "@" + str(assembly_segment) + "\n" + "A=M+D\n" + "D=M\n"


    def point_temp(self, segment, index):
        assembly_segment = 0
        if segment == POINT:
            assembly_segment = POS_THIS
        if segment == TEMP:
            assembly_segment = POS_TEMP
        return "@" + str(index) + "\n" + "D=A\n" + "@" + str(assembly_segment) + "\n" + "A=A+D\n" + "D=M\n"


    def push(self, segment, index):
        if segment == CONST:
            return "@" + str(index) + "\n" + "D=A\n" + self.wrapper_push()
        if segment == STATIC:
            return "@" + self.name + "." + str(index) + "\n" + "D=M\n" + self.wrapper_push()
        if segment in {THIS, THAT, ARG, LCL}:
            return self.push_seg(segment, index) + self.wrapper_push()
        if segment in {POINT, TEMP}:
            return self.point_temp(segment, index) + self.wrapper_push()


    def pop_seg(self, segment, index, am):
        assembly_segment = ""
        if segment == LCL:
            assembly_segment = POS_LCL
        if segment == ARG:
            assembly_segment = POS_ARG
        if segment == POINT or segment == THIS:
            assembly_segment = POS_THIS
        if segment == THAT:
            assembly_segment = POS_THAT
        if segment == TEMP:
            assembly_segment = POS_TEMP
        return "@" + str(index) + "\n" + "D=A\n" + "@" + str(assembly_segment) + "\n" + \
                am + "D=A+D\n" + "@R13\n" + "M=D\n" + "@SP" + "\n" + \
               "M=M-1\n" + "A=M\n" + "D=M\n" + "@R13\n" + "A=M\n" + "M=D\n"


    def pop(self, segment, index):
        if segment == STATIC:
            return "@SP" + "\n" + "M=M-1\n" + "A=M\n" + "D=M\n" \
                   + "@" + self.name + "." + str(index) + '\n' + "M=D\n"
        if segment in {THIS, THAT, ARG, LCL}:
            return self.pop_seg(segment, index, "A=M\n")
        if segment in {POINT, TEMP}:
            return self.pop_seg(segment, index, "")

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        assembly_command = ""
        if command == C_PUSH:
            assembly_command = self.push(segment, index)
        if command == C_POP:
            assembly_command = self.pop(segment, index)
        self.output_file.write(assembly_command)


    def write_init(self):
        command = "@256\nD=A\n@SP\nM=D\n"
        self.output_file.write(command)
        self.write_call("Sys.init", 0)

    def write_label(self, label: str) -> None:
        command = "(" + label + ")\n"
        self.output_file.write(command)

    def write_go_to(self, label: str) -> None:
        command = "@"+label+"\n0;JMP\n"
        self.output_file.write(command)

    def write_if(self, label: str) -> None:
        command = "@SP\nM=M-1\nA=M\nD=M\n@"+label+"\nD;JNE\n"
        self.output_file.write(command)

    def write_function(self, function_name: str, n_vars: int) -> None:
        self.write_label(function_name)
        for i in range(n_vars):
            self.write_push_pop(C_PUSH, CONST, 0)

    def write_call(self, function_name: str, n_args: int) -> None:
        str_count = str(self.count)
        self.output_file.write("@" + function_name + "$ret" + str_count +
                               "\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
                               "@LCL\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
                               "@ARG\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
                               "@THIS\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
                               "@THAT\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
                               "@" + str(5+n_args) + "\nD=A\n@SP\nD=M-D\n@ARG\nM=D\n@SP\nD=M\n@LCL\nM=D\n")
        self.write_go_to(function_name)
        self.write_label(function_name + "$ret" + str_count)
        self.count += 1

    def write_return(self) -> None:
        str_count = str(self.count)
        self.output_file.write("@LCL\nD=M\n@FRAME" + str_count + "\nM=D\n" + "@5\nD=A\n@FRAME" +
                               str_count + "\nA=M-D\nD=M\n@RET"+ str_count + "\nM=D\n"
                               "@SP\nA=M\nA=A-1\nD=M\n@ARG\nA=M\nM=D\n@SP\nM=M-1\n"
                               "@ARG\nD=M+1\n@SP\nM=D\n@FRAME" + str_count + "\nA=M-1\nD=M\n@THAT\nM=D\n"
                               "@2\nD=A\n@FRAME" + str_count + "\nA=M-D\nD=M\n@THIS\nM=D\n"
                               "@3\nD=A\n@FRAME" + str_count + "\nA=M-D\nD=M\n@ARG\nM=D\n"
                               "@4\nD=A\n@FRAME" + str_count + "\nA=M-D\nD=M\n@LCL\nM=D\n"
                               "@RET" + str_count + "\nA=M\n0;JMP\n")
        self.count += 1






