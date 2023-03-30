// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.



@i
M=0
@max
M=0

@16384
D=A
@min
M=D
@max
M=M-D


(LOOP)
    //if i==length go to swap
    @i
    D=M
    @R15
    D=D-M
    @SWAP
    D;JEQ
    //if arr[i] < min update min
    @R14
    D=M
    @i
    A=D+M
    D=M
    @min
    D=D-M
    @MIN_UPDATE
    D;JLT


(MORE_LOOP)
    //if arr[i] > max update max
    @R14
    D=M
    @i
    A=D+M
    D=M
    @max
    D=D-M
    @MAX_UPDATE
    D;JGT
    //i++
    @i
    M=M+1
    @LOOP
    0;JMP

(MIN_UPDATE)
    @R14
    D=M
    @i
    A=D+M
    D=M
    @min
    M=D
    @MORE_LOOP
    0;JMP

(MAX_UPDATE)
    @R14
    D=M
    @i
    A=D+M
    D=M
    @max
    M=D
    @LOOP
    0;JMP

(SWAP)
    //temp=min
    @min
    D=M
    @temp
    M=D
    //min=max
    @max
    D=M
    @min
    M=D
    //max=temp
    @temp
    D=M
    @max
    M=D
    @LOOP
    0;JMP


    

