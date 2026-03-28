"""
This script do :

- formating of metadata of recorded sounds
- compute distances between pairs of recorders

for the field test of localization
"""

import pandas as pd
import laplace_soundscape as lps
import matplotlib.pyplot as plt
import os
import numpy as np
import subprocess
import laplace_soundscape as lps
import pandas as pd
import os
import warnings

### METADATA ###############################################################

# Process raw sound files with R (baRulho) this script creates a file with timestamps of broadcasted sounds
subprocess.call(["Rscript","./src/fieldTest_getSoundsTimestamps.R"])

points = pd.read_csv("./data/test_localisation_20250808/data.csv")
sounds = pd.read_csv("./results/aligned_sounds_20250808.csv")
sounds["utc"] = sounds["sound.files"].str.extract(r'_(\d{6})_SYNC\.WAV$')[0]
sounds["aru"] = sounds["sound.files"].str.extract(r'^([A-Z]\d)_')[0]
sounds = sounds[sounds["utc"].isin(points["utc"].astype(str))].copy()
files = os.listdir("./data/test_localisation_20250808/SYNC/")
sounds_metadata = sounds.groupby(["utc", "selec"]).agg(
    start_min=('start', 'min'),
    end_max=('end', 'max')
).reset_index()
points["utc"] = points["utc"].astype(str)
sounds_metadata["utc"] = sounds_metadata["utc"].astype(str)
sounds["utc"] = sounds["utc"].astype(str)
sounds_metadata = pd.merge(sounds_metadata, points, on="utc", how="left")
sounds_metadata = pd.merge(
    sounds_metadata,
    sounds[["utc", "selec", "sound.id", "bottom.freq", "top.freq"]].drop_duplicates(),
    on=["utc", "selec"],
    how="left"
)
col = sounds_metadata["sound.id"]
matches = col.str.extract(r'dur:(?P<duration>[\d\.]+);freq:(?P<frequency>[\d\.]+);(?P<modulation>fm|tonal)_(?P<rep>\d)')
matches["duration"] = matches["duration"].astype(float)
matches["frequency"] = matches["frequency"].astype(float)
sounds_metadata = pd.concat([sounds_metadata, matches], axis=1)
sounds_metadata = sounds_metadata.rename(columns={"bottom.freq": "bottom_freq", "top.freq": "top_freq"})
sounds_metadata = sounds_metadata.drop(columns="sound.id")

# remove sounds with 2 simulteneous diffusion points
sounds_metadata["distance"] = pd.to_numeric(sounds_metadata["distance"], errors="coerce")
sounds_metadata = sounds_metadata.dropna(subset=["distance"])
sounds_metadata = sounds_metadata.dropna(subset=["modulation"])

metadata = sounds_metadata[sounds_metadata["transect"].str.len() == 4].copy()
metadata["from"] = metadata["transect"].str[:2]
metadata["to"] = metadata["transect"].str[2:]

# save metadata
metadata.to_csv("./results/fieldTest_metadata.csv")

### DISTANCES ###########################################################################

# Compute distances from time difference of arriaval of a signal between two
# synchronised audiomoth recorders

PATH = "./data/mesures_distances_wood1_20250807/SYNC/"

# file containing extremity points of measured segments and timestamp
DATA = pd.read_csv("./data/mesures_distances_wood1_20250807/distances.csv")

files = os.listdir(PATH)

distances = {}

for i in DATA.index:
    key = (DATA.loc[i,"from"],DATA.loc[i,"to"])
    date = DATA.loc[i,"date"]
    time = DATA.loc[i,"hour"]
    hearing_files = [f for f in files if f'{date}_{time}_' in f]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        signals = lps.signal.load_signals(path = PATH, files_list=hearing_files, start=5,stop=30)
    tdoa = lps.signal.estimate_tdoa(signals=signals, plot=False)
    temp = lps.utils.guano_mean_temperature([os.path.join(PATH, f) for f in hearing_files])
    c = lps.utils.calc_speed_of_sound(temp)
    distance = lps.utils.delay_to_distance(tdoa[0]['delay'], c)
    distances[key] = distance
    print(f"Distance from {DATA.loc[i,'from']} to {DATA.loc[i,'to']} at{temp: .2f}°C: {distance: .2f}")

# Convert dictionary to DataFrame
df = pd.DataFrame(
    [(k[0], k[1], float(v)) for k, v in distances.items()],
    columns=["key1", "key2", "value"]
)

# Save to CSV
df.to_csv("./results/fieldTest_distances.csv", index=False)
