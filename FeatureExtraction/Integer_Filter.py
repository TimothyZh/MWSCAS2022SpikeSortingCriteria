import torch
import numpy as np
import itertools
import time
import matplotlib.pyplot as plt
import collections
from scipy.io import loadmat


# Load dataset
raw_data = loadmat('Extracted Spikes//GTthrSpike5.mat')
GTaligned = np.array(raw_data['GTthrSpike'])
spike = GTaligned
length = GTaligned.shape[0]

# Integer coefficient filter
IntFilSpike = []
for i in range(GTaligned.shape[0]):
    temp = []
    for j in range(3, 32):
        temp.append(8 * GTaligned[i, j] - 2 * GTaligned[i, j - 1] -
                    6 * GTaligned[i, j - 2] - 4 * GTaligned[i, j - 3])

    IntFilSpike.append(temp)

IntFilSpike = np.array(IntFilSpike)

# Plotting spikes
for i in range(1000):
    plt.plot(IntFilSpike[i, :])

plt.figure()
# Visualizing distribution at each sample point
for i in range(29):
    print(i)
    plt.hist(IntFilSpike[:, i], bins=50)
    plt.xlabel(i)
    plt.show()

waveMatrix = IntFilSpike

# K-means
from sklearn.cluster import KMeans
waveMatrix = IntFilSpike
# Index of IntFilSpike is selected based on the time samples that provide the best separation in each dataset
PC = np.concatenate(([IntFilSpike[:, 2]], [IntFilSpike[:, 8]], [
                    IntFilSpike[:, 9]], [IntFilSpike[:, 16]]), axis=0)
PC = np.transpose(PC)
print(PC.shape)
kmeans = KMeans(n_clusters=3, max_iter=1000).fit(PC)
group = kmeans.labels_
pc11 = PC[:, 0]
pc22 = PC[:, 1]
cdict = {0: 'red', 1: 'blue', 2: 'green'}
fig, ax = plt.subplots()
for g in np.unique(group):
    ix = np.where(group == g)
    ax.scatter(pc11[ix], pc22[ix], c=cdict[g], label=g, s=10)

ax.legend()
plt.show()
