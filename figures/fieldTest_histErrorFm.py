import pandas as pd
import numpy as np
from shapely.geometry import Point
import matplotlib.pyplot as plt

df = pd.read_csv('./results/fieldTest_results.csv')
metadata = pd.read_csv('./results/fieldTest_metadata.csv')

# Only fm
df = df[metadata['modulation']=='fm']
metadata = metadata[metadata['modulation']=='fm']

# Remove MCMC sampling problems
metadata = metadata[~(df["max_rhat"]>1.01) & ~(df["min_ess"]<400) & (df["no_divergences"])]
df = df[~(df["max_rhat"]>1.01) & ~(df["min_ess"]<400) & (df["no_divergences"])]

fig, ax = plt.subplots(figsize=(9,6))
ax.hist(
    df["distance_target_mode"],
    bins=30,
    color="silver"
)
plt.grid(True, linestyle="--", alpha=0.4)
ax.set_xlabel("Distance from real position (m)")
ax.set_ylabel("Frequency")

plt.savefig("./results/figures/fieldTest_histErrorFm.png", dpi=300, bbox_inches="tight")
# plt.show()
