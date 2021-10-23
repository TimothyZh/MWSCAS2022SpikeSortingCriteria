import torch
import numpy as np
import itertools
import time
import matplotlib.pyplot as plt
import collections
import random
import os

# Features variable refers to the n by 2 matrix obtained from feature extraction, where n is the number of spikes and 2 features are associated with each spike.
# K-means
from sklearn.cluster import KMeans

kmeans = KMeans(n_clusters=3, max_iter=1000).fit(PC)  # random_state=0,
group = kmeans.labels_
pc11 = Features[:, 0]
pc22 = Features[:, 1]
cdict = {0: "red", 1: "blue", 2: "green"}
fig, ax = plt.subplots()
for g in np.unique(group):
    ix = np.where(group == g)
    ax.scatter(pc11[ix], pc22[ix], c=cdict[g], label=g, s=10)
ax.legend()
plt.show()

# Gaussian mixture model
from sklearn.mixture import GaussianMixture

gmm = GaussianMixture(n_components=3)
gmm.fit(Features)
group = gmm.predict(Features)
pc11 = Features[:, 0]
pc22 = Features[:, 1]
cdict = {0: "red", 1: "blue", 2: "green"}
fig, ax = plt.subplots()
for g in np.unique(group):
    ix = np.where(group == g)
    ax.scatter(pc11[ix], pc22[ix], c=cdict[g], label=g, s=10)

ax.legend()
plt.show()

# Accuracy testing
from scipy.io import loadmat

raw_data = loadmat("../FeatureExtraction/Extracted Spike Labels/GTthr1.mat")
spikeclass = np.array(raw_data["spikeclass"])
spikeclass = np.squeeze(spikeclass)
idx2 = np.empty(
    [
        len(Features[:, 0]),
    ]
)
for i in range(len(Features[:, 0])):
    if group[i] == 0:
        idx2[i] = 0
    elif group[i] == 1:
        idx2[i] = 1
    elif group[i] == 2:
        idx2[i] = 2

correct = 0
incorrect = 0

for i in range(len(Features[:, 0])):
    if idx2[i] == spikeclass[i]:
        correct = correct + 1
    elif idx2[i] != spikeclass[i]:
        incorrect = incorrect + 1

import collections

print(collections.Counter(group))
print(collections.Counter(spikeclass))
print(correct)
print(incorrect)
