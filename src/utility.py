#! usr/bin/env python3
import os
import re
from typing import Dict, List, Tuple


class ScriptParser:
    """ Basic scripting language parser.
    """

    HEADER = re.compile(r"\[(\s*\S+(?:\s+\S+)*\s*)]")
    PARAMS = re.compile(r"<(\s*\S+(?:\s+\S+)*\s*)>")

    @classmethod
    def parse(cls, filename: str) -> Dict[int, Tuple[Tuple[str], Tuple[str]]]:
        """ Reads a text file and returns a dictionary representing its (formatted) contents.
            This merely turns it into a dictionary. It's up to whoever's calling the parser
            to interpret what the dictionary elements actually mean.
        """
        output: Dict[int, Tuple[Tuple[str], Tuple[str]]] = {}
        with open(filename, "r") as f:
            s_contents: str = " ".join(f.readlines())
            l_statements: List[str] = s_contents.split("!")
            for i_num, s_statement in enumerate(l_statements):
                t_header: Tuple[str] = tuple()
                t_params: Tuple[str] = tuple()
                r_header = ScriptParser.HEADER.search(s_statement)
                if r_header:
                    s_header: str = r_header.group(1)
                    t_header = tuple(s_header.split())
                r_params = ScriptParser.PARAMS.search(s_statement)
                if r_params:
                    s_params: str = r_params.group(1)
                    t_params = tuple(s_params.split())
                if t_header:
                    output[i_num] = (t_header, t_params)
        return output


class Utility:
    """ Various utility methods.
    """

    @staticmethod
    def cwd(filename: str) -> str:
        """ Returns the parent directory of some file.
        """
        return os.path.dirname(os.path.abspath(filename))

    @staticmethod
    def abspath(current: str, target: str) -> str:
        """ Returns the absolute path of a file that's expected to be in the current directory.
        """
        return os.path.join(Utility.cwd(current), target)

    @staticmethod
    def stob(s: str) -> bool:
        """ Converts a string value to a boolean. Very simple.
        """
        return "t" in s.lower()

    @staticmethod
    def null() -> float:
        """ Forces reflexive non-equivalence.
        """
        return float('nan')

    @staticmethod
    def dict_keys_in_order(adict: dict) -> list:
        """ Returns a list of dictionary keys in ascending order.
        """
        return sorted(list(adict.keys()))

    @staticmethod
    def add_to_dict(adict: dict, key, value):
        """ Adds an item to a list of values under the given key.
        """
        try:
            adict[key].append(value)
        except KeyError:
            adict[key] = [value]

    @staticmethod
    def print_list(l_items: list):
        """ Prints a list of items one line at a time.
        """
        for x in l_items:
            print(x)
