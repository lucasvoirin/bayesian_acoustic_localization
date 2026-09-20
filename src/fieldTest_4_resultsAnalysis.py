"""
This script compute summaries from localization field tests results.
"""

import pandas as pd
import numpy as np
from shapely.geometry import Point
import matplotlib.pyplot as plt

df = pd.read_csv('./results/fieldTest_results.csv')
metadata = pd.read_csv('./results/fieldTest_metadata.csv')

# keep only fm
df = df[metadata['modulation']=='fm']
metadata = metadata[metadata['modulation']=='fm']

len_fm = len(df)

# Remove MCMC sampling problems
metadata = metadata[~(df["max_rhat"]>1.01) & ~(df["min_ess"]<400) & (df["no_divergences"])]
df = df[~(df["max_rhat"]>1.01) & ~(df["min_ess"]<400) & (df["no_divergences"])]

len_fm_ok = len(df)

min_err = min(df["distance_target_mode"])
max_err = max(df["distance_target_mode"])

avg_err = np.mean(df["distance_target_mode"])
std_err np.std(df["distance_target_mode"])

numb_under_err_5m = sum(df["distance_target_mode"] <5)

prop_under_err_5m = sum(df['distance_target_mode']<5)/len_fm_ok

print(f"Number of frequency modulated sounds: {len_fm}")
print(f"Number of frequency modulated sounds without sampling problems: {len_fm_ok}")
print(f"Minimum distance error: {min_err:.4f}")
print(f"Maximum distance error: {max_err:.4f}")
print(f"Average distance error: {avg_err:.4f}")
print(f"St.Dev. distance error: {std_err:.4f}")
print(f"Number of sounds under distance error of 5m: {numb_under_err_5m}/{len_fm_ok}")
print(f"Proportion of sounds under distance error of 5m: {numb_under_err_5m:.4f}")
