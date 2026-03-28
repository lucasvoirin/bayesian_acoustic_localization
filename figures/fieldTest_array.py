import pandas as pd
import numpy as np
from shapely.geometry import Point
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import laplace_soundscape as lps

# ---------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------
array = lps.array.ArrayReconstruction.load("./results/fieldTest_array")
metadata = pd.read_csv("./results/fieldTest_metadata.csv")

transect_distances = metadata["distance"].unique()

# ---------------------------------------------------------------------
# Figure and colors
# ---------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(6, 6), facecolor="white")

COL_PRIOR = "tomato"
COL_POST = "cornflowerblue"

def flat_alpha(color, background="white", alpha=0.5):
    fg = mcolors.to_rgb(color)
    bg = mcolors.to_rgb(background)
    return tuple((1 - alpha) * bg[i] + alpha * fg[i] for i in range(3))

COL_POST_POINTS = flat_alpha(COL_POST, alpha=0.6)

# ---------------------------------------------------------------------
# Posterior trace cloud
# ---------------------------------------------------------------------
ax.scatter(
    array.trace.posterior["x"],
    array.trace.posterior["y"],
    edgecolors="none",
    c=COL_POST_POINTS,
    alpha=0.2
)

# ---------------------------------------------------------------------
# Prior → posterior displacement vectors
# ---------------------------------------------------------------------
for x_post, y_post, x_prior, y_prior in zip(
    array.posterior_points["x"],
    array.posterior_points["y"],
    array.prior_points["x"],
    array.prior_points["y"]
):
    ax.plot(
        [x_prior, x_post],
        [y_prior, y_post],
        linestyle="--",
        color="silver",
        alpha=0.8,
        zorder=1
    )

# ---------------------------------------------------------------------
# Transect
# ---------------------------------------------------------------------
x1 = array.posterior_points["x"]["C2"]
y1 = array.posterior_points["y"]["C2"]

x2, y2 = lps.utils.point_along_line(
    array.posterior_points,
    ["C2", "D1"],
    60
)

ax.plot([x1, x2], [y1, y2], c="grey", alpha=0.7, zorder=10)

for i in transect_distances:
    x_t, y_t = lps.utils.point_along_line(
        array.posterior_points,
        ["C2", "D1"],
        i
    )
    ax.scatter(
        x_t,
        y_t,
        c="dimgrey",
        marker="+",
        label="Broadcasting positions" if i == 10 else None,
        zorder=11
    )

# ---------------------------------------------------------------------
# Mean positions
# ---------------------------------------------------------------------
ax.scatter(
    array.posterior_points["x"],
    array.posterior_points["y"],
    c=COL_POST,
    label="Mean posterior positions",
    zorder=3
)

ax.scatter(
    array.prior_points["x"],
    array.prior_points["y"],
    c=COL_PRIOR,
    label="Mean prior positions",
    zorder=4
)

# ---------------------------------------------------------------------
# Axis limits (clean & correct)
# ---------------------------------------------------------------------
margin = 10

xmin = array.prior_points["x"].min() - margin
xmax = array.prior_points["x"].max() + margin
ymin = array.prior_points["y"].min() - margin
ymax = array.prior_points["y"].max() + margin

ax.set_xlim(xmin, xmax)
ax.set_ylim(ymin, ymax)

# ---------------------------------------------------------------------
# Labels & styling
# ---------------------------------------------------------------------
ax.set_xlabel("Easting (m)", fontsize=12)
ax.set_ylabel("Northing (m)", fontsize=12)

ax.legend(frameon=True, fontsize=9)
ax.grid(True, linestyle="--", alpha=0.4)
ax.set_aspect("equal")

fig.tight_layout()

# ---------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------
fig.savefig(
    "./results/figures/fieldTest_array.png",
    dpi=300,
    bbox_inches="tight"
)

# plt.show()
