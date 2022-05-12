"""
simulation_1 -- simulation_5 files were used to construct the dataset.

These were originally presented in Ref. [1], and were previously made available at:
http://www2.le.ac.uk/departments/engineering/research/bioengineering/neuroengineering-lab/software

The Synthetic Simulations Of Extracellular Recordings (SSOER) dataset is licensed under a 
Creative Commons Attribution 4.0 International Licence. Consequently, when 
using or making modifications to this dataset, in addition to citing [2], 
it is necessary to cite [1].

[1] J. Martinez, C. Pedreira, M. J. Ison, and R. Quian Quiroga, 
“Realistic simulation of extracellular recordings,” Journal of Neuroscience Methods, 
vol. 184, no. 2, pp. 285–293, Nov. 2009, doi: 10.1016/j.jneumeth.2009.08.017.

[2] T. Zhang, C. Lammie, Amirali Amirsoleimani, M. Ahmadi, Mostafa Rahimi Azghadi, and R. Genov,
“Synthetic Simulations Of Extracellular Recordings (SSOER) Dataset,” Zenodo, 
Mar. 2022, doi: 10.5281/zenodo.6214550.
"""


import numpy as np
import pandas as pd
from scipy.io import loadmat


sims = ['simulation_1.mat', 'simulation_2.mat', 'simulation_3.mat', 'simulation_4.mat', 'simulation_5.mat']
amlitudes = [4, 4, 2, 2, 3] # Taken from [1]
firing_rates = [1, 5, 5, 5, 0.5] # Taken from [1]
df = pd.DataFrame(columns=['spike_timestep', 'spike_class', 'amplitude', 'firing_rate'])
data = np.array([])
global_duration = 0.
for sim_idx, sim in enumerate(sims):
    sim = loadmat(sim)
    sim_df = pd.DataFrame(columns=['spike_timestep', 'spike_class'])
    sim_df['spike_timestep'] = sim['spike_times'].flatten()[0][0] + global_duration
    sim_df['spike_class'] = sim['spike_class'].flatten()[0][0]
    sim_df['amplitude'] = amlitudes[sim_idx]
    sim_df['firing_rate'] = firing_rates[sim_idx]
    data = np.concatenate((data, sim['data'].flatten()))
    global_duration += len(sim['data'].flatten())
    df = df.append(sim_df)

df.to_csv('labels.csv', index=False)
np.save('data.npy', data)
