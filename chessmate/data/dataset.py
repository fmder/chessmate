import io
import itertools
import pathlib
import re

import chess
import chess.engine
import numpy
import pandas
from torch.utils.data import Dataset

from .nnue_pytorch import halfkp
from . import utils


def _preprocess_3500k_san(content: io.BytesIO) -> pandas.DataFrame:
    data = content.read()
    data = re.sub("###\s(.*?)\s?$", "\"\g<1>\"", data, flags=re.MULTILINE)
    data = re.sub("[WB]\d+\.", "", data)
    data = io.StringIO(data)

    df = pandas.read_csv(data,
                         sep=" ",
                         usecols=[0, 1, 2, 3, 4, 5, 7, 11, 16],
                         header=None,
                         names=[
                             "id", "date", "result", "white_rating",
                             "black_rating", "len", "result_null", "setup",
                             "moves"
                         ],
                         skiprows=5)

    df = df[df["setup"] == "setup_false"]
    df = df.drop("setup", axis=1)

    df["date"] = pandas.to_datetime(df["date"], format="%Y.%m.%d", errors="coerce")
    df["white_rating"] = pandas.to_numeric(df["white_rating"], errors="coerce")
    df["black_rating"] = pandas.to_numeric(df["black_rating"], errors="coerce")
    df[df["result_null"] == "result_true"]["result"] = numpy.nan
    df = df.drop("result_null", axis=1)

    df[df["result"] == "1-0"]["winner"] = "W"
    df[df["result"] == "0-1"]["winner"] = "B"
    df[df["result"] == "1/2-1/2"]["winner"] = "D"
    df = df.drop("result", axis=1)

    return df


def _fetch_3500k_san():
    id_ = "0Bw0y3jV73lx_aXE3RnhmeE5Rb1E"
    content = utils.download_file_from_google_drive(id_)
    return content


def load_3500k_san() -> pandas.DafaFrame:
    # TODO: Find data root
    path = pathlib.Path("../data/3500k_san.feather")
    if path.exists():
        return pandas.read_feather(path)

    content = _fetch_3500k_san()
    df = _preprocess_3500k_san(content)
    path.parent.mkdir(exist_ok=True)
    df.to_feather(path)
    return df


def build_board(moves: str, move_index=None) -> chess.Board:
    board = chess.Board()
    for i, move in enumerate(moves.split(" ")):
        board.push_san(move)
    return board


def _build_index_table(data: pandas.DataFrame) -> list[tuple[int, int]]:
    index_table = []
    for i, l in enumerate(data["len"]):
        if l != l:
            continue
        index_table.extend(list(itertools.product([i], range(int(l)))))

    return index_table


class BoardLoader:
    def __init__(self):


        self.data = pandas.read_feather("../filtered_games.feather")

        self._index_table = _build_index_table(self.data)
        self._len = self.data["len"].sum()

    def __len__(self) -> int:
        return self._len

    def __getitem__(self, idx):
        game_index, move_index = self._index_table[idx]

        board = chess.Board()
        for move in self.data[game_index, "moves"].split(" ")[:move_index]:
            board.push_san(move)

        # TODO: This should be moved out of dataset into feature pipeline
        turn = board.turn        # chess.WHITE == True, chess.BLACK == False
        white_rating = self.data["white_rating"]
        black_rating = self.data["black_rating"]

        # Transform in HalfKP representation (NNUE)
        white, black = self.features.get_active_features(board)


