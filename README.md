# ISCAS2022SpikeSortingCriteria

Details for simulation methods and results are analysis can be found at: (Link for paper)

## Instruction for using the code reproduce the results:

Dataset folder includes the 5 sets of synthetic raw extracellular recordings in matlab data format. 

Spike detection folder includes AmpThrDet which performs amplitude threshold detection on raw signal. To compare the performance of various feature extraction algorithms, the folder also includes the DetThrGT which matches the detected spikes with the ground truth (GT) labels while performing alignment, false positive detection results are removed to reduce confounding factors. 

Feature extraction folder includes files for performing the zero-crossing feature extraction and crossbar wavelet transform feature extraction. For simplicity, the extracted spikes and ground truths from the previous step are provided as matlab variables in the "extracted spikes" and "extracted spikes labels" folder. Note that the "extracted spikes" folder contains aligned and unaligned spike waveforms for "alignment requirements" evaluation. 

Classification and accuracy testing folder includes a single python file which performs K-means clustering followed by accuracy evaluation which outputs the number of correctly sorted spikes vs. number of incorrectly sorted spikes. Note that the zero-crossing feature extraction is performed in matlab, hence the extracted feature matrix needs to be saved and imported into this python file and named Features. 

