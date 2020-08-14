import sys
from os import path
import re
import logging

from typing import Optional, List


def search_file_for_term(filename: str, search_term: str):
    if not path.isfile(filename):
        raise FileNotFoundError(filename)
    found_results = False
    with open(filename, "r") as a_file:
        ds = DependencyStack()
        for line in a_file:
            ds.prune_trim_and_push(line)
            peek = ds.peek()
            if peek and search_term in peek:
                found_results = True
                print(ds)
    if not found_results:
        print("No results found.")


class DependencyStack:
    dep_line_pattern = re.compile(
        r"""
        ^                               # Start of (cleaned-up) string
        ([-+ |\\]+ )?                   # Indentation characters, optional
        (\()?                           # Parenthesis around duplicate, optional
        ([a-z0-9._-]+):                 # Group (ex: us.catalist.fusion)
        ([a-zA-Z0-9._-]+):              # Name (ex: fusion)
        ([a-z]+):                       # Artifact type (pom or jar)
        ([0-9a-zA-Z._-]+)               # Version (ex: 6.12.1-SNAPSHOT)
        (:(compile|test|provided))?     # Scope, optional (ex: compile or test)
        ( - omitted for duplicate\))?   # Duplicate dependency note, optional
        """, re.VERBOSE)
    indent_pattern = re.compile(r"\+- |\\- | {3}|\| {2}")
    info_prefix = "[INFO] "

    @staticmethod
    def is_valid_dependency_line(dependency_line: str) -> bool:
        return DependencyStack.dep_line_pattern.match(
            DependencyStack._cleanup_line(dependency_line)) is not None

    @staticmethod
    def _cleanup_line(dependency_line: str) -> str:
        if dependency_line.startswith(DependencyStack.info_prefix):
            return dependency_line[len(DependencyStack.info_prefix):].rstrip()
        else:
            return dependency_line.rstrip()

    @staticmethod
    def _calc_level(dependency_line: str) -> int:
        line_match = DependencyStack.dep_line_pattern.match(dependency_line)
        if line_match:
            if line_match.group(1):
                indent_matches = DependencyStack.indent_pattern.findall(
                    line_match.group(1))
                return len(indent_matches)
            else:
                return 0
        else:
            return -1

    def __init__(self):
        self._stack: List[str] = list()

    def prune_trim_and_push(self, log_line: str):
        cleaned_line = DependencyStack._cleanup_line(log_line)
        if not DependencyStack.is_valid_dependency_line(log_line):
            if cleaned_line.startswith("-----"):
                logging.debug("Reached end of module in Maven project")
                while self._stack:
                    self._stack.pop()
            if self._stack:
                logging.warning("Invalid dependency line: %s", cleaned_line)
            return
        this_level = DependencyStack._calc_level(cleaned_line)
        if this_level < 0:
            return
        while self._get_level() >= this_level:
            toss = self.pop()
            logging.debug("Toss: L%d %s", DependencyStack._calc_level(toss),
                          toss)
        self._stack.append(cleaned_line)
        logging.debug("Push: L%d %s", self._get_level(), cleaned_line)

    def pop(self) -> str:
        ret_val = self._stack.pop()
        logging.debug("Pop : L%d %s", DependencyStack._calc_level(ret_val),
                      ret_val)
        return ret_val

    def peek(self) -> Optional[str]:
        if self._stack:
            logging.debug("Peek: L%d %s", self._get_level(), self._stack[-1])
            return self._stack[-1]
        else:
            return None

    def _get_level(self):
        if self._stack:
            return DependencyStack._calc_level(self._stack[-1])
        else:
            return -1

    def __str__(self):
        ret_val = ""
        for item in self._stack:
            ret_val += item + '\n'
        return ret_val


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) != 3 or sys.argv[1] in ["--help", "-h"]:
        print(f"Usage: python3 {sys.argv[0]} <maven_output_text_file.txt> "
              f"<search_term>")
        sys.exit(1)

    filename_arg = sys.argv[1]
    search_term_arg = sys.argv[2]
    print(f"File  : {filename_arg}")
    print(f"Search: {search_term_arg}")
    print()
    search_file_for_term(filename_arg, search_term_arg)
