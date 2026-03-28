"""
This script estimates real recorder positions from GPS points and field measurements of distances between recorders.
It exports objects containing the estimated array geometry.
"""

import os
import numpy as np
import pandas as pd
import laplace_soundscape as lps
import lps.audiomoth.AudiomothPosition as AudiomothPosition

distances = pd.read_csv("./results/fieldTest_distances.csv")

DISTANCES = {
    (row.key1, row.key2): np.float64(row.value)
    for row in distances.itertuples(index=False)
}
INPUT_EPSG = 4326
TARGET_EPSG = 32620
DISTANCE_ERROR = 0.5

# Import audiomoth GPS data
C1, _ = AudiomothPosition("./data/test_localisation_20250808/C1/20250808","C1").summary(data_frame=True)
C2, _ = AudiomothPosition("./data/test_localisation_20250808/C2/20250808","C2").summary(data_frame=True)
D1, _ = AudiomothPosition("./data/test_localisation_20250808/D1/20250808","D1").summary(data_frame=True)
D2, _ = AudiomothPosition("./data/test_localisation_20250808/D2/20250808","D2").summary(data_frame=True)
A1, _ = AudiomothPosition("./data/test_localisation_20250808/A1/20250808","A1").summary(data_frame=True)
A2, _ = AudiomothPosition("./data/test_localisation_20250808/A2/20250808","A2").summary(data_frame=True)
A3, _ = AudiomothPosition("./data/test_localisation_20250808/A3/20250808","A3").summary(data_frame=True)
A4, _ = AudiomothPosition("./data/test_localisation_20250808/A4/20250808","A4").summary(data_frame=True)
B1, _ = AudiomothPosition("./data/test_localisation_20250808/B1/20250808","B1").summary(data_frame=True)

# Concatenate all priors coordinates in a table
priors_gps = pd.concat([D1,C2,C1,D2,A1,A2,A3,A4,B1]).set_index("aru")

# Change coordinates system
priors = lps.array.set_priors_crs(priors_gps, INPUT_EPSG, TARGET_EPSG)

# Fix two priors positions
priors.loc["C1","lon_mu"], priors.loc["C1", "lat_mu"] = -139600.928, 5195963.201
priors.loc["C1","lon_sd"], priors.loc["C1", "lat_sd"] = 1, 1
priors.loc["C2","lon_mu"], priors.loc["C2", "lat_mu"] = -139556.983, 5195954.490
priors.loc["C2","lon_sd"], priors.loc["C2", "lat_sd"] = 1, 1

print(priors)

array = lps.array.ArrayReconstruction(priors, DISTANCES, TARGET_EPSG, DISTANCE_ERROR)
array.get_distances()
array.plot()
# array.export_geojson("./results/aru_positions.geojson")
# array.export_geojson("./results/aru_gps_positions.geojson",posterior=False)
array.prior_points
array.posterior_points
array.names

array.save("./results/fieldTest_array")
print("Array successfully reconstructed. Results have been saved")
