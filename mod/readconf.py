#!/usr/bin/env python3
from configparser import ConfigParser
import os


def read_conf(path: str) -> ConfigParser:
    config = ConfigParser()
    config.read(path)

    filterdir = config["DIRECTORY"]["FilterDir"]
    config["FILE"]["ContentFilter"] = os.path.join(
        filterdir,
        config["FILE"]["ContentFilter"])
    config["FILE"]["AccountFilter"] = os.path.join(
        filterdir,
        config["FILE"]["AccountFilter"])
    config["FILE"]["ClientFilter"] = os.path.join(
        filterdir,
        config["FILE"]["ClientFilter"])
    config["FILE"]["HighlightWords"] = os.path.join(
        filterdir,
        config["FILE"]["HighlightWords"])

    return config
