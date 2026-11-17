# How to

## Trace a value from result to source

1. Find the branch in [`branch_index.csv`](../data/structure/branch_index.csv) (`branch_path`).
2. Read its expression in [`variables_baseline.csv`](../data/structure/variables_baseline.csv) (or `variables_current_accounts.csv` for 2019–2025).
3. For every `Key\…[unit]` in the expression, look up that branch; repeat until you reach a data block (`Interp`, `Step`).
4. The data block's source is in `data/inputs/*.csv` (see [data/README.md](../data/README.md)).
5. To go the other way (who uses this branch?): filter [`branch_links.csv`](../data/dataflow/branch_links.csv) on `from_path`.

## See what a scenario changes

Filter [`scenario_overrides.csv`](../data/structure/scenario_overrides.csv) on `Scenario`. Columns show the scenario and Baseline expression side by side.

## Add a branch

1. Add it in LEAP under the right sector, keep the naming of siblings (Indonesian, same unit).
2. Feed it from a Key Assumption rather than typing numbers into Demand, so it appears in the dataflow.
3. Export All Data and re-run the scripts; check the branch in `branch_index.csv`.

## Refresh the files

| Script | Input | Output |
|---|---|---|
| `scripts/export_structure.py` | `data/original/All LEAP Data.xlsx` (sheet `All Data`) | `data/structure/*`, `data/dataflow/branch_links.csv`, `sector_links.csv` |
| `scripts/build_flow_tables.py` | `data/dataflow/branch_links.csv` | `key_to_demand_by_source.csv`, `transformation_inputs.csv`, `chain_summary.csv` |
| `scripts/split_workbooks.py` | workbooks in `data/` | one CSV per sheet |
| `scripts/compile_bauran_energi.py` | five yearly ESDM `Worksheet Perhitungan Bauran Energi Daerah` workbooks (`data/calibration/source_worksheets/`) | `data/calibration/Bauran_Energi_Daerah_NTT_2021-2025.xlsx` and `bauran_energi/*.csv` |

Run from the repository root with Python 3.10+, `pandas` and `openpyxl`. Never edit generated CSV files by hand.

## Git LFS

`.leap` and `.xlsx` are tracked with Git LFS (see `.gitattributes`). Run `git lfs install` once, before the first `git add`. The `.leap` file is 54 MB: above GitHub's 50 MB warning, below its 100 MB limit, so LFS is recommended.

## Open the model

Unzip is not needed: in LEAP use *Area → Restore* and select `model/RUED NTT 2027-2038 Agustus 2026.leap`. Do not commit an unpacked LEAP working folder (see `.gitignore`).
