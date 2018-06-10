#!/usr/bin/env python3
"""Types for type hints"""
from typing import (Dict, TypeVar)


T = TypeVar("T")
TOOT = Dict[str, T]
NOTIFICATION = Dict[str, T]
