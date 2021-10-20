# -*- coding: utf-8 -*-
"""CrossbarWaveletFE.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1E-6EnayCACIP9xVUuAbfMgl7Z7SL2Ia9
"""

import torch
import numpy as np
import itertools
import time
import matplotlib.pyplot as plt
import collections
import random
import os

"""Crossbar Accuracy Model """

"""
crossbary.py
Louis Primeau
University of Toronto Department of Electrical and Computer Engineering
louis.primeau@mail.utoronto.ca
July 29th 2020
Last updated: March 18th 2021
https://github.com/louisprimeau/node-crossbar/blob/main/networks/crossbar/crossbar.py
"""

"""
Circuit Solver taken from:
A Comprehensive Crossbar Array Model With Solutions for Line Resistance and Nonlinear Device Characteristics
An Chen
IEEE TRANSACTIONS ON ELECTRON DEVICES, VOL. 60, NO. 4, APRIL 2013
"""

import torch
import numpy as np
import itertools
import time


# Implements scipy's minmax scaler except just between 0 and 1 for torch Tensors.
# Taken from a ptrblck post on the PyTorch forums. Love that dude.
class MinMaxScaler(object):
    def __call__(self, tensor):
        self.scale = 1.0 / (tensor.max(dim=1, keepdim=True)
                            [0] - tensor.min(dim=1, keepdim=True)[0])
        self.min = tensor.min(dim=1, keepdim=True)[0]
        tensor.sub_(self.min).mul_(self.scale)
        return tensor

    def inverse_transform(self, tensor):
        tensor.div_(self.scale).add_(self.min)
        return tensor


