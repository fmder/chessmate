import torch
from torch import nn


# 3 layer fully connected network
L1 = 256
L2 = 32
L3 = 32

# HalfKP Params
NUM_SQ = 64
NUM_PT = 10
NUM_PLANES = (NUM_SQ * NUM_PT + 1)


class NNUEEmbedding(nn.Module):
    def __init__(self, checkpoint):
        super().__init__()

        # Stockfish trains its neural nets with HalfKP representation
        # which has 41024 features
        num_features = NUM_PLANES * NUM_SQ
        self.input = nn.Linear(num_features, L1)
        self.l1 = nn.Linear(2 * L1, L2)
        self.l2 = nn.Linear(L2, L3)
        self.output = nn.Linear(L3, 1)

        self.load_state_dict(torch.load(checkpoint))
        self.eval()

        # We only want the board encoding
        del self.output

    def forward(self, current, other):
        w = self.input(current)
        b = self.input(other)
        l0_ = torch.cat([w, b], dim=1)
        # clamp here is used as a clipped relu to (0.0, 1.0)
        l0_ = torch.clamp(l0_, 0.0, 1.0)
        l1_ = torch.clamp(self.l1(l0_), 0.0, 1.0)
        l2_ = torch.clamp(self.l2(l1_), 0.0, 1.0)
        return l2_
