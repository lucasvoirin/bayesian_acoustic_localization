from pyDataverse.api import NativeApi
import requests
import os
import pandas as pd
from tqdm import tqdm

BASE_URL = "https://borealisdata.ca"
DOI = "doi:10.5683/SP3/AUWB3O"
DIRS = ["test_localisation_20250808/SYNC", "mesures_distances_wood1_20250807/SYNC"]
FILES = ["test_localisation_20250808/master_propagation_2025_annotations.rds"]
TAB_FILES = ["test_localisation_20250808/data.tab", "mesures_distances_wood1_20250807/distances.tab"]

api = NativeApi(BASE_URL)
dataset = api.get_dataset(DOI)
files = dataset.json()["data"]["latestVersion"]["files"]

# Filtrer les fichiers
fichiers_a_telecharger = []
for f in files:
    directory = f.get("directoryLabel", "")
    filename = f["dataFile"]["filename"]
    filepath_relatif = os.path.join(directory, filename)

    dans_dossier_cible = any(directory.startswith(d) for d in DIRS)
    est_fichier_specifique = filepath_relatif in FILES
    est_fichier_tab = filepath_relatif in TAB_FILES

    if dans_dossier_cible or est_fichier_specifique or est_fichier_tab:
        fichiers_a_telecharger.append((f, est_fichier_tab))

# Télécharger avec barre de progression
for f, est_fichier_tab in tqdm(fichiers_a_telecharger, desc="Téléchargement", unit="fichier"):
    directory = f.get("directoryLabel", "")
    filename = f["dataFile"]["filename"]
    file_id = f["dataFile"]["id"]

    url = f"{BASE_URL}/api/access/datafile/{file_id}"

    if est_fichier_tab:
        filename_out = filename.replace(".tab", ".csv")
    else:
        filename_out = filename

    filepath = os.path.join("data", directory, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    r = requests.get(url, headers={"X-Dataverse-key": API_TOKEN})

    if est_fichier_tab:
        filepath_tab_tmp = filepath.replace(".csv", ".tab")
        with open(filepath_tab_tmp, "wb") as out:
            out.write(r.content)
        try:
            df = pd.read_csv(filepath_tab_tmp, sep="\t")
            df.to_csv(filepath, index=False)
            os.remove(filepath_tab_tmp)
        except Exception as e:
            os.rename(filepath_tab_tmp, filepath_tab_tmp)
    else:
        with open(filepath, "wb") as out:
            out.write(r.content)

# Ajouter les dossiers de figures et résultats
os.makedirs("results/figures", exist_ok=True)
