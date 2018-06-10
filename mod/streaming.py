#!/usr/bin/env python3
from typing import (Tuple, List)
from urllib.parse import urljoin
import contextlib
import operator
import sys

import requests

from .deftypes import (NOTIFICATION, TOOT)
from .parser import (decode_json, TootContentParser)


class MstdnStreamListener:
    def __init__(self) -> None:
        self.parser = TootContentParser()  # type: TootContentParser

    def on_update(self, toot: TOOT) -> None:
        pass

    def on_notification(self, notification: NOTIFICATION) -> None:
        pass

    def on_delete(self, data: str) -> None:
        pass


class MstdnStream:
    def __init__(self,
                 base_url: str,
                 access_token: str,
                 listener: MstdnStreamListener) -> None:
        self.base_url = base_url  # type: str
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": "Bearer " + access_token})
        self.listener = listener  # type: MstdnStreamListener
        self.exclude = (b"", b":thump")  # type: Tuple[bytes, bytes]
        self.events = (
            "update",
            "notification",
            "delete"
        )  # type: Tuple[str, str, str]

    def decode_lines(self, lines: bytes) -> List[str]:
        toots = []
        for line in lines.split(b"\x00"):
            if line in self.exclude:
                continue
            toots.append(line.decode("utf-8"))
        return toots

    def home(self) -> None:
        self.stream(urljoin(self.base_url, "/api/v1/streaming/user"))

    def public(self) -> None:
        self.stream(urljoin(self.base_url, "/api/v1/streaming/public"))

    def local(self) -> None:
        self.stream(urljoin(self.base_url, "/api/v1/streaming/public/local"))

    def stream(self, url: str) -> None:
        with contextlib.closing(self.session.get(url, stream=True)) as resp:
            try:
                resp.raise_for_status()
            except requests.exceptions.HTTPError as err:
                sys.exit("[ERR]{0}".format(err.response))

            event = None
            for iter_lines in resp.iter_lines():
                lines = self.decode_lines(iter_lines)
                for receive in lines:
                    if receive.startswith("event:"):
                        event = receive.split(":", 1)[1].strip()
                        continue
                    data = receive.replace("data: ", "")
                    toot = decode_json(data)

                    if event:
                        call = operator.methodcaller(
                            "on_{0}".format(event), toot)
                        call(self.listener)
                        event = None
