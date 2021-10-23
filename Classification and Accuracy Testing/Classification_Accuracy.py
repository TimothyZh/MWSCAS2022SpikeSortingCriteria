import torch
import numpy as np
import itertools
import time
import matplotlib.pyplot as plt
import collections
import random
import os
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from scipy.io import loadmat
import collections


# Features variable refers to the n by 2 matrix obtained from feature extraction, where n is the number of spikes and 2 features are associated with each spike.
def det_classification_accuracy(features, extracted_spike_labels_path='../FeatureExtraction/Extracted Spike Labels/GTthr1.mat'):
    # K-means
    kmeans = KMeans(n_clusters=3, max_iter=1000).fit(features)
    group = kmeans.labels_
    pc11 = features[:, 0]
    pc22 = features[:, 1]
    cdict = {0: "red", 1: "blue", 2: "green"}
    _, ax = plt.subplots()
    for g in np.unique(group):
        ix = np.where(group == g)
        ax.scatter(pc11[ix], pc22[ix], c=cdict[g], label=g, s=10)

    ax.legend()
    plt.show()
    # Gaussian mixture model
    gmm = GaussianMixture(n_components=3)
    gmm.fit(features)
    group = gmm.predict(features)
    pc11 = features[:, 0]
    pc22 = features[:, 1]
    cdict = {0: "red", 1: "blue", 2: "green"}
    _, ax = plt.subplots()
    for g in np.unique(group):
        ix = np.where(group == g)
        ax.scatter(pc11[ix], pc22[ix], c=cdict[g], label=g, s=10)

    ax.legend()
    plt.show()
    # Accuracy testing
    raw_data = loadmat(extracted_spike_labels_path)
    spikeclass = np.array(raw_data["spikeclass"])
    spikeclass = np.squeeze(spikeclass)
    idx2 = np.empty(
        [
            len(features[:, 0]),
        ]
    )
    for i in range(len(features[:, 0])):
        if group[i] == 0:
            idx2[i] = 0
        elif group[i] == 1:
            idx2[i] = 1
        elif group[i] == 2:
            idx2[i] = 2

    correct = 0
    incorrect = 0
    for i in range(len(features[:, 0])):
        if idx2[i] == spikeclass[i]:
            correct = correct + 1
        elif idx2[i] != spikeclass[i]:
            incorrect = incorrect + 1

    return collections.Counter(group), collections.Counter(spikeclass), correct, incorrect
