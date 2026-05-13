from pyDataverse.api import NativeApi
import requests
import os
import pandas as pd
from tqdm import tqdm
import glob

BASE_URL = "https://borealisdata.ca"
DOI = "doi:10.5683/SP3/AUWB3O"

DIRS_ALL = [
    "test_localisation_20250808/SYNC",
    "mesures_distances_wood1_20250807/SYNC",
]

DIRS_CSV_ONLY = [
    "test_localisation_20250808/C1/20250808",
    "test_localisation_20250808/C2/20250808",
    "test_localisation_20250808/D1/20250808",
    "test_localisation_20250808/D2/20250808",
    "test_localisation_20250808/A1/20250808",
    "test_localisation_20250808/A2/20250808",
    "test_localisation_20250808/A3/20250808",
    "test_localisation_20250808/A4/20250808",
    "test_localisation_20250808/B1/20250808",
]

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

    dans_dossier_all = any(directory.startswith(d) for d in DIRS_ALL)
    dans_dossier_csv = any(directory.startswith(d) for d in DIRS_CSV_ONLY) and filename.endswith(".tab")
    est_fichier_specifique = filepath_relatif in FILES
    est_fichier_tab = filepath_relatif in TAB_FILES

    if dans_dossier_all or dans_dossier_csv or est_fichier_specifique or est_fichier_tab:
        est_tab = dans_dossier_csv or est_fichier_tab
        fichiers_a_telecharger.append((f, est_tab))

# Télécharger avec barre de progression
for f, est_tab in tqdm(fichiers_a_telecharger, desc="Téléchargement", unit="fichier"):
    directory = f.get("directoryLabel", "")
    filename = f["dataFile"]["filename"]
    file_id = f["dataFile"]["id"]

    dest_dir = os.path.join("data", directory) if directory else "data"
    os.makedirs(dest_dir, exist_ok=True)

    url = f"{BASE_URL}/api/access/datafile/{file_id}"
    r = requests.get(url, headers={"X-Dataverse-key": API_TOKEN}, timeout=120)

    if est_tab:
        filepath_tab_tmp = os.path.join(dest_dir, filename)
        filepath_csv = filepath_tab_tmp.replace(".tab", ".csv")
        with open(filepath_tab_tmp, "wb") as out:
            out.write(r.content)
        df = pd.read_csv(filepath_tab_tmp, sep="\t")
        df.to_csv(filepath_csv, index=False)
        os.remove(filepath_tab_tmp)
    else:
        filepath = os.path.join(dest_dir, filename)
        with open(filepath, "wb") as out:
            out.write(r.content)

# remettre les fichiers audiomoth en capitales
for path in glob.glob("./data/test_localisation_20250808/**/*.csv", recursive=True):
    os.rename(path, path.replace(".csv", ".CSV"))

path="./data/test_localisation_20250808/data.CSV"
os.rename(path, path.replace(".CSV", ".csv"))

os.makedirs("results/figures", exist_ok=True)
