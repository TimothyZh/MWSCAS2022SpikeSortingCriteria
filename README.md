# ISCAS2022SpikeSortingCriteria

Details for simulation methods and results are analysis can be found at: (Link for paper)

## Instruction for using the code reproduce the results:

Dataset folder includes the 5 sets of synthetic raw extracellular recordings in .mat data format. 

Spike detection folder includes AmpThrDet which performs amplitude threshold detection on raw signal. To compare the performance of various feature extraction algorithms, the folder also includes the DetThrGT which matches the detected spikes with the ground truth (GT) labels. Only detected spikes are only kept if it corresponds with a ground truth label are kept and false positives are removed. This is to ensure the spike sorting accuracy can be determined fairly using ground truth labels across various algorithms and confounding variables are minimized. ThrDetMaxAmpAlign.mlx and ThrDetMaxDeriAlign.mlx operate similarly to ThrDetGT, except they also perform spike alignment at the maximum amplitude and maximum derivative, respectively.

Feature extraction folder includes the code of integer filter feature extraction and crossbar wavelet transform feature extraction. For simplicity, the extracted spikes and ground truths from the previous step are provided as matlab variables in the "extracted spikes" and "extracted spikes labels" folder and can be loaded directly into the python codes using the "loadmat" function. Note that the "extracted spikes" folder contains unaligned (GTthrspike), aligned at maximum amplitude (GTthrAigned) and aligned at maximum derivative (GTthrAlignedDeri) waveforms to compare the alignment requirements for each algorithm.  

Classification and accuracy testing folder includes the Classification_Accuracy.py file which performs K-means clustering followed by accuracy evaluation which outputs the number of correctly sorted spikes vs. number of incorrectly sorted spikes. ICV.py calculates the ICV values for each cluster. The "group" variable in ICV.py refers to the output of K-means classifier in the form of a numpy array. 


## Memristor Crossbar Accuracy Simulation 


## Memristor Crossbar Power and Area Simulation

