import numpy as np

# Calculate mean waveform template
group0wave = []
group1wave = []
group2wave = []

# Group refers to the output variable from either feature extraction algorithms
for i in range(group.shape[0]):
    if group[i] == 0:
        group0wave.append(GTaligned[i])
    elif group[i] == 1:
        group1wave.append(GTaligned[i])
    elif group[i] == 2:
        group2wave.append(GTaligned[i])

group0wave = np.array(group0wave)
group1wave = np.array(group1wave)
group2wave = np.array(group2wave)
group0mean = np.mean(group0wave, axis=0)
group1mean = np.mean(group1wave, axis=0)
group2mean = np.mean(group2wave, axis=0)

# ICV
sum0 = 0
sum1 = 0
sum2 = 0
for i in range(group.shape[0]):
    if group[i] == 0:
        sum0 = sum0 + np.linalg.norm(GTaligned[i] - group0mean)
    elif group[i] == 1:
        sum1 = sum1 + np.linalg.norm(GTaligned[i] - group1mean)
    elif group[i] == 2:
        sum2 = sum2 + np.linalg.norm(GTaligned[i] - group2mean)

ICV0 = sum0 / group0wave.shape[0]
ICV1 = sum1 / group1wave.shape[0]
ICV2 = sum2 / group2wave.shape[0]
print(ICV0)
print(ICV1)
print(ICV2)
