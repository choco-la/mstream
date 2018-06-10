#!/usr/bin/env python3
"""Parse toot json"""
from html.parser import HTMLParser
from typing import (Dict, Callable)
from urllib.parse import urlparse
import functools
import json
import os


from .deftypes import TOOT


class TootContentParser(HTMLParser):
    """Parse toot content"""
    def __init__(self) -> None:
        super(TootContentParser, self).__init__()
        self.__content = ""  # type: str

    def handle_starttag(self, tag, attrs) -> None:
        if tag == "br":
            self.__content += os.linesep

    def handle_data(self, data) -> None:
        self.__content += data

    @property
    def content(self) -> str:
        try:
            return self.__content
        finally:
            self.__content = ""

    def parse_content(self, toot: TOOT) -> str:
        self.feed(toot["content"])
        return self.content


def decode_json(data: str) -> TOOT:
    return json.loads(data)


def color_name(func: Callable) -> Callable:
    @functools.wraps(func)
    def newfunc(*args, **kwargs):
        dic = func(*args, **kwargs)
        dic["display"] = "\033[{0}m{1}\033[0m".format(
            "96",
            dic["display"])
        return dic
    return newfunc


@color_name
def parse_name(toot: TOOT) -> Dict[str, str]:
    account = toot["account"]
    host = urlparse(account["url"]).netloc
    username = account["username"]
    displayname = account["display_name"]

    namedict = {
        "account": "{0}@{1}".format(username, host),
        "display": displayname
    }
    return namedict
