from typing import Union

import chess.engine


MATERIAL_VALUE = {
    "p": -1, "n": -3, "b": -3, "r": -5, "q": -9, "k": 0,
    "P": 1, "N": 3, "B": 3, "R": 5, "Q": 9, "K": 0
}

stockfish_path = "/usr/local/bin/stockfish"

def _start_engine(path) -> Union[chess.engine.SimpleEngine, None]:
    try:
        return chess.engine.SimpleEngine.popen_uci(path)
    except FileNotFoundError:
        return None


class EngineFeature:
    # TODO: need config file
    engine = _start_engine(stockfish_path)

    def _get_line(self, board, depth) -> list[chess.Move]:
        if self.engine is None:
            raise RuntimeError
        analysis = self.engine.analyse(board, chess.engine.Limit(depth=depth))
        return analysis["pv"]

    def _get_pov_score(self, board, pov, depth, mate_score=1000):
        if self.engine is None:
            raise RuntimeError

        analysis = self.engine.analyse(board, chess.engine.Limit(depth=depth))
        pov_score = analysis["score"].pov(pov).score(mate_score=mate_score)
        return pov_score

    def __del__(self):
        if self.engine is not None:
            self.engine.close()




class RawMaterialScores(EngineFeature):
    """Computes the raw material scores at given plies following the best
    line for this move."""
    def __init__(self, *, depth=None, relative_plies=None):
        if (depth is None) == (relative_plies is None):
            raise ValueError("One and only one of depth and plies should be provided")

        if depth is not None:
            self.depth = depth
            self.use_ply = [True] * depth
        elif relative_plies is not None:
            self.depth = max(relative_plies) + 1
            self.use_ply = [i in relative_plies for i in range(self.depth)]

        self._feature_length = sum(self.use_ply) + 1

    def _raw_material_score(self, board, pov) -> float:
        score = sum(MATERIAL_VALUE[p.symbol()] for _, p in board.piece_map().items())
        if pov == chess.BLACK:
            # Invert black score
            score *= -1
        return score

    def __call__(self, board: chess.Board) -> list[float]:
        # We are in a situation where we evaluate a given move (already played here).
        # So if we want to evaluate the value of a move it is the value as the
        # other player (which is ours!)
        us = not board.turn

        # First move is already done, get current material score
        material_scores: list[float] = []
        if len(self.use_ply) > 1 and self.use_ply[0]:
            material_scores.append(self._raw_material_score(board, us))


        print(f"us = {'white' if us else 'black'}")

        line = self._get_line(board, self.depth + 2)
        for move, use_ply in zip(line, self.use_ply):
            board.push(move)
            if not use_ply:
                continue

            material_scores.append(self._raw_material_score(board, us))

        if len(material_scores) < self._feature_length:
            material_scores += [float("nan")] * (self._feature_length - len(material_scores))

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
