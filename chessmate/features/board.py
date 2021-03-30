from functools import partial

from .. import nnue_pytorch


_halfkp = nnue_pytorch.halfkp.Features()
_factorized_halfkp = nnue_pytorch.halfkp.FactorizedFeatures()
_halfka = nnue_pytorch.halfka.Features()
_factorized_halfka = nnue_pytorch.halfka.FactorizedFeatures()


def _configurable_board_repr(board, *, f=None):
    """Computes the board representation of current player"""
    if board.turn:    # White's turn
        current, other = f.get_active_features(board)
    else:             # Black's turn
        other, current = f.get_active_features(board)
    return current, other


halfkp = partial(_configurable_board_repr, f=_halfkp)
factorized_halfkp = partial(_configurable_board_repr, f=_factorized_halfkp)
halfka = partial(_configurable_board_repr, f=_halfka)
factorized_halfka = partial(_configurable_board_repr, f=_factorized_halfka)
