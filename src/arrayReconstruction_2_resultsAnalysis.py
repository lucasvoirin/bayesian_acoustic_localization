"""
This script compute summaries from array reconstruction simulatiosn.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

results = pd.read_csv("./results/arrayReconstruction_simulationResults.csv")

results.columns

original_len = len(results)

results = results[~(results["max_rhat"]>1.01) & ~(results["min_ess"]<400) & (results["no_divergences"])]

# discarded simulations
original_len - len(results)

# Réduction erreur sur position enregistreurs
np.mean(results['configuration_diff'])

# Réduction variance sur position enregistreurs
np.mean(results['variance_diff'])

# Réduction erreur sur position grille
np.mean(results['bias_diff'])

# Réduction erreur sur localisation
np.mean(results['loc_error_diff'])


# Proportion de simulations avec amélioration position enregistreur
len(results[results["configuration_diff"]<0])/len(results)

# Proportion de simulations avec amélioration variance position enregistreur
len(results[results["variance_diff"]<0])/len(results)

# Proportion de simulations avec amélioration position grille
len(results[results["bias_diff"]<0])/len(results)

# Proportions de localisations améliorées
len(results[results["loc_error_diff"]<0])/len(results)
