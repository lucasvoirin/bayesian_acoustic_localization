# Bayesian acoustic localization with uncertain recorders positions

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11.9](https://img.shields.io/badge/python-3.11.9-blue.svg)](https://www.python.org/)

This repository contains code to reproduce analyses from "Bayesian acoustic localization with uncertain recorders positions"

## Installation

### Prerequisites

- Python >= 3.11.9
- pip

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
│   ├── arrayReconstruction_1_simulations.py      #
│   ├── arrayReconstruction_2_resultsAnalysis.py  #
│   ├── fieldTest_1_formatMetadata.py             #
│   ├── fieldTest_2_arrayReconstruction.py        #
│   ├── fieldTest_3_localization.py               #
│   ├── fieldTest_4_resultsAnalysis.py            #
│   └── fieldTest_getSoundsTimestamps.R           #
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
├── requirements.txt                              # pip dependencies
├── LICENSE
└── README.md
```

## Usage

As we udes relative paths to access data and functions, please make sure that you are running scripts from the root directory.


