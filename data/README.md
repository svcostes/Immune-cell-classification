# data/

Input files required to run the notebooks.

## representative_images/

Raw microscopy TIFFs (one multi-channel Z-stack per field of view), e.g. `852_Fe_0_4hr_CD4_CD19_D6/`, `934_Gamma_1_4hr_CD4_CD19_B11/`. Each field folder holds the per-channel/per-Z-slice TIFFs (C00–C03, Z0000–Z0020) named like `859_Fe_0_24h_Set2_B_21B_S1411(P2-H2)_Z0010_C03(AF647)_M0000_ORG.tif`.

The full set is too large for version control (git-ignored). Obtain it from:

- **OSDR** — `uv run python src/download_from_osdr.py` (accession **OSD-1027**), or
- the machine where it was already extracted, or the lead contact (sylvain.costes@pitt.edu).

A small subset of fields is sufficient for a demo run of notebook 2.

## Tabular inputs (notebook 1)

- `cleaned_counterstain_data_with_metadata.csv` — per-cell counterstain intensity data with well/plate/radiation metadata. 
- `BNL_21B_flat_plate_IDs_new.csv` — maps (Radiation, Set, Well) → Patient ID.
- `patient_info.csv` — patient demographics (Age, Sex, Height, Weight, BMI, self-reported category).
- `full_53bp1_connie.csv` — (Pariset et al. 2020) 53BP1 dataset. Notebook 1 merges it as `"All-old"` and uses it as the **trusted baseline** to batch-correct the new (`"All-new"`) measurements (per-condition linear regression) and in the `nac = (na + no)/2` cell-count normalization. The 192-donor cohort reported in the manuscript is the "All-new" data; "All-old" is the correction reference, not part of the reported cohort.
