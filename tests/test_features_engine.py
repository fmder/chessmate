import unittest
from unittest import mock

import chess
import chess.engine

from chessmate.features import engine


class TestEngineFeature(unittest.TestCase):
    def test_get_line(self):
        black_score = 648

        analyse_return_value = {
            'string': 'NNUE evaluation using nn-82215d0fd0df.nnue enabled',
            'depth': 3,
            'seldepth': 3,
            'multipv': 1,
            'score': chess.engine.PovScore(chess.engine.Cp(black_score), chess.BLACK),
            'nodes': 133,
            'nps': 66500,
            'tbhits': 0,
            'time': 0.002,
            'pv': [
                chess.Move.from_uci('d4f5'),
                chess.Move.from_uci('e4f5'),
                chess.Move.from_uci('e7g5')
            ]
        }

        expected_line = [
            chess.Move.from_uci('d4f5'),
            chess.Move.from_uci('e4f5'),
            chess.Move.from_uci('e7g5')
        ]

        with mock.patch("chessmate.features.engine.EngineFeature.engine") as mock_engine:
            mock_engine.analyse.return_value = analyse_return_value

            engine_feature = engine.EngineFeature()
            result = engine_feature._get_line(None, None)

        self.assertEqual(result, expected_line)

    def test_get_pov_score_as_white(self):
        black_score = 648
        expected_white_score = -black_score

        analyse_return_value = {
            'string': 'NNUE evaluation using nn-82215d0fd0df.nnue enabled',
            'depth': 3,
            'seldepth': 3,
            'multipv': 1,
            'score': chess.engine.PovScore(chess.engine.Cp(black_score), chess.BLACK),
            'nodes': 133,
            'nps': 66500,
            'tbhits': 0,
            'time': 0.002,
            'pv': [
                chess.Move.from_uci('d4f5'),
                chess.Move.from_uci('e4f5'),
                chess.Move.from_uci('e7g5')
            ]
        }

        with mock.patch("chessmate.features.engine.EngineFeature.engine") as mock_engine:
            mock_engine.analyse.return_value = analyse_return_value

            engine_feature = engine.EngineFeature()
            result = engine_feature._get_pov_score(None, chess.WHITE, None, mate_score=318)

        self.assertEqual(result, expected_white_score)

    def test_get_pov_score_as_black(self):
        expected_black_score = 648

        analyse_return_value = {
            'string': 'NNUE evaluation using nn-82215d0fd0df.nnue enabled',
            'depth': 3,
            'seldepth': 3,
            'multipv': 1,
            'score': chess.engine.PovScore(chess.engine.Cp(expected_black_score), chess.BLACK),
            'nodes': 133,
            'nps': 66500,
            'tbhits': 0,
            'time': 0.002,
            'pv': [
                chess.Move.from_uci('d4f5'),
                chess.Move.from_uci('e4f5'),
                chess.Move.from_uci('e7g5')
            ]
        }

        with mock.patch("chessmate.features.engine.EngineFeature.engine") as mock_engine:
            mock_engine.analyse.return_value = analyse_return_value

            engine_feature = engine.EngineFeature()
            result = engine_feature._get_pov_score(None, chess.BLACK, None, mate_score=318)

        self.assertEqual(result, expected_black_score)

    def test_get_pov_raises(self):
        engine_feature = engine.EngineFeature()
        engine_feature.engine = None
        with self.assertRaises(RuntimeError):
            engine_feature._get_pov_score(None, None, None, None)


