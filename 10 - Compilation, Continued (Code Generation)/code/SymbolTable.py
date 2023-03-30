"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""

class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        self.dict_class = dict()
        self.dict_subroutine = dict()
        self.counter = {"FIELD": 0, "STATIC": 0, "ARG": 0, "VAR": 0}
        # self.field_counter = 0
        # self.static_counter = 0
        # self.arg_counter = 0
        # self.var_counter = 0

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        self.dict_subroutine.clear()
        self.counter["ARG"] = 0
        self.counter["VAR"] = 0

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        if kind in {"STATIC", "VAR", "FIELD", "ARG"}:
            self.dict_class[name] = (kind, type, self.counter[kind])
            self.counter[kind] += 1

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        if kind in {"STATIC", "VAR", "FIELD", "ARG"}:
            return self.counter[kind]

    def general_(self, name, ind):
        if name in self.dict_class:
            return self.dict_class[name][ind]
        elif name in self.dict_subroutine:
            return self.dict_subroutine[name][ind]

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        # if name in self.dict_class:
        #     return self.dict_class[name][0]
        # elif name in self.dict_subroutine:
        #     return self.dict_subroutine[name][0]
        return self.general_(name, 0)

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        # if name in self.dict_class:
        #     return self.dict_class[name][1]
        # elif name in self.dict_subroutine:
        #     return self.dict_subroutine[name][1]
        return self.general_(name, 1)

    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        # if name in self.dict_class:
        #     return self.dict_class[name][2]
        # elif name in self.dict_subroutine:
        #     return self.dict_subroutine[name][2]
        return self.general_(name, 2)

