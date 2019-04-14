from typing import Tuple

import torch
from torch import nn
from torch.nn import functional as F

from constants import HIDDEN_DIM_G, LAYERS_G, BIDIRECTIONAL_G, TYPE_G, MAX_POLYPHONY
from model.gan.RNN import RNN
from utils.tensors import device


class GANGenerator(nn.Module):
    def __init__(self):
        """
        **Generator** network of a GAN model.
        Applies a RNN to a random noise generator, and passes each hidden state through a Dense Layer.
        Tries to generate realistic synthetic data to trick the **Discriminator** to make it say that it's real.
        """
        super(GANGenerator, self).__init__()

        self.rnn = RNN(architecture=TYPE_G,
                       inp_dim=1,
                       hid_dim=HIDDEN_DIM_G,
                       layers=LAYERS_G,
                       bidirectional=BIDIRECTIONAL_G).to(device)

        dense_input_features = (2 if BIDIRECTIONAL_G else 1) * HIDDEN_DIM_G
        self.dense_1 = nn.Linear(in_features=dense_input_features, out_features=2 * MAX_POLYPHONY)
        self.dense_2 = nn.Linear(in_features=2 * MAX_POLYPHONY, out_features=MAX_POLYPHONY)

    def forward(self, x):
        x, _ = self.rnn(x, )
        x = F.leaky_relu(x)
        x = F.dropout(x)

        x = self.dense_1(x)
        x = F.leaky_relu(x)
        x = F.dropout(x)

        x = self.dense_2(x)
        x = F.relu(x)

        return x

    @staticmethod
    def noise(dims: Tuple):
        """
        Generates a 2-d vector of uniform sampled random values.
        :param dims: Tuple with the dimensions of the data.
        """
        return torch.randn(dims + (1,), dtype=torch.float).to(device)
