import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

results = pd.read_csv("./results/arrayReconstruction_simulationResults.csv")
results = results[~(results["max_rhat"]>1.01) & ~(results["min_ess"] < 400) & (results["no_divergences"])]

sns.set(style="whitegrid")

COL1="tomato"
COL2="cornflowerblue"
COL3="silver"

# --- Top row: Prior vs Posterior distributions ---
fig, axes = plt.subplots(2, 3, figsize=(12, 6))

# Recorders positions
sns.kdeplot(x=results["prior_distances"], fill=True, ax=axes[0, 0], label="Prior", color=COL1, alpha=0.5, clip=(0,None))
sns.kdeplot(x=results["posterior_distances"], fill=True, ax=axes[0, 0], label="Posterior", color=COL2, alpha=0.5, clip=(0,None))
axes[0, 0].set_title("Error on recorder positions", fontsize=15, y=1.04)
axes[0, 0].set_xlabel("Mean distance from real position (m)")
axes[0, 0].legend()

# Variance
sns.kdeplot(x=results["prior_variance"], fill=True, ax=axes[0, 1], label="Prior", color=COL1, alpha=0.5, clip=(0,None))
sns.kdeplot(x=results["posterior_variance"], fill=True, ax=axes[0, 1], label="Posterior", color=COL2, alpha=0.5, clip=(0,None))
axes[0, 1].set_title("Variance on recorder positions", fontsize=15, y=1.04)
axes[0, 1].set_xlabel("Mean standard deviation (m)")
axes[0, 1].legend()

# Barycentre
sns.kdeplot(x=results["prior_bias"], fill=True, ax=axes[0, 2], label="Prior", color=COL1, alpha=0.5, clip=(0,None))
sns.kdeplot(x=results["posterior_bias"], fill=True, ax=axes[0, 2], label="Posterior", color=COL2, alpha=0.5, clip=(0,None))
axes[0, 2].set_title("Error on the array barycenter", fontsize=15, y=1.04)
axes[0, 2].set_xlabel("Distance from real position (m)")
axes[0, 2].legend()

# --- Bottom row: differences ---
sns.kdeplot(x=results["configuration_diff"], fill=True, ax=axes[1, 0], color=COL3)
axes[1, 0].set_xlabel("Difference (m)")

sns.kdeplot(x=results["variance_diff"], fill=True, ax=axes[1, 1], color=COL3)
axes[1, 1].set_xlabel("Difference (m)")

sns.kdeplot(x=results["bias_diff"], fill=True, ax=axes[1, 2], color=COL3)
axes[1, 2].set_xlabel("Difference (m)")

for ax in axes.flat:
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)

plt.subplots_adjust(wspace=0)
plt.tight_layout()
plt.savefig("./results/figures/arrayReconstruction_arrayMetrics.png", dpi=300, bbox_inches="tight")
# plt.show()
