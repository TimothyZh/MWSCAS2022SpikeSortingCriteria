# Toward A Streamlined Approach for Spike Sorting Algorithms and Hardware Evaluation
Spike sorting algorithms are used to separate extracellular recordings of neuronal populations into single-unit spike activities. The development of customized hardware implementations implementing spike sorting algorithms is burgeoning, however, there lacks a standardized set of criteria for evaluation to facilitate direct comparison of both software and hardware implementations in the literature. This can be largely attributed to the lack of publicly available labelled datasets. In this paper, we propose a standardized set of criteria for evaluating spikesorting algorithms and processors, using five publicly available datasets. We present a benchmark for future comparison, and use our criteria to evaluate a simulated Resistive Random-Access Memory (RRAM) In-Memory Computing (IMC) system using the Discrete Wavelet Transform (DWT) for feature extraction. Our system consumes approximately (per channel) 10.72mW and occupies an area of 0.66mm2 in a 22nm FDSOI Complementary Metal–Oxide–Semiconductor (CMOS) process.

## Instruction for using the code reproduce the results:
Dataset folder includes the 5 sets of synthetic raw extracellular recordings in .mat data format. 

Spike detection folder includes AmpThrDet which performs amplitude threshold detection on raw signal. To compare the performance of various feature extraction algorithms, the folder also includes the DetThrGT which matches the detected spikes with the ground truth (GT) labels. Only detected spikes are only kept if it corresponds with a ground truth label are kept and false positives are removed. This is to ensure the spike sorting accuracy can be determined fairly using ground truth labels across various algorithms and confounding variables are minimized. ThrDetMaxAmpAlign.mlx and ThrDetMaxDeriAlign.mlx operate similarly to ThrDetGT, except they also perform spike alignment at the maximum amplitude and maximum derivative, respectively.

Feature extraction folder includes the code of integer filter feature extraction and crossbar wavelet transform feature extraction, as well as crossbar accuracy, power, area and latency simulation associated with our proposed wavelet crossbar implementation. For simplicity, the extracted spikes and ground truths from the previous step are provided as matlab variables in the "extracted spikes" and "extracted spikes labels" folder and can be loaded directly into the python codes using the "loadmat" function. Note that the "extracted spikes" folder contains unaligned (GTthrspike), aligned at maximum amplitude (GTthrAigned) and aligned at maximum derivative (GTthrAlignedDeri) waveforms to compare the alignment requirements for each algorithm.  

Classification and accuracy testing folder includes the Classification_Accuracy.py file which performs K-means clustering followed by accuracy evaluation which outputs the number of correctly sorted spikes vs. number of incorrectly sorted spikes. ICV.py calculates the ICV values for each cluster. The "group" variable in ICV.py refers to the output of K-means classifier in the form of a numpy array. 


## Memristor Crossbar Accuracy, Power and Area Simulation 
This study uses a semi-passive crossbar model proposed by Primeau et al. 2021[28], which is based on existing semi-passive crossbar models [26], [29]. This model accounts for a variety of device non-idealities.
The parameters for accuracy simulations are as follows: 
- Wordline(WL) resistance: 20Ω
- Bitline(BL) resistance: 20Ω
- Size of crossbar: 64 by 64
- Size of tile: 8 by 8 
- Voltage Supplied (Vdd): 0.2V
- DAC resolution: 4 bits
- ADC resolution: 14 bits 
- CMOS line resistance: 600Ω
- CMOS transistor resistance: 20Ω
- R_on (High resistive state): 1e4 
- R_off (Low resistive state): 1e5 
- Bias Scheme: 1/3 bias scheme (unselected WLs biased to Vdd/3, unselected BLs biased to 2Vdd/3)
- Probability of memristor stuck on High resistive state: 0.01
- Probability of memristor stuck on Low resistive state: 0.01

The parameters for power consumption simulation:
- RRAM cell area: 1e-14
- RRAM cell read voltage: 0.2V
- RRAM cell read latency: 6e-9s 
- DAC area: 0.05e-6
- DAC power: 2e-4W
- DAC frequency: 100e6 Hz
- ADC area: 1.1e-3 by 0.6e-3
- ADC power: 10e-3W
- ADC frequency: 10e6 Hz

