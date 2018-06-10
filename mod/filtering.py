#!/usr/bin/env python3
"""Filtering module using regex"""
from typing import (Pattern, Iterable, Set, Match)
import logging
import os
import re
import sre_constants


from .stdfunc import exc_msg


LOGGER = logging.getLogger(__name__)


class MatchFilter():
    """Regex matching class.
    """
    def __init__(self, words: Iterable[str]) -> None:
        # If word is str, make it into list.
        if isinstance(words, str):
            words = [words]
        self.__regexset = gen_reg_set(words)

    def is_match(self, text: str) -> bool:
        """If text contains regex match.
        """
        for regex in self.__regexset:
            if regex.search(text):
                LOGGER.debug("%s is matched with %s", text, regex.pattern)
                return True
        return False


class Highlight(MatchFilter):
    """Word highlighting class.
    """
    def __init__(self, words: Iterable[str]) -> None:
        # If word is str, make it into list.
        if isinstance(words, str):
            words = [words]
        self.__regexset = gen_reg_set(words)

    def highlight_word(self, content: str) -> str:
        """Highlight words
        """
        for regex in self.__regexset:
            content = regex.sub(color_word, content)
        return content


def ignore(line: str) -> bool:
    """Ignore comment/blank lines.
    """
    conditions = (
        line.startswith("#"),
        line == os.linesep
    )
    return any(conditions)


def gen_word_set(csv: str) -> Set[str]:
    """Generate strings set from text file.
    """
    try:
        with open(csv, "r") as fopen:
            nameset = {ln.strip() for ln in fopen if not ignore(ln)}
    except FileNotFoundError:
        LOGGER.error(exc_msg(csv))
        return set()
    except IOError:
        LOGGER.error(exc_msg(csv))
        return set()

    return nameset


def gen_reg_set(words: Iterable[str]) -> Set[Pattern]:
    """Generate regex set from iterable containter of strings.
    """
    reglist = set()
    for word in words:
        try:
            # escaping quote/dquote is not needed.
            regex = re.compile(word.replace(r"\\", r"\\"))
        except sre_constants.error:
            LOGGER.error('"%s" is invalid pattern', word)
        else:
            reglist.add(regex)
    return reglist


def color_word(match: Match) -> str:
    """Set color
    """
    colored = "\033[{0}m{1}\033[0m".format(
        "91",
        match.group(0))
    return colored
