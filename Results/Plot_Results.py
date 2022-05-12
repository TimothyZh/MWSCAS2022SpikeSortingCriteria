import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial"]
plt.rcParams["figure.figsize"] = (30, 8)
plt.rcParams.update({"font.size": 16})
plt.rcParams["axes.linewidth"] = 2
color_palette = ["#6cbdde", "#FA233E"]

fig, ax = plt.subplots(1, 3)
int_filter = pd.read_csv("int_filter.csv")
df = pd.DataFrame(columns=["Alignment", "Accuracy (%)"])
for idx, row in int_filter.iterrows():
    for i in range(1, 6):
        df = df.append(
            {
                "Alignment": row["Alignment"],
                "Method": "Integer Filter",
                "Accuracy (%)": row["Dataset %d" % i] * 100,
            },
            ignore_index=True,
        )

wavelet = pd.read_csv("wavelet.csv")
for idx, row in wavelet.iterrows():
    for i in range(1, 6):
        df = df.append(
            {
                "Alignment": row["Alignment"],
                "Method": "Wavelet",
                "Accuracy (%)": row["Dataset %d" % i] * 100,
            },
            ignore_index=True,
        )

df.loc[df["Alignment"] == "Max Amplitude Alignment", "Alignment"] = "Max Amplitude"
df.loc[df["Alignment"] == "Max Derivative Alignment", "Alignment"] = "Max Derivative"
df.loc[df["Alignment"] == "No Alignment", "Alignment"] = "None"
sns.boxplot(
    data=df,
    x="Alignment",
    y="Accuracy (%)",
    hue="Method",
    showfliers=True,
    palette=color_palette,
    ax=ax[0],
)
ax[0].set_ylim([70, 101])
ax[0].xaxis.grid(True, which="both")

SNR= pd.read_csv("SNR.csv")
SNR['Accuracy (%)'] = SNR['Accuracy'] * 100

sns.lineplot(
    data=SNR,
    x="SNR",
    y="ICV (Weighted)",
    hue="Method",
    style="Method",
    linewidth=2,
    markers=True,
    dashes=False,
    ms=25,
    palette=color_palette,
    ax=ax[1],
)
ax[1].grid(axis="both")

sns.lineplot(
    data=SNR,
    x="SNR",
    y="Accuracy (%)",
    hue="Method",
    style="Method",
    linewidth=2,
    markers=True,
    dashes=False,
    ms=25,
    palette=color_palette,
    ax=ax[2],
)
ax[2].set_ylim([80, 101])
ax[2].grid(axis="both")

print(pearsonr(SNR["ICV (Weighted)"], SNR["Accuracy (%)"]))
plt.show()
