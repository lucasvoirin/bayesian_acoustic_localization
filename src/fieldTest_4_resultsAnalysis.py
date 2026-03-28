"""
This script compute summaries from localization field tests results.
"""

import pandas as pd
import numpy as np
from shapely.geometry import Point
import matplotlib.pyplot as plt

df = pd.read_csv('./results/fieldTest_results.csv')
metadata = pd.read_csv('./results/fieldTest_metadata.csv')

# Only fm
df = df[metadata['modulation']=='tonal']
metadata = metadata[metadata['modulation']=='tonal']

original_len = len(df)

filter = ~(df["max_rhat"]>1.01) & ~(df["min_ess"]<400) & (df["no_divergences"])

metadata = metadata[filter]
df = df[filter]

# number of sounds
len(df)

# Number of sounds
len(metadata["selec"].unique())

# Frequencies
metadata["frequency"].unique()

# Durations
metadata["duration"].unique()

# Distances
metadata["distance"].unique()
len(metadata["distance"].unique())

min(df["distance_target_mode"])
max(df["distance_target_mode"])

np.mean(df["distance_target_mode"])
np.std(df["distance_target_mode"])

sum(df["distance_target_mode"] <5)

sum(df["distance_target_mode"][metadata["modulation"]=="fm"] <5)/sum(metadata["modulation"]=="fm")


sum(df['distance_target_mode']<5)/len(df)

# Probability of good localization with sigma median below 0.05
total = len(df['sigma_median']<0.05)
sum(df[df['sigma_median']<0.05]['distance_target_mode']<0.5)/total

# Probability of good localization with sigma median below 0.05
total = sum(df['min_ess']>2000)
sum(df[df['min_ess']>2000]['distance_target_mode']<3)/total


# Proportion of Rhat
sum(df["rhat_y"]>=1.01)/len(df)
sum(df["rhat_x"]>=1.01)/len(df)

