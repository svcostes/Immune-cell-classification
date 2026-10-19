# Immune Cell Classification & Processing

Analysis code for the iScience manuscript *"Divergent DNA Damage and Morphological Responses of Immune Cells to High-LET Radiation"* (Modi, Bansal, Sakharkar, Penninckx, Cekanaviciute, Costes).

This package reproduces the immune-cell classification pipeline and the representative-image visualization used in the paper. 

## Directory structure

```
Immune-cell-classification/
├── README.md
├── pyproject.toml                      # uv project definition (dependencies)
├── .gitignore
├── data/
│   ├── representative_images/          # raw microscopy TIFFs (see "Raw data" below)
│   ├── cleaned_counterstain_data_with_metadata.csv
│   ├── BNL_21B_flat_plate_IDs_new.csv
│   ├── patient_info.csv
│   └── full_53bp1_connie.csv
├── results/                             # all outputs land here
│   └── Output_MIP_panel_1/              # generated 2-panel PNGs
└── src/
    ├── immune_cell_classification_and_processing.ipynb   # step 1
    ├── cell_classification_visualization.ipynb           # step 2
    └── download_from_osdr.py                             # fetch data from OSDR (placeholder)
```

## Environment (uv)

This repository uses [uv](https://docs.astral.sh/uv/) to manage its Python environment. Dependencies are declared in `pyproject.toml`.

```bash
# one-time: create the virtualenv and install all dependencies
uv sync

# include the optional Cellpose dependency (recommended for better segmentation;
# the notebooks fall back to Otsu thresholding without it)
uv sync --extra cellpose

# start Jupyter inside the uv-managed environment
uv run jupyter notebook
```

If you don't have `uv`, install it first: `curl -LsSf https://astral.sh/uv/install.sh | sh` (or `pip install uv`).

## The two notebooks

### 1. `immune_cell_classification_and_processing.ipynb`

The classification + processing pipeline. It:

1. Loads the cleaned per-cell counterstain data (`cleaned_counterstain_data_with_metadata.csv`).
2. Fits per-well Gaussian mixture models (1- vs 2-component) to the log-transformed AF594/AF647 intensity distributions to identify the negative population; the 97.5th percentile of the negative component (with secondary-control "floors") defines the positivity cutoffs.
3. Applies the cutoffs to classify cells (AF594-only / AF647-only / unclassified) and writes the per-well cutoff table.
4. Merges cell types, demographics, and the historical ("Connie") 53BP1 dataset into the final foci/size datasets — the legacy cohort becomes `"All-old"`, the new cohort becomes `"All-new"`.
5. Batch-corrects `"All-new"` against the `"All-old"` trusted baseline (per-condition linear regression on `mean_nfoci` / `mean_AF488`) and writes `corrected_nfoci_AF488_dataset_12.20_high.csv`.
6. Computes cell-count proportions and the `nac = (na + no)/2` normalization, writing `immune_cells_corrected_output_12.20_high_wp2a.csv`.

**Inputs (all in `data/`):** `cleaned_counterstain_data_with_metadata.csv`, `BNL_21B_flat_plate_IDs_new.csv`, `patient_info.csv`, `full_53bp1_connie.csv`.

**Outputs (written to `results/`):** `per_well_cutoffs_all_plates_AF594_AF647_0.975_WITH_secondary_floors_high.csv`, `combined_data_with_cell_types_12.20_high.csv`, `final_nfoci_AF488_size_with_demographics_and_old_FFI_12.20_high.csv`, `corrected_nfoci_AF488_dataset_12.20_high.csv`, `immune_cells_corrected_output_12.20_high_wp2a.csv`.

### 2. `cell_classification_visualization.ipynb`

Generates the two-panel quality-control figures (left: DAPI + 53BP1/AF488 overlay; right: classified overlay with AF594-purple / AF647-red masks) for each field of view, using Cellpose (if available) or Otsu for nuclear segmentation.

**Inputs:** `data/representative_images/` (raw TIFFs) and the per-well cutoff table produced by notebook 1 (`results/per_well_cutoffs_...csv`).

**Outputs:** `results/Output_MIP_panel_1/` (one `*_two_panel_classified.png` per field, plus `panel_metrics.csv`).

> **Run order matters:** notebook 1 must be run first, because notebook 2 reads the `per_well_cutoffs` CSV that notebook 1 writes.

## Downloading data from OSDR

The full imaging dataset is deposited in the NASA Open Science Data Repository (**OSDR**, accession **OSD-1027**). `src/download_from_osdr.py` pulls it down and places the TIFFs in `data/representative_images/` and any tabular inputs in `data/`:

```bash
uv run python src/download_from_osdr.py
```

> **Note:** this script is a placeholder until the OSDR upload is finalised — it will report "No files found" while the accession is still pending, and is expected to work unchanged once the deposit is live. See the `TODO(OSDR upload)` markers in the script.

## Raw data

The raw multi-channel Z-stack TIFFs (one per field of view, e.g. `852_Fe_0_4hr_CD4...`, `934_Gamma_1_4hr...`) are too large to commit to version control and are **not** tracked by git (see `.gitignore`). They can be obtained two ways:

1. **From OSDR** — run `uv run python src/download_from_osdr.py` (accession **OSD-1027**).
2. **Locally** — the full set lives in `data/representative_images/`. A small subset of fields is sufficient for a demo run of notebook 2.

A full image set is also available from the lead contact (sylvain.costes@pitt.edu).
