from functools import partial

from ..nnue_pytorch import halfka as nnue_halfka
from ..nnue_pytorch import halfkp as nnue_halfkp


_halfka = nnue_halfka.Features()
_factorized_halfka = nnue_halfka.FactorizedFeatures()
_halfkp = nnue_halfkp.Features()
_factorized_halfkp = nnue_halfkp.FactorizedFeatures()


def _configurable_board_repr(board, *, f=None):
    """Computes the board representation of current player"""
    if board.turn:    # White's turn
        current, other = f.get_active_features(board)
    else:             # Black's turn
        other, current = f.get_active_features(board)
    return current, other


halfka = partial(_configurable_board_repr, f=_halfka)
factorized_halfka = partial(_configurable_board_repr, f=_factorized_halfka)
halfkp = partial(_configurable_board_repr, f=_halfkp)
factorized_halfkp = partial(_configurable_board_repr, f=_factorized_halfkp)
