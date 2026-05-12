"""
This script runs simulations to test a bayesian model used to estimate real 
positions of recorders from their positions measured by GPS.
At each iteration it simulates a true array, add variance and bias to the
positions and try to reconstruct the true array with the model.
The model takes in input the biased simulated GPS point clouds and some
distances measured between real recorders positions.
"""

import os
import numpy as np
import pandas as pd
import pymc as pm
from scipy.optimize import minimize
from scipy.spatial import distance
import time

# Settings ====================================================================
OUTPUT = "./results/arrayReconstruction_simulationResults.csv"
GRID = False # Recorders placed in a regular grid
SEED = 123 # For reproductibility

N_SIMULATIONS = 1000 # Number of simulations
N_SAMPLES = 500 # Number of prior positions per recorder
N_FIXED_PRIORS = 2  # Nombre de priors fixés dans la grille
N_NEIGHBORS = 3 # Number of closest neighbors used for measuring distances
# N_RECORDERS = 6 # Number of recorders sinon aléatoire entre 4 et 8
MIN_RECORDERS_DISTANCE = 20 # Minimum distance between two recorders (m)
DISTANCE_ERROR = 0.3 # Expected measurement error between recorders (m)

# Parameters for array deformation (aléatoire sinon)
ARRAY_JITTER = 5
# ARRAY_ROTATION = 5
# ARRAY_X_SHIFT = 5
# ARRAY_Y_SHIFT = 0


# Functions ===================================================================
def generate_grid(width, height, spacing):
    xx, yy = np.meshgrid(np.arange(0, width * spacing, spacing),
                         np.arange(0, height * spacing, spacing)[::-1])
    return xx.ravel(), yy.ravel(), width * height

def deform_grid(x, y, jitter=0, rotation=0, shift_x=0, shift_y=0):
    coords = np.column_stack((x.astype(float), y.astype(float)))
    if jitter > 0:
        coords += np.random.normal(0, jitter, coords.shape)
    if rotation != 0:
        angle = np.deg2rad(rotation)
        center = coords.mean(axis=0)
        coords_centered = coords - center
        rotation_matrix = np.array([[np.cos(angle), -np.sin(angle)],
                                    [np.sin(angle),  np.cos(angle)]])
        coords = coords_centered @ rotation_matrix.T + center
    coords[:,0] += shift_x
    coords[:,1] += shift_y
    return coords[:,0], coords[:,1]

def create_coef_matrix(n_mics, tdoa_pairs):
    mat = np.zeros((len(tdoa_pairs), n_mics))
    for idx, (i, j) in enumerate(tdoa_pairs):
        mat[idx, i] = 1
        mat[idx, j] = -1
    return mat

def tdoa_cost(xy, array, coef_matrix, tdoa, c=340.0):
    dists = np.linalg.norm(array - xy, axis=1)
    theo_tdoa = coef_matrix @ (dists / c)
    return np.linalg.norm(tdoa - theo_tdoa)

def localize(array, tdoa, x0, y0, coef_matrix, buffer=10.0):
    bounds = [(array[:,0].min()-buffer, array[:,0].max()+buffer),
              (array[:,1].min()-buffer, array[:,1].max()+buffer)]
    res = minimize(
        tdoa_cost, (x0, y0),
        args=(array, coef_matrix, tdoa), method='L-BFGS-B', bounds=bounds)
    return res.x

def generate_measured_positions(xb, yb, sdxs, sdys, n_samples):
    return [np.stack([np.random.normal(xb[i], sdxs[i], n_samples),
                      np.random.normal(yb[i], sdys[i], n_samples)], axis=1)
            for i in range(len(xb))]

def compute_mse(est, true):
    pairs = [(i,j) for i in range(len(est)) for j in range(i+1, len(est))]
    return np.mean([np.linalg.norm(est[i]-est[j] - (true[i]-true[j])) for i,j in pairs])

