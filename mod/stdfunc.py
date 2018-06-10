#!/usr/bin/env python3
"""Standard shared functions"""
import sys


def exc_msg(target: str=None) -> str:
    info = sys.exc_info()
    etype = info[0].__name__
    args = [arg for arg in info[1].args if isinstance(arg, str)]
    msg = " ".join(args)
    if target:
        msg += ": {0} {1}".format(etype, target)
    return msg