class TestRawMaterialScore(unittest.TestCase):
    def test_depth(self):
        expected_depth = 7
        expected_use_ply = [True] * 7
        rms = engine.RawMaterialScores(depth=expected_depth)
        self.assertEqual(rms.depth, expected_depth)
        self.assertSequenceEqual(rms.use_ply, expected_use_ply)

    def test_relative_plies(self):
        relative_plies = [0, 1, 5]
        expected_use_ply = [True, True, False, False, False, True]
        rms = engine.RawMaterialScores(relative_plies=relative_plies)
        self.assertEqual(rms.depth, 6)
        self.assertSequenceEqual(rms.use_ply, expected_use_ply)

    def test_raw_material_score_white_2_up(self):
        expected_score = 2
        fen = "rn2k3/p2b1p1p/3bp2B/8/1p6/1P1q4/P2P1PNP/R2QR1K1 w q - 0 18"
        board = chess.Board(fen=fen)
        rms = engine.RawMaterialScores(depth=0)
        result = rms._raw_material_score(board, chess.WHITE)
        self.assertEqual(result, expected_score)

    def test_raw_material_score_black_2_down(self):
        expected_score = -2
        fen = "rn2k3/p2b1p1p/3bp2B/8/1p6/1P1q4/P2P1PNP/R2QR1K1 w q - 0 18"
        board = chess.Board(fen=fen)
        rms = engine.RawMaterialScores(depth=0)
        result = rms._raw_material_score(board, chess.BLACK)
        self.assertEqual(result, expected_score)

    def test_raw_material_score_white_1_down(self):
        expected_score = -1
        fen = "rn2k3/p2b1p1p/4p2B/8/1p3b2/1P1q4/P2P1P1P/R2QR1K1 w q - 0 19"
        board = chess.Board(fen=fen)
        rms = engine.RawMaterialScores(depth=0)
        result = rms._raw_material_score(board, chess.WHITE)
        self.assertEqual(result, expected_score)

    def test_raw_material_score_black_1_up(self):
        expected_score = 1
        fen = "rn2k3/p2b1p1p/4p2B/8/1p3b2/1P1q4/P2P1P1P/R2QR1K1 w q - 0 19"
        board = chess.Board(fen=fen)
        rms = engine.RawMaterialScores(depth=0)
        result = rms._raw_material_score(board, chess.BLACK)
        self.assertEqual(result, expected_score)

    def test_raw_material_score_line_as_white(self):
        fen = "1r1q1rk1/3nbppp/p1bp4/2p1pN2/P2nP3/2NP3P/1BPQ1PP1/1R2KB1R b K - 6 16"
        board = chess.Board(fen=fen)
        analyse_return_value = {
            'string': 'NNUE evaluation using nn-82215d0fd0df.nnue enabled',
            'depth': 5,
            'seldepth': 5,
            'multipv': 1,
            'score': chess.engine.PovScore(chess.engine.Cp(648), chess.BLACK),
            'nodes': 228,
            'nps': 114000,
            'tbhits': 0,
            'time': 0.002,
            'pv': [
                chess.Move.from_uci('d4f5'),
                chess.Move.from_uci('e4f5'),
                chess.Move.from_uci('e7g5'),
                chess.Move.from_uci('d2d1'),
                chess.Move.from_uci('d8a5'),
                chess.Move.from_uci('b2a1'),
                chess.Move.from_uci('d6d5')
            ]
        }

        rms = engine.RawMaterialScores(depth=5)
        expected_scores = [0, -3, 0, 0, 0, 0]

        with mock.patch("chessmate.features.engine.EngineFeature.engine") as mock_engine:
            mock_engine.analyse.return_value = analyse_return_value

            result = rms(board)

        self.assertSequenceEqual(result, expected_scores)

    def test_raw_material_score_black_turn(self):
        fen = "1r1q1rk1/3nbppp/p1bp4/2p1pn2/P3P3/2NP3P/1BPQ1PP1/1R2KB1R w K - 0 17"
        board = chess.Board(fen=fen)
        analyse_return_value = {
            'string': 'NNUE evaluation using nn-82215d0fd0df.nnue enabled',
            'depth': 5,
            'seldepth': 5,
            'multipv': 1,
            'score': chess.engine.PovScore(chess.engine.Cp(648), chess.BLACK),
            'nodes': 228,
            'nps': 114000,
            'tbhits': 0,
            'time': 0.002,
            'pv': [
                chess.Move.from_uci('e4f5'),
                chess.Move.from_uci('e7g5'),
                chess.Move.from_uci('d2d1'),
                chess.Move.from_uci('d8a5'),
                chess.Move.from_uci('b2a1'),
                chess.Move.from_uci('d6d5'),
                chess.Move.from_uci('h3h4')
            ]
        }

        rms = engine.RawMaterialScores(depth=5)
        expected_scores = [3, 0, 0, 0, 0, 0]

        with mock.patch("chessmate.features.engine.EngineFeature.engine") as mock_engine:
            mock_engine.analyse.return_value = analyse_return_value

            result = rms(board)

        self.assertSequenceEqual(result, expected_scores)

class TestEngineEstimate(unittest.TestCase):
    def test_fail(self):
        raise NotImplementedError()