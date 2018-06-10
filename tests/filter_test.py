#!/usr/bin/env python3
"""
    Execute this script like:

    $ python3 -m unittest tests.filter_test

    on parent directory.
"""
import os
import unittest

import mod.filtering as filtering


# import logging
# Regex debugging.
# logging.basicConfig(level=logging.DEBUG)
# LOGGER = logging.getLogger(__name__)


class TestFilter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.file = os.path.join("tests", "re.txt")
        cls.repatterns = filtering.gen_word_set(cls.file)
        cls.validStr = r"https://t\.co/test"
        cls.validTuple = ("hellowork", r"https://t\.co/test", r"\\")
        cls.validList = ["hellowork", r"https://t\.co/test", r"\\"]
        # Use tuple.
        cls.matchList = (
            "https://t.co/test",
            "hellowork",
            r"\\"
        )
        # Use list.
        cls.unmatchList = [
            "https://examplet.co/test",
        ]

    def test_match_file_0_0(self):
        mutefilter = filtering.MatchFilter(self.repatterns)
        for word in self.matchList:
            self.assertTrue(mutefilter.is_match(word))

    def test_match_file_0_1(self):
        mutefilter = filtering.MatchFilter(self.repatterns)
        for word in self.unmatchList:
            self.assertFalse(mutefilter.is_match(word))

    def test_match_file_1_0(self):
        mutefilter = filtering.MatchFilter(self.validStr)
        self.assertTrue(mutefilter.is_match(self.matchList[0]))

    def test_match_file_1_1(self):
        mutefilter = filtering.MatchFilter(self.validStr)
        for word in self.unmatchList:
            self.assertFalse(mutefilter.is_match(word))

    def test_match_file_2_0(self):
        mutefilter = filtering.MatchFilter(self.validTuple)
        for word in self.matchList:
            self.assertTrue(mutefilter.is_match(word))

    def test_match_file_2_1(self):
        mutefilter = filtering.MatchFilter(self.validTuple)
        for word in self.unmatchList:
            self.assertFalse(mutefilter.is_match(word))

    def test_match_file_3_0(self):
        mutefilter = filtering.MatchFilter(self.validList)
        for word in self.matchList:
            self.assertTrue(mutefilter.is_match(word))

    def test_match_file_3_1(self):
        mutefilter = filtering.MatchFilter(self.validList)
        for word in self.unmatchList:
            self.assertFalse(mutefilter.is_match(word))
