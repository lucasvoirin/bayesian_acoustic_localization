import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

results = pd.read_csv("./results/arrayReconstruction_simulationResults.csv")

results = results[~(results["max_rhat"]>1.01) & ~(results["min_ess"] < 400) & (results["no_divergences"])]

# sns.set(style="whitegrid")
plt.style.use("seaborn-v0_8-talk")
plt.style.use("seaborn-v0_8-whitegrid")

COL1="tomato"
COL2="cornflowerblue"
COL3="silver"

# --- Localization performance ---
fig, axes = plt.subplots(1, 2, figsize=(12, 6))

# Prior vs Posterior localization errors
sns.kdeplot(x=results["prior_loc_error"], fill=True, ax=axes[0], label="Prior", color=COL1, alpha=0.5, clip=(0, None))
sns.kdeplot(x=results["posterior_loc_error"], fill=True, ax=axes[0], label="Posterior", color=COL2, alpha=0.5, clip=(0, None))
# axes[0].set_title("Localization", fontsize=15, y=1.04)
axes[0].set_xlabel("Distance from real position (m)")
axes[0].legend()

# Localization error difference
sns.kdeplot(x=results["loc_error_diff"], fill=True, ax=axes[1], color=COL3)
axes[1].set_xlabel("Difference (m)")

fig.suptitle("Error on localization", fontsize=15, y=.98)
axes[0].set_title("(a)", fontsize=12, y=1.04)
axes[1].set_title("(b)", fontsize=12, y=1.04)


for ax in axes.flat:
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)

plt.tight_layout()
plt.subplots_adjust(top=0.9, wspace=.2)
plt.savefig("./results/figures/arrayReconstruction_localizationMetrics.png", dpi=300, bbox_inches="tight")
# plt.show()
