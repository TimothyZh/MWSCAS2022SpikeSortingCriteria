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

ICV = pd.read_csv("ICV.csv")
df = pd.DataFrame(columns=["Method", "Dataset", "Accuracy (%)", "ICV (Weighted)"])
for idx, row in ICV.iterrows():
    for i in range(1, 6):
        df = df.append(
            {
                "Method": row["Method"],
                "Dataset": i,
                "ICV (Weighted)": row["Dataset %d" % i],
            },
            ignore_index=True,
        )

df.loc[df["Method"] == "wavelet", "Method"] = "Wavelet"
df.loc[df["Method"] == "int_filter", "Method"] = "Integer Filter"
for idx, row in wavelet.iterrows():
    for i in range(1, 6):
        df.loc[(df["Method"] == "Wavelet") & (df["Dataset"] == i), "Accuracy (%)"] = (
            row["Dataset %d" % i] * 100
        )

for idx, row in int_filter.iterrows():
    for i in range(1, 6):
        df.loc[
            (df["Method"] == "Integer Filter") & (df["Dataset"] == i), "Accuracy (%)"
        ] = (row["Dataset %d" % i] * 100)


ax_left = ax[1]
ax_right = ax[1].twinx()
print(pearsonr(df["ICV (Weighted)"], df["Accuracy (%)"]))


sns.barplot(
    data=df,
    x="Dataset",
    y="ICV (Weighted)",
    hue="Method",
    palette=color_palette,
    linewidth=1,
    edgecolor="k",
    ax=ax_left,
)
sns.barplot(
    data=df,
    x="Dataset",
    y="Accuracy (%)",
    hue="Method",
    hatch="xx",
    palette=color_palette,
    linewidth=1,
    edgecolor="k",
    ax=ax_right,
)

width_scale = 0.5
offset = 0.01
for bar in ax_left.containers[0]:
    bar.set_width(bar.get_width() * width_scale)

for bar in ax_left.containers[1]:
    bar.set_width(bar.get_width() * width_scale)

for idx, bar in enumerate(ax_right.containers[0]):
    bar.set_width(bar.get_width() * width_scale)
    x = ax_left.containers[0][idx].get_x()
    bar.set_x(x + (2 * bar.get_width() * width_scale) - 2 * offset)

for idx, bar in enumerate(ax_right.containers[1]):
    bar.set_width(bar.get_width() * width_scale)
    x = ax_left.containers[1][idx].get_x()
    bar.set_x(x + (2 * bar.get_width() * width_scale) + 2 * offset)

for bar in ax_left.containers[0]:
    x = bar.get_x()
    bar.set_x(x - 3 * offset)

ax_left.set_ylim([35, 50])
ax_right.set_ylim([75.75, 100])
ax_right.set_ylabel("")
ax[1].xaxis.grid(True, which="both")
ax[1].set_axisbelow(True)

noise = pd.read_csv("noise.csv")
noise_levels = [4, 3, 2]
df = pd.DataFrame(columns=["Method", "Noise (dB)", "Accuracy (%)"])
for idx, row in noise.iterrows():
    for i in range(1, 4):
        df = df.append(
            {
                "Method": row["Method"],
                "SNR": noise_levels[i - 1],
                "Accuracy (%)": row["Noise Level %i" % i] * 100,
            },
            ignore_index=True,
        )

df.loc[df["Method"] == "wavelet", "Method"] = "Wavelet"
df.loc[df["Method"] == "int_filter", "Method"] = "Integer Filter"
sns.lineplot(
    data=df,
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
# exit(0)

plt.show()
