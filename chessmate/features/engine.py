from typing import Union

import chess.engine


MATERIAL_VALUE = {
    "p": -1, "n": -3, "b": -3, "r": -5, "q": -9, "k": 0,
    "P": 1, "N": 3, "B": 3, "R": 5, "Q": 9, "K": 0
}


def _material_advantage(board: chess.Board) -> float:
    material = 0.0
    for _, p in board.piece_map().items():
        material += MATERIAL_VALUE[p.symbol()]

    if not board.turn:
        material *= -1

    return material


def _engine_estimate(board: chess.Board, engine: chess.engine.SimpleEngine) -> float:
    analysis = engine.analyse(board, chess.engine.Limit(depth=10))
    return analysis["score"]


class EngineFeatures:
    def __init__(self, features: list[str], engine_path: Union[str, path.Pathlib]):
        self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)
        self.features = features

    def __call__(self, board) -> list[float]:
        pass