class crossbar:
    def __init__(self, device_params):

        # Power Supply Voltage
        self.V = device_params["Vdd"]

        # DAC resolution
        self.input_resolution = device_params["dac_resolution"]
        self.output_resolution = device_params["adc_resolution"]

        # Wordline Resistance
        self.r_wl = torch.Tensor((device_params["r_wl"],))
        # Bitline Resistance
        self.r_bl = torch.Tensor((device_params["r_bl"],))

        # Number of rows, columns
        self.size = device_params["m"], device_params["n"]

        # Crossbar conductance model
        self.method = device_params["method"]
        if (self.method == "linear"):
            self.g_on = 1 / \
                torch.normal(
                    device_params["r_on"], device_params["r_on_stddev"], size=self.size)
            self.g_off = 1 / \
                torch.normal(
                    device_params["r_off"], device_params["r_off_stddev"], size=self.size)
            # Resolution
            self.resolution = device_params["device_resolution"]
            self.conductance_states = torch.cat(
                [torch.cat([torch.linspace(self.g_off[i, j], self.g_on[i, j], 2 ** self.resolution - 1).unsqueeze(0)
                            for j in range(self.size[1])], dim=0).unsqueeze(0)
                 for i in range(self.size[0])], dim=0)

        elif self.method == "viability":
            self.g_on = 1 / \
                torch.normal(
                    device_params["r_on"], device_params["r_on_stddev"], size=self.size)
            self.g_off = 1 / \
                torch.normal(
                    device_params["r_off"], device_params["r_off_stddev"], size=self.size)
            self.viability = device_params["viability"]

        else:
            raise ValueError(
                "device_params['method'] must be \"linear\" or \"viability\"")

        self.g_wl = torch.Tensor((1 / device_params["r_wl"],))
        self.g_bl = torch.Tensor((1 / device_params["r_bl"],))

        # Bias Scheme
        self.bias_voltage = self.V * device_params["bias_scheme"]

        # Tile size (1x1 = 1T1R, nxm = passive, etc.)
        self.tile_rows = device_params["tile_rows"]
        self.tile_cols = device_params["tile_cols"]
        assert self.size[0] % self.tile_rows == 0, "tile size does not divide crossbar size in row direction"
        assert self.size[1] % self.tile_cols == 0, "tile size does not divide crossbar size in col direction"

        # Resistance of CMOS lines
        self.r_cmos_line = device_params["r_cmos_line"]

        # WL & BL resistances
        self.g_s_wl_in = torch.ones(self.tile_rows) * 1
        self.g_s_wl_out = torch.ones(self.tile_rows) * 1e-9
        self.g_s_bl_in = torch.ones(self.tile_rows) * 1e-9
        self.g_s_bl_out = torch.ones(self.tile_rows) * 1

        # WL & BL voltages that are not the signal
        self.v_bl_in = torch.zeros(self.size[1])
        self.v_bl_out = torch.ones(self.size[1])
        self.v_wl_out = torch.zeros(self.size[0])

        # Conductance Matrix; initialize each memristor at the on resstance
        self.W = torch.ones(self.size) * self.g_on

        # Stuck-on & stuck-on device nonideality
        self.p_stuck_on = device_params["p_stuck_on"]
        self.p_stuck_off = device_params["p_stuck_off"]
        self.devicefaults = False

        self.mapped = []
        self.tensors = []  # original data of all mapped weights
        self.saved_tiles = {}

    # Maps an already scaled matrix to differential weights
    def map(self, matrix):
        assert not (matrix.size(0) > self.size[0] or matrix.size(
            1) * 2 > self.size[1]), "input too large"

        if (self.method == "linear"):
            midpoint = self.conductance_states.size(2) // 2
            for i in range(matrix.size(0)):
                for j in range(matrix.size(1)):
                    shifted = self.conductance_states[i, j] - \
                        self.conductance_states[i, j, midpoint]
                    idx = torch.min(
                        torch.abs(shifted - matrix[i, j]), dim=0)[1]
                    self.W[i, 2 * j + 1] = self.conductance_states[i, j, idx]
                    self.W[i, 2 * j] = self.conductance_states[i,
                                                               j, midpoint - (idx - midpoint)]

        elif (self.method == "viability"):
            midpoint = (g_on[i, j] - g_off[i, j]) / 2 + g_off[i, j]
            for i in range(matrix.size(0)):
                for j in range(matrix.size(1)):
                    high_state = midpoint + matrix[i, j] / 2
                    low_state = midpoint - matrix[i, j] / 2
                    self.W[i, 2 * j + 1] = self.window(
                        high_state + torch.normal(mean=0, std=high_state * self.viability))
                    self.W[i, 2 * j] = self.window(low_state + torch.normal(
                        mean=0, std=low_state * self.viability))

    def solve(self, voltage):
        output = torch.zeros((voltage.size(1), self.size[1]))
        for i in range(self.size[0] // self.tile_rows):
            for j in range(self.size[1] // self.tile_cols):
                coords = (slice(i * self.tile_rows, (i + 1) * self.tile_rows),
                          slice(j * self.tile_cols, (j + 1) * self.tile_rows))
                vect = voltage[i * self.tile_rows:(i + 1) * self.tile_rows, :]
                solution = self.batch_solve(coords, vect)
                output += torch.cat((torch.zeros(voltage.size(1), j * self.tile_cols), solution, torch.zeros(
                    (voltage.size(1), (self.size[1] // self.tile_cols - j - 1) * self.tile_cols))), axis=1)
        return output

    def batch_solve(self, coords, vectors):
        if str(coords) not in self.saved_tiles.keys():
            M = self.make_M(coords)  # Lazy hash
        else:
            M = self.saved_tiles[str(coords)]
        Es = torch.cat(tuple(self.make_E(
            vectors[:, i]).view(-1, 1) for i in range(vectors.size(1))), axis=1)
        V = torch.transpose(-torch.sub(*torch.chunk(torch.matmul(M, Es), 2, dim=0)), 0, 1).view(-1, self.tile_rows,
                                                                                                self.tile_cols)
        I = torch.sum(V * self.W[coords], axis=1)
        return I

    def make_E(self, v_wl_in):
        m, n = self.tile_rows, self.tile_cols
        E = torch.cat([torch.cat(((v_wl_in[i] * self.g_s_wl_in[i]).view(1), torch.zeros(n - 2),
                                  (self.v_wl_out[i] * self.g_s_wl_out[i]).view(1))) for i in range(m)] +
                      [torch.cat(((-self.v_bl_in[i] * self.g_s_bl_in[i]).view(1), torch.zeros(m - 2),
                                  (-self.v_bl_in[i] * self.g_s_bl_out[i]).view(1))) for i in range(n)]).view(-1, 1)
        return E

    def make_M(self, coords):

        g = self.W[coords]
        m, n = self.tile_rows, self.tile_cols

        def makec(j):
            c = torch.zeros(m, m * n)
            for i in range(m):
                c[i, n * (i) + j] = g[i, j]
            return c

        def maked(j):
            d = torch.zeros(m, m * n)

            i = 0
            d[i, j] = -self.g_s_bl_in[j] - self.g_bl - g[i, j]
            d[i, n * (i + 1) + j] = self.g_bl

            for i in range(1, m):
                d[i, n * (i - 1) + j] = self.g_bl
                d[i, n * i + j] = -self.g_bl - g[i, j] - self.g_bl
                d[i, j] = self.g_bl

            i = m - 1
            d[i, n * (i - 1) + j] = self.g_bl
            d[i, n * i + j] = -self.g_s_bl_out[j] - g[i, j] - self.g_bl

            return d

        A = torch.block_diag(*tuple(torch.diag(g[i, :])
                                    + torch.diag(torch.cat((self.g_wl, self.g_wl * 2 * torch.ones(n - 2), self.g_wl)))
                                    + torch.diag(self.g_wl * -1 *
                                                 torch.ones(n - 1), diagonal=1)
                                    + torch.diag(self.g_wl * -1 *
                                                 torch.ones(n - 1), diagonal=-1)
                                    + torch.diag(
            torch.cat((self.g_s_wl_in[i].view(1), torch.zeros(n - 2), self.g_s_wl_out[i].view(1))))
            for i in range(m)))
        B = torch.block_diag(*tuple(-torch.diag(g[i, :]) for i in range(m)))
        C = torch.cat([makec(j) for j in range(n)], dim=0)
        D = torch.cat([maked(j) for j in range(0, n)], dim=0)
        M = torch.inverse(
            torch.cat((torch.cat((A, B), dim=1), torch.cat((C, D), dim=1)), dim=0))

        self.saved_tiles[str(coords)] = M

        return M

    def register_linear(self, matrix, bias=None):

        self.tensors.append(matrix)
        row, col = self.find_space(matrix.size(0), matrix.size(1))
        # Need to add checks for bias size and col size

        # Scale matrix

        if (self.method == "linear"):
            mat_scale_factor = torch.max(
                torch.abs(matrix)) / torch.max(self.g_on) * 2
            scaled_matrix = matrix / mat_scale_factor
            midpoint = self.conductance_states.size(2) // 2
            for i in range(row, row + scaled_matrix.size(0)):
                for j in range(col, col + scaled_matrix.size(1)):
                    shifted = self.conductance_states[i, j] - \
                        self.conductance_states[i, j, midpoint]
                    idx = torch.min(
                        torch.abs(shifted - scaled_matrix[i - row, j - col]), dim=0)[1]
                    self.W[i, 2 * j + 1] = self.conductance_states[i, j, idx]
                    self.W[i, 2 * j] = self.conductance_states[i,
                                                               j, midpoint - (idx - midpoint)]

        elif (self.method == "viability"):
            mat_scale_factor = torch.max(
                torch.abs(matrix)) / (torch.max(self.g_on) - torch.min(self.g_off)) * 2
            scaled_matrix = matrix / mat_scale_factor
            for i in range(row, row + scaled_matrix.size(0)):
                for j in range(col, col + scaled_matrix.size(1)):
                    midpoint = (
                        self.g_on[i, j] - self.g_off[i, j]) / 2 + self.g_off[i, j]
                    right_state = midpoint + \
                        scaled_matrix[i - row, j - col] / 2
                    left_state = midpoint - scaled_matrix[i - row, j - col] / 2
                    self.W[i, 2 * j + 1] = self.clip(
                        right_state + torch.normal(mean=0, std=right_state * self.viability), i, 2 * j + 1)
                    self.W[i, 2 * j] = self.clip(left_state + torch.normal(mean=0, std=left_state * self.viability), i,
                                                 2 * j)

        return ticket2(row, col, matrix.size(0), matrix.size(1), matrix, mat_scale_factor, self)

    def clip(self, tensor, i, j):
        if self.g_off[i, j] < tensor < self.g_on[i, j]:
            return tensor
        elif tensor > self.g_on[i, j]:
            return self.g_on[i, j]
        else:
            return self.g_off[i, j]

    def apply_stuck(self, p_stuck_on, p_stuck_off):

        state_dist = torch.distributions.categorical.Categorical(
            probs=torch.Tensor([p_stuck_on, p_stuck_off, 1 - p_stuck_on - p_stuck_off]))
        state_mask = state_dist.sample(self.size)

        self.W[state_mask == 0] = self.g_off[state_mask == 0]
        self.W[state_mask == 1] = self.g_on[state_mask == 1]

        return None

    def which_tiles(self, row, col, m_row, m_col):
        return itertools.product(range(row // self.tile_rows, (row + m_row) // self.tile_rows + 1),
                                 range(col // self.tile_cols,
                                       (col + m_col) // self.tile_cols + 1),
                                 )

    def find_space(self, m_row, m_col):
        if not self.mapped:
            self.mapped.append((0, 0, m_row, m_col))
        else:
            self.mapped.append(
                (self.mapped[-1][0] + self.mapped[-1][2], self.mapped[-1][1] + self.mapped[-1][3], m_row, m_col))
        return self.mapped[-1][0], self.mapped[-1][1]

    def clear(self):
        self.mapped = []
        self.tensors = []
        self.saved_tiles = {}
        self.W = torch.ones(self.size) * self.g_on


class ticket2:
    def __init__(self, row, col, m_rows, m_cols, matrix, mat_scale_factor, crossbar):
        self.row, self.col = row, col
        self.m_rows, self.m_cols = m_rows, m_cols
        self.crossbar = crossbar
        self.mat_scale_factor = mat_scale_factor
        self.matrix = matrix

    def prep_vector(self, vector, v_bits):

        # Scale vector to [0, 2^v_bits]
        vect_min = torch.min(vector)
        vector = vector - vect_min
        vect_scale_factor = torch.max(vector) / (2 ** v_bits - 1)
        vector = vector / vect_scale_factor if vect_scale_factor != 0.0 else vector

        # decompose vector by bit
        bit_vector = torch.zeros(vector.size(0), v_bits)
        def bin2s(x): return "".join(
            reversed([str((int(x) >> i) & 1) for i in range(v_bits)]))
        for j in range(vector.size(0)):
            bit_vector[j, :] = torch.Tensor(
                [float(i) for i in list(bin2s(vector[j]))])
        bit_vector *= self.crossbar.V

        # Pad bit vector with unselected voltages
        pad_vector = torch.zeros(self.crossbar.size[0], v_bits)

        pad_vector[self.row:self.row + self.m_rows, :] = bit_vector

        return pad_vector, vect_scale_factor, vect_min

    def vmm(self, vector, v_bits=4):
        assert vector.size(1) == 1, "vector wrong shape"

        crossbar = self.crossbar

        # Rescale vector and convert to bits.
        pad_vector, vect_scale_factor, vect_min = self.prep_vector(
            vector, v_bits)

        # Solve crossbar circuit
        output = crossbar.solve(pad_vector)

        # Get relevant output columns and add binary outputs

        output = output.view(
            v_bits, -1, 2)[:, :, 0] - output.view(v_bits, -1, 2)[:, :, 1]

        for i in range(output.size(0)):
            output[i] *= 2 ** (v_bits - i - 1)
        output = torch.sum(output, axis=0)[self.col:self.col + self.m_cols]

        # Rescale output
        # can use to compensate for resistive losses in the lines. Recommend multiplying a bunch of 8x8 integer matrices to find this.
        magic_number = 1

        output = (output / crossbar.V * vect_scale_factor * self.mat_scale_factor) / magic_number + torch.sum(
            vect_min * self.matrix, axis=0)

        return output.view(-1, 1)


# setting device parameter
device_params = {"Vdd": 0.2,
                 "r_wl": 20.0,
                 "r_bl": 20.0,
                 "m": 128,
                 "n": 128,
                 "r_on": 1e4,
                 "r_off": 1e5,
                 "dac_resolution": 4,
                 "adc_resolution": 14,
                 "bias_scheme": 1 / 3,
                 "tile_rows": 8,
                 "tile_cols": 8,
                 "r_cmos_line": 600,
                 "r_cmos_transistor": 20,
                 "r_on_stddev": 1e3,
                 "r_off_stddev": 1e4,
                 "p_stuck_on": 0.01,
                 "p_stuck_off": 0.01,
                 "method": "viability",
                 "viability": 0.05,
                 }

cb = crossbar(device_params)

seed = 12
random.seed(seed)
os.environ['PYTHONHASHSEED'] = str(seed)
np.random.seed(seed)
torch.manual_seed(seed)


def vmmdot(matrix, vector):
    matrix = torch.tensor(matrix)
    vector = torch.tensor(vector)
    cb.clear()
    ticket = cb.register_linear(torch.transpose(matrix, 0, 1))
    output = ticket.vmm(vector, v_bits=4)
    result = matrix.matmul(vector)
    result = np.array(result)
    return result


a = torch.ones((10, 10)) * 0.1
b = torch.zeros((10, 1)).uniform_(0, 1)
out = vmmdot(a, b)
print((a * b).sum(axis=0))
print(out)
exit(0)
"""Loading Dataset 

"""

# from google.colab import drive
# drive.mount('/content/drive')


from scipy.io import loadmat
# addpath(fullfile('Desktop'));
# raw_data=loadmat('/content/drive/My Drive/SURE2021/GTaligned1.mat')
raw_data = loadmat('Extracted Spikes/GTthrAligned1.mat')
# print(raw_data)
GTaligned = np.array(raw_data['GTthrAligned'])


print(GTaligned.shape)

spike = GTaligned

length = GTaligned.shape[0]
print(length)

"""Iteration 1"""
print('Interation 1')

A1 = np.zeros((16, 32))  # lowpass
B1 = np.zeros((16, 32))  # highpass

# record high passed version
H1 = np.zeros((length, 16))  # change matrix size based on number of samples
L1 = np.zeros((length, 16))
for i in range(16):
    A1[i, 2 * i] = 1
    A1[i, 2 * i + 1] = 1
    B1[i, 2 * i] = 1
    B1[i, 2 * i + 1] = -1

A1 = (1 / 2) * A1
B1 = (1 / 2) * B1

for i in range(length):
    t = np.array([spike[i, :]])
    t = np.transpose(t)
    y0 = vmmdot(A1, t)

    L1[i, :] = np.squeeze(y0)
    y1 = vmmdot(B1, t)
    H1[i, :] = np.squeeze(y1)

"""Iteration *2*"""
print('Interation 2')

A2 = np.zeros((8, 16))  # lowpass
B2 = np.zeros((8, 16))  # highpass

# record high passed version
H2 = np.zeros((length, 8))
L2 = np.zeros((length, 8))
for i in range(8):
    A2[i, 2 * i] = 1
    A2[i, 2 * i + 1] = 1
    B2[i, 2 * i] = 1
    B2[i, 2 * i + 1] = -1

A2 = (1 / 2) * A2
B2 = (1 / 2) * B2

for i in range(length):
    t = np.array([L1[i, :]])
    t = np.transpose(t)
    y0 = vmmdot(A2, t)
    L2[i, :] = np.squeeze(y0)
    y1 = vmmdot(B2, t)
    H2[i, :] = np.squeeze(y1)

"""iteration 3"""
print('Interation 3')

A3 = np.zeros((4, 8))  # lowpass
B3 = np.zeros((4, 8))  # highpass

# record high passed version
H3 = np.zeros((length, 4))
L3 = np.zeros((length, 4))
for i in range(4):
    A3[i, 2 * i] = 1
    A3[i, 2 * i + 1] = 1
    B3[i, 2 * i] = 1
    B3[i, 2 * i + 1] = -1

A3 = (1 / 2) * A3
B3 = (1 / 2) * B3

for i in range(length):
    t = np.array([L2[i, :]])
    t = np.transpose(t)
    y0 = vmmdot(A3, t)
    L3[i, :] = np.squeeze(y0)
    y1 = vmmdot(B3, t)
    H3[i, :] = np.squeeze(y1)

"""Iteration 4"""
print('Interation 4')

A4 = np.zeros((2, 4))  # lowpass
B4 = np.zeros((2, 4))  # highpass

# record high passed version
H4 = np.zeros((length, 2))
L4 = np.zeros((length, 2))
for i in range(2):
    A4[i, 2 * i] = 1
    A4[i, 2 * i + 1] = 1
    B4[i, 2 * i] = 1
    B4[i, 2 * i + 1] = -1

A4 = (1 / 2) * A4
B4 = (1 / 2) * B4

for i in range(length):
    t = np.array([L3[i, :]])
    t = np.transpose(t)
    y0 = vmmdot(A4, t)
    L4[i, :] = np.squeeze(y0)
    y1 = vmmdot(B4, t)
    H4[i, :] = np.squeeze(y1)

"""Iteration 5"""
print('Interation 5')

A5 = np.zeros((1, 2))  # lowpass
B5 = np.zeros((1, 2))  # highpass

# record high passed version
H5 = np.zeros((length, 1))
L5 = np.zeros((length, 1))
for i in range(1):
    A5[i, 2 * i] = 1
    A5[i, 2 * i + 1] = 1
    B5[i, 2 * i] = 1
    B5[i, 2 * i + 1] = -1

A5 = (1 / 2) * A5
B5 = (1 / 2) * B5

for i in range(length):
    t = np.array([L4[i, :]])
    t = np.transpose(t)
    y0 = vmmdot(A5, t)
    L5[i, :] = np.squeeze(y0)
    y1 = vmmdot(B5, t)
    H5[i, :] = np.squeeze(y1)

# required size 897x32

wavespike = np.concatenate((L5, H5, H4, H3, H2, H1), axis=1)
print(wavespike.shape)

"""K means 
"""
print('KMeans')

from sklearn.cluster import KMeans
pc = []
pc1 = np.array([waveMatrix[:, 9]])
pc2 = np.array([waveMatrix[:, 21]])
PC = np.concatenate((pc1, pc2), axis=0)
PC = np.transpose(PC)
print(PC.shape)
kmeans = KMeans(n_clusters=3, max_iter=1000).fit(PC)  # random_state=0,

group = kmeans.labels_

pc11 = waveMatrix[:, 9]
pc22 = waveMatrix[:, 21]
cdict = {0: 'red', 1: 'blue', 2: 'green'}
fig, ax = plt.subplots()
for g in np.unique(group):
    ix = np.where(group == g)
    ax.scatter(pc11[ix], pc22[ix], c=cdict[g], label=g, s=10)
ax.legend()
plt.show()

Features = PC