def generate_points_with_min_distance(n_points, xlim=(0,50), ylim=(0,50), dmin=5):
    points = []
    attempts = 0
    max_attempts = 1000

    while len(points) < n_points and attempts < max_attempts:
        candidate = np.random.uniform([xlim[0], ylim[0]], [xlim[1], ylim[1]])
        if all(np.linalg.norm(candidate - np.array(p)) >= dmin for p in points):
            points.append(candidate)
        attempts += 1

    if len(points) < n_points:
        remaining = n_points - len(points)
        extra = np.random.uniform([xlim[0], ylim[0]], [xlim[1], ylim[1]], size=(remaining, 2))
        points.extend(extra)

    return np.array(points)[:,0], np.array(points)[:,1]

if __name__ == "__main__":

    start_timestamp = time.time()

    # Simulations ==============================================================
    if SEED:
        np.random.seed(SEED)
    for iteration in range(1, N_SIMULATIONS+1):
        print(iteration,"/",N_SIMULATIONS)

        N_RECORDERS = np.random.randint(4,8)
        
        # Real points ----------------------------------------------------------
        if GRID:
            x_real, y_real, N = generate_grid(2, 2, 25)
            real_array = np.column_stack([x_real, y_real])
            array_shape="grid"
        elif MIN_RECORDERS_DISTANCE is not None:
            x_real, y_real = generate_points_with_min_distance(
                N_RECORDERS,
                xlim=(0,50),
                ylim=(0,50),
                dmin=MIN_RECORDERS_DISTANCE)
            real_array = np.column_stack([x_real, y_real])
            array_shape="min_dist"
        else:
            x_real = np.random.uniform(0,50,N_RECORDERS)
            y_real = np.random.uniform(0,50,N_RECORDERS)
            real_array = np.column_stack([x_real, y_real])
            array_shape = "random"

        # Biased points + variance ---------------------------------------------
        array_rotation, array_x_shift, array_y_shift = np.random.uniform(-5,5,3)
        x_biased, y_biased = deform_grid(
            x_real, y_real,
            jitter=ARRAY_JITTER,
            rotation=array_rotation,
            shift_x=array_x_shift,
            shift_y=array_y_shift
        )
        sdxs, sdys = np.random.uniform(5,8,N_RECORDERS), np.random.uniform(5,8,N_RECORDERS)
        measured_positions = generate_measured_positions(x_biased, y_biased, sdxs, sdys, N_SAMPLES)

        # Measured distances ---------------------------------------------------
        if GRID:
            thresholds = [25, np.sqrt(25**2 + 25**2)]
            measured_pairs = [(i,j) for i in range(N_RECORDERS) for j in range(i+1,N)
                              if any(np.isclose(distance.euclidean(real_array[i], real_array[j]), t, atol=1e-6) for t in thresholds)]
            measured_distances = [distance.euclidean(real_array[i], real_array[j]) for i,j in measured_pairs]
        else:
            dist_matrix = distance.squareform(distance.pdist(real_array))
            measured_pairs = []
            measured_distances = []
            for i in range(N_RECORDERS):
                for j in np.argsort(dist_matrix[i])[1:N_NEIGHBORS+1]:
                    if j>i:
                        measured_pairs.append((i,j))
                        measured_distances.append(dist_matrix[i,j])
        measured_distances = np.random.normal(measured_distances, DISTANCE_ERROR)

        # Prior distributions --------------------------------------------------
        prior_array = np.array([pts.mean(axis=0) for pts in measured_positions])
        prior_stds = np.array([pts.std(axis=0) for pts in measured_positions])
        if N_FIXED_PRIORS > 0:
            fixed_indices = np.random.choice(len(prior_array), size=N_FIXED_PRIORS, replace=False)
            for idx in fixed_indices:
                prior_array[idx] = real_array[idx].copy()
                prior_stds[idx] = np.array([1.0, 1.0])

        # Bayesian estimation --------------------------------------------------
        with pm.Model() as model:
            x = pm.Normal("x", mu=prior_array[:,0], sigma=prior_stds[:,0])
            y = pm.Normal("y", mu=prior_array[:,1], sigma=prior_stds[:,1])
            for (i,j), d_obs in zip(measured_pairs, measured_distances):
                pm.Normal(f"d_{i}_{j}", mu=pm.math.sqrt((x[i]-x[j])**2 + (y[i]-y[j])**2),
                          sigma=0.5, observed=d_obs)
            trace = pm.sample(N_SAMPLES, tune=N_SAMPLES, chains=4, target_accept=0.9, random_seed=SEED)

        # Posterior checks -----------------------------------------------------
        summary = pm.summary(trace)
        max_rhat = summary["r_hat"].max()
        rhat_ok = max_rhat <= 1.01
        # effective sample size
        min_ess = summary["ess_bulk"].min()
        ess_ok = min_ess >= 200  # seuil souvent recommandé
        # divergences
        n_divergences = int(trace.sample_stats["diverging"].sum().item())
        divergences_ok = n_divergences == 0
        # min distance between two recorders
        np.fill_diagonal(dist_matrix, np.inf)
        min_distance = dist_matrix.min()
        x_posterior = trace.posterior["x"].mean(dim=("chain","draw")).values
        y_posterior = trace.posterior["y"].mean(dim=("chain","draw")).values
        sigma_posterior = np.stack([trace.posterior["x"].std(dim=("chain","draw")).values,
                              trace.posterior["y"].std(dim=("chain","draw")).values], axis=1)

        # Localization ---------------------------------------------------------
        x_sound = np.random.uniform(x_real.min(), x_real.max())
        y_sound = np.random.uniform(y_real.min(), y_real.max())
        posterior_array = np.stack([x_posterior,y_posterior],axis=1)
        toa = np.linalg.norm(np.column_stack([x_sound,y_sound])-real_array, axis=1)/340
        tdoa_pairs = [(0,i) for i in range(1,N_RECORDERS)]
        coef_matrix = create_coef_matrix(N_RECORDERS, tdoa_pairs)
        tdoa = coef_matrix @ toa
        x0, y0 = real_array.mean(axis=0)
        posterior_loc = localize(posterior_array, tdoa, x0, y0, coef_matrix)
        prior_loc = localize(prior_array, tdoa, x0, y0, coef_matrix)

        # Metrics --------------------------------------------------------------
        # recorders positions variance
        prior_mean_std = prior_stds.mean()
        posterior_mean_std = sigma_posterior.mean()
        # recorders positions mean
        prior_mse = compute_mse(prior_array, real_array)
        posterior_mse = compute_mse(posterior_array, real_array)
        # grid shifting
        prior_bias = np.linalg.norm(prior_array.mean(axis=0)-real_array.mean(axis=0))
        posterior_bias = np.linalg.norm(posterior_array.mean(axis=0)-real_array.mean(axis=0))
        # localization error
        prior_err = np.linalg.norm([x_sound,y_sound]-prior_loc)
        posterior_err = np.linalg.norm([x_sound,y_sound]-posterior_loc)

        # Saving results -------------------------------------------------------
        row = {
            "iteration": iteration,
            "prior_bias": prior_bias,
            "posterior_bias": posterior_bias,
            "bias_diff": posterior_bias - prior_bias,
            "prior_variance": prior_mean_std,
            "posterior_variance": posterior_mean_std,
            "variance_diff": posterior_mean_std - prior_mean_std,
            "prior_distances": prior_mse,
            "posterior_distances": posterior_mse,
            "configuration_diff": posterior_mse - prior_mse,
            "prior_loc_error": prior_err,
            "posterior_loc_error": posterior_err,
            "loc_error_diff": posterior_err-prior_err,
            "array_x_shift": array_x_shift,
            "array_y_shift": array_y_shift,
            "array_rotation": array_rotation,
            "n_recorders": N_RECORDERS,
            "max_rhat": max_rhat,
            "good_rhat": rhat_ok,
            "min_ess": min_ess,
            "good_ess": ess_ok,
            "n_divergences": n_divergences,
            "no_divergences": divergences_ok,
            "min_distance_between_recorders": min_distance
        }
        df = pd.DataFrame([row])
        df.to_csv(
            OUTPUT,
            mode="a",
            header=not os.path.exists(OUTPUT),
            index=False
        )

    end_timestamp = time.time()
    print(f"All ({N_SIMULATIONS}) simulations have been done in : {(end_timestamp - start_timestamp)/60:.2f} m.")
    print(f"Results are saved in {OUTPUT}")
