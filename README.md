# Bayesian acoustic localization with uncertain recorders positions

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11.9](https://img.shields.io/badge/python-3.11.9-blue.svg)](https://www.python.org/)
[![R 4.5.3](https://img.shields.io/badge/R-4.5.3-blue.svg)](https://www.r-project.org/)

This repository contains code to reproduce analyses from "Bayesian acoustic localization with uncertain recorders positions"

## Installation

### Prerequisites

Make sure the following softwares (with appropriate version if specified) are installed on your device:

- Python >= 3.11.9
- pip
- R >= 4.5.3

To install a specific version of Python on your device we recommand you to use [pyenv](https://github.com/pyenv/pyenv).

### Download code

```bash
# Download files
git clone https://github.com/lucasvoirin/bayesian_acoustic_localization.git

# Move to the working directory
cd bayesian_acoustic_localization
```

### Install dependencies in a virtual environment

```bash
# Create venv directory to store dependencies
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install required libraries in virtual environment
pip install -r requirements.txt

```

### Download data

The `download_data.py` script can be used to download acoustic data from the Borealis dataverse.

```bash
python3 download_data.py
```

## Repository structure

```
├── data/                                         # Only after running download_data.py
│   ├── test_localisation_20250808/               # Acoustic data for localization tests
│   └── mesures_distances_wood1_20250807/         # Acoustic data for acoustic distance meter
│
├── notebooks/
│   └── localization_field_test.ipynb             # Example workflow
│
├── src/
│   ├── arrayReconstruction_1_simulations.py      # Performs simulations of array reconstruction
│   ├── arrayReconstruction_2_resultsAnalysis.py  # Computes summary statistics
│   ├── fieldTest_1_formatMetadata.py             # Prepares metadata and compute real distances
│   ├── fieldTest_2_arrayReconstruction.py        # Estimates recorder coordinates
│   ├── fieldTest_3_localization.py               # Localize broadcast sounds
│   ├── fieldTest_4_resultsAnalysis.py            # Computes summary statistics
│   └── fieldTest_getSoundsTimestamps.R           # Finds sounds sequences in recordings
│
├── figures/                                      # Contains code to reproduce figures
│   ├── arrayReconstruction_arrayExample.py
│   ├── arrayReconstruction_arrayMetrics.py
│   ├── arrayReconstruction_localizationMetrics.py
│   ├── fieldTest_array.py
│   └── fieldTest_histErrorFm.py
│
├── results/
│   └── figures/                                  # Generated figures
│
├── download_data.py                              # Downloads data TO RUN FIRST
├── run_all.py                                    # Runs all analyses CAN TAKE SOME TIME
├── requirements.txt                              # pip dependencies
├── LICENSE
└── README.md
```

## Usage

As we udes relative paths to access data and functions, please make sure that you are running scripts from the root directory.

The analyses are computation intesive, running them can take a lot of time (several hours).

### "À la carte"

To run the simultions of array reconstruction, please execute the following scripts in the specified order:

1. `src/arrayReconstruction_1_simulations.py`
2. `src/arrayReconstruction_2_resultsAnalysis.py`

To run the localization tests, please execute the following scripts in the specified order:

1. `src/fieldTest_1_formatMetadata.py`
2. `src/fieldTest_2_arrayReconstruction.py`
3. `src/fieldTest_3_localization.py`
4. `src/fieldTest_4_resultsAnalysis.py`

To run figure generation scripts, please execute the following scripts:

- `figures/arrayReconstruction_arrayExample.py`
- `figures/arrayReconstruction_arrayMetrics.py`
- `figures/arrayReconstruction_localizationMetrics.py`
- `figures/fieldTest_array.py`
- `figures/fieldTest_histErrorFm.py`


### All

To run all scripts (analyses and figures), please run the following script:

```bash
python3 run_all.py
```

This can take a very long time, it is better to run it on a server.

If you experience problems runing this script, you can try to run scripts "à la carte" to debug.

## Notebook

We provide an extra notebook as a simple example of acoustic localization.

You can access it by running jupyter lab from the root directory.

```bash
jupyter lab
```
