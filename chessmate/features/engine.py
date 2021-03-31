from typing import Union

import chess.engine


MATERIAL_VALUE = {
    "p": -1, "n": -3, "b": -3, "r": -5, "q": -9, "k": 0,
    "P": 1, "N": 3, "B": 3, "R": 5, "Q": 9, "K": 0
}

stockfish_path = "/usr/local/bin/stockfish"

class EngineFeature:
    # TODO: need config file
    engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)

    def _get_line(self, board, depth) -> list[chess.Move]:
        analysis = self.engine.analyse(board, chess.engine.Limit(depth=depth))
        return analysis["pv"]

    def _get_pov_score(self, board, pov, depth, mate_score=1000):
        analysis = self.engine.analyse(board, chess.engine.Limit(depth=depth))
        pov_score = analysis["score"].pov(pov, mate_score)
        return pov_score


class RawMaterialScores(EngineFeature):
    """Computes the raw material scores at given plies following the best
    line for this move."""
    def __init__(self, *, depth=None, relative_plies=None):
        if (depth is None) == (relative_plies is None):
            raise ValueError("One and only one of depth and plies should be provided")

        if depth is not None:
            self.depth = depth
            self.plies = list(range(self.depth))
        elif relative_plies is not None:
            self.depth = max(relative_plies)
            self.plies = sorted(relative_plies)

    def __call__(self, board: chess.Board) -> list[float]:
        material_scores: list[float] = list()
        plies = iter(self.plies)
        next_ply = next(plies)

        # We are in a situation where we evaluate a given move (already played here).
        # So if we want to evaluate the value of a move it is the value as the
        # other player (which is ours!)
        us = not board.turn

        for i, move in enumerate(self._get_line(board, self.depth)):
            board.push_uci(move.uci())
            if next_ply != i:
                continue

            score = sum(MATERIAL_VALUE[p.symbol()] for _, p in board.piece_map().items())

            if us == chess.BLACK:
                # Invert black score
                score *= -1

            material_scores.append(score)
            next_ply = next(plies)

        return material_scores


class EngineEstimate(EngineFeature):
    """Computes the engine estimate score for this move """
    def __init__(self, depth, mate_score=318):
        self.depth = depth
        self.mate_score = mate_score

    def __call__(self, board) -> float:
        # We are in a situation where the move has already been played
        # So if we want to evaluate the value this move value it is seen as the
        # previous player point of view
        us = not board.turn
        return self._get_pov_score(board, us, self.depth, self.mate_score)
