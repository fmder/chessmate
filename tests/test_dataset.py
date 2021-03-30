import unittest

import numpy
import pandas

from chess_player import dataset


class TestBuildIndexTable(unittest.TestCase):
    def test_empty_dataframe(self):
        df = pandas.DataFrame({"len": []})
        index_table = dataset._build_index_table(df)

        self.assertSequenceEqual(index_table, [])

    def test_dataframe_has_nan(self):
        df = pandas.DataFrame({"len": [2, 1, numpy.nan]})
        index_table = dataset._build_index_table(df)

        expected = [(0, 0), (0, 1), (1, 0)]

        self.assertSequenceEqual(index_table, expected)

    def test_index_table(self):
        df = pandas.DataFrame({"len": [2, 1, 3]})
        index_table = dataset._build_index_table(df)

        expected = [(0, 0), (0, 1), (1, 0), (2, 0), (2, 1), (2, 2)]

        self.assertSequenceEqual(index_table, expected)