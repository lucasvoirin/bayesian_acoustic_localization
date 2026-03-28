"""
This script perform bayesian acoustic localisation for each sound broadcasted during the field test.
The shape of the array is imported from the previous script ("./fieldTest_2_arrayReconstruction.py").
"""

import pandas as pd
import laplace_soundscape as lps
import matplotlib.pyplot as plt
import os
import numpy as np
import pymc as pm
import arviz as az
from shapely.geometry import Point
import time

array = lps.array.ArrayReconstruction.load("./results/fieldTest_array")
metadata = pd.read_csv("./results/fieldTest_metadata.csv")

TARGET_EPSG = array.epsg
PATH = "../../Data/test_localisation_20250808/SYNC/"
FILES = os.listdir(PATH)
RECORDERS = ["A1", "A2", "A3", "B1", "C1", "C2", "D1", "D2"]
TIME_BUFFER = 0.5
OUTPUT="./results/fieldTest_results.csv"

# Centering array coordinates
posterior_hearing_array = array.posterior_points.loc[array.posterior_points.index.isin(RECORDERS)]
X_ref_location = posterior_hearing_array["x"].mean()
Y_ref_location = posterior_hearing_array["y"].mean()
posterior_hearing_array.loc[:,"x"] -= X_ref_location
posterior_hearing_array.loc[:,"y"] -= Y_ref_location

n = len(metadata)
# n = 3 # for debug

start_timestamp = time.time()

for i in range(n):

    print(f'{i+1}/{n}')

    from_point = metadata.loc[i,"from"]
    to_point = metadata.loc[i,"to"]
    distance = float(metadata.loc[i,"distance"])
    point_posterior_array = lps.utils.point_along_line(
        array.posterior_points,
        [from_point,to_point],
        distance
    )
    i_files = lps.utils.get_files_metadata(FILES, metadata, i)

    hearing_files = [f for f in i_files if f.split("_")[0] in RECORDERS and not f.lower().endswith(".txt")]

    temperature = lps.utils.guano_mean_temperature([os.path.join(PATH,f) for f in hearing_files])
    sound_speed = lps.utils.calc_speed_of_sound(temperature)

    start = metadata.loc[i,"start_min"] - TIME_BUFFER
    stop = metadata.loc[i,"end_max"] + TIME_BUFFER

    metadata.loc[i]

    signals = lps.signal.load_signals(path=PATH, files_list=hearing_files, start=start, stop=stop)
    retards = lps.signal.estimate_tdoa(signals, plot = False, pdf_path="./results/retards.pdf")
    sigmas = [r["cc_peak_width"] for r in retards]
    coef_matrix_pt, tdoa = lps.signal.compute_coef_matrix(retards)

    posterior_trace = lps.spatial.sample_posterior_localization(
        array=np.array(posterior_hearing_array),
        coef_matrix=coef_matrix_pt,
        tdoa=tdoa,
        buffer=10,
        iterations=800,
        sigma=sigmas,
        c=sound_speed,
        method="TDOA"
    )
    posterior_samples = az.extract(posterior_trace, var_names=["x", "y"]).to_dataframe()
    summary = az.summary(posterior_trace, var_names=["x","y"])

    # Posterior checks
    summary = pm.summary(posterior_trace)
    # r hat
    max_rhat = summary["r_hat"].max()
    rhat_ok = max_rhat <= 1.01
    # effective sample size
    min_ess = summary["ess_bulk"].min()
    ess_ok = min_ess >= 200
    # divergences
    n_divergences = int(posterior_trace.sample_stats["diverging"].sum().item())
    divergences_ok = n_divergences == 0

    # Using SpatialPosterior class 
    spatial_posterior = lps.spatial.SpatialPosterior(posterior_samples.x, posterior_samples.y, TARGET_EPSG)

    mode = spatial_posterior.mode()
    target = Point(
        point_posterior_array[0]-X_ref_location,
        point_posterior_array[1]-Y_ref_location
    )
    distance_mode_target = mode.distance(target)

    # Save informations --------------------------------------------------------
    sigmas = [float(sigma) for sigma in sigmas]
    posterior = summary.to_dict()
    rhat_x = posterior["r_hat"]["x"] if "r_hat" in posterior else np.nan
    rhat_y = posterior["r_hat"]["y"] if "r_hat" in posterior else np.nan
    mode = Point([mode.x, mode.y])
    target = Point([target.x, target.y])
    dist = mode.distance(target)
    row = {
        "i": i,
        "sigma_min": np.min(sigmas),
        "sigma_max": np.max(sigmas),
        "sigma_mean": np.mean(sigmas),
        "sigma_median": np.median(sigmas),
        "rhat_x": rhat_x,
        "rhat_y": rhat_y,
        "distance_target_mode": dist,
        "within_hdi_01": int(target.within(spatial_posterior.hdi(0.01)).loc[0,"geometry"]),
        "within_hdi_05": int(target.within(spatial_posterior.hdi(0.05)).loc[0,"geometry"]),
        "within_hdi_25": int(target.within(spatial_posterior.hdi(0.25)).loc[0,"geometry"]),
        "within_hdi_50": int(target.within(spatial_posterior.hdi(0.50)).loc[0,"geometry"]),
        "within_hdi_75": int(target.within(spatial_posterior.hdi(0.75)).loc[0,"geometry"]),
        "within_hdi_99": int(target.within(spatial_posterior.hdi(0.99)).loc[0,"geometry"]),
        "area_hdi_50": float(spatial_posterior.hdi(0.50).area.values[0]),
        "area_hdi_99": float(spatial_posterior.hdi(0.99).area.values[0]),
        "max_rhat": max_rhat,
        "good_rhat": rhat_ok,
        "min_ess": min_ess,
        "good_ess": ess_ok,
        "n_divergences": n_divergences,
        "no_divergences": divergences_ok,
    }
    df = pd.DataFrame([row])
    df.to_csv(
        OUTPUT,
        mode="a",
        header=not os.path.exists(OUTPUT),
        index=False
    )

end_timestamp = time.time()
print(f"All {n} sounds have been localized in : {(end_timestamp - start_timestamp)/60:.2f} m.")
print(f"Results have been saved in {OUTPUT}.")
