import numpy as np
import pandas as pd
import pymc as pm
from scipy.optimize import minimize
from scipy.spatial import distance
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

# Settings ====================================================================
GRID = False # params.GRID # Recorders placed in a regular grid
SEED = 666 # For reproductibility

N_SAMPLES = 500# params.N_SAMPLES # Number of prior positions per recorder
N_FIXED_PRIORS = 2 #params.N_FIXED_PRIORS  # par exemple
N_NEIGHBORS = 3 # params.N_NEIGHBORS # Number of closest neighbors used for measuring distances
N_RECORDERS = 6 # Number of recorders

DISTANCE_ERROR = 0.3# params.DISTANCE_ERROR # Expected measurement error between recorders

# Parameters for array deformation
ARRAY_JITTER = 5 # params.ARRAY_JITTER
# ARRAY_ROTATION = 5
# ARRAY_X_SHIFT = 5
# ARRAY_Y_SHIFT = 0

MIN_RECORDERS_DISTANCE = 10

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
    max_attempts = 10000

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


if SEED:
    np.random.seed(SEED)
# Simulation ==================================================================

if GRID:
    x_real, y_real, N = generate_grid(2, 2, 25)
    real_array = np.column_stack([x_real, y_real])
    array_shape="grid"
elif MIN_RECORDERS_DISTANCE is not None:
    x_real, y_real = generate_points_with_min_distance(
        N_RECORDERS,
        xlim=(0,70),
        ylim=(0,70),
        dmin=MIN_RECORDERS_DISTANCE)
    real_array = np.column_stack([x_real, y_real])
    array_shape="min_dist"
else:
    x_real = np.random.uniform(0,50,N_RECORDERS)
    y_real = np.random.uniform(0,50,N_RECORDERS)
    real_array = np.column_stack([x_real, y_real])
    array_shape = "random"

# Biased points + variance ------------------------------------------------
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

# Measured distances ------------------------------------------------------
if GRID:
    thresholds = [25, np.sqrt(25**2 + 25**2)]
    measured_pairs = [(i,j) for i in range(N_RECORDERS) for j in range(i+1,N_RECORDERS)
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

# Prior distributions -----------------------------------------------------
prior_array = np.array([pts.mean(axis=0) for pts in measured_positions])
prior_stds = np.array([pts.std(axis=0) for pts in measured_positions])
if N_FIXED_PRIORS > 0:
    fixed_indices = np.random.choice(len(prior_array), size=N_FIXED_PRIORS, replace=False)
    for idx in fixed_indices:
        prior_array[idx] = real_array[idx].copy()
        prior_stds[idx] = np.array([1.0, 1.0])

# Bayesian estimation -----------------------------------------------------
with pm.Model() as model:
    x = pm.Normal("x", mu=prior_array[:,0], sigma=prior_stds[:,0])
    y = pm.Normal("y", mu=prior_array[:,1], sigma=prior_stds[:,1])
    for (i,j), d_obs in zip(measured_pairs, measured_distances):
        pm.Normal(f"d_{i}_{j}", mu=pm.math.sqrt((x[i]-x[j])**2 + (y[i]-y[j])**2),
                  sigma=0.5, observed=d_obs)
    trace = pm.sample(N_SAMPLES, tune=N_SAMPLES, chains=4, target_accept=0.9, random_seed=SEED)

summary = pm.summary(trace)
max_rhat = summary["r_hat"].max()
rhat_ok = max_rhat <= 1.01

x_posterior = trace.posterior["x"].mean(dim=("chain","draw")).values
y_posterior = trace.posterior["y"].mean(dim=("chain","draw")).values
sigma_posterior = np.stack([trace.posterior["x"].std(dim=("chain","draw")).values,
                      trace.posterior["y"].std(dim=("chain","draw")).values], axis=1)

# Localization ------------------------------------------------------------
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


# graphique
def flat_alpha(color, background="white", alpha=0.5):
    fg = mcolors.to_rgb(color)
    bg = mcolors.to_rgb(background)
    return tuple((1 - alpha) * bg[i] + alpha * fg[i] for i in range(3))

plt.figure(figsize=(6, 6), facecolor="white")

COL_TRUE = "dimgrey"
COL_PRIOR = "tomato"
COL_POST = "cornflowerblue"
COL_PRIOR_POINTS = flat_alpha(COL_PRIOR, alpha=0.6)
COL_POST_POINTS  = flat_alpha(COL_POST, alpha=0.6)

for i in range(N_RECORDERS):
    if i in fixed_indices:
        continue
    df = measured_positions[i]
    plt.scatter(df[:,0], df[:,1], s=6, c=[COL_PRIOR_POINTS], edgecolors="none", alpha=0.2)

plt.scatter(trace.posterior["x"], trace.posterior["y"], s=6, c=[COL_POST_POINTS], edgecolors="none", alpha=0.2)

# Positions des enregistreurs
plt.scatter(x_real, y_real, c=COL_TRUE,marker = "D", label="True positions", s=100, edgecolors="white", linewidths=.3)
for i, (x, y) in enumerate(zip(x_real, y_real), start=1):
    plt.text(x-2, y+2, str(i), color="dimgrey", fontsize=9,
             ha="center", va="center", fontweight="bold")

plt.scatter(prior_array[:, 0], prior_array[:, 1], label="Mean prior positions", 
            c=COL_PRIOR, marker="X", s=50,linewidths=.3, edgecolors="white")
plt.scatter(posterior_array[:,0], posterior_array[:,1], label="Mean posterior positions", 
            c=COL_POST, marker="P", s=50,linewidths=.3, edgecolors="white")

# Sources sonores
plt.scatter(x_sound, y_sound, label="True sound source", marker="H" ,s=100, c=COL_TRUE)
plt.scatter(prior_loc[0], prior_loc[1], label="Prior sound source", 
            marker="*", s=180, c=COL_PRIOR, edgecolors="white",linewidths=.5)
plt.scatter(posterior_loc[0], posterior_loc[1], label="Posterior sound source", 
            marker="*", s=180, c=COL_POST, edgecolors="white",linewidths=.5 )

plt.xlabel("Easting (m)", fontsize=12)
plt.ylabel("Northing (m)", fontsize=12)

plt.legend(frameon=True, fontsize=9)
plt.grid(True, linestyle="--", alpha=0.4)
plt.axis("equal")
plt.tight_layout()

plt.savefig("./results/figures/arrayReconstruction_arrayExample.png", dpi=300, bbox_inches="tight")
# plt.show()
