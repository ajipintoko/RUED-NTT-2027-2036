# Data

All CSV files are plain-text copies (values only) of the sheets of the original workbooks in [`original/`](original/) and the component folders. Files marked *generated* are written by the scripts: do not edit them by hand.

| Folder / file | Source | Content |
|---|---|---|
| `original/Data untuk RUED NTT 2024.xlsx` | collected data | master data workbook (formulas, notes, source URLs) |
| `original/All LEAP Data.xlsx` | LEAP export | `All Data` (85k rows, all scenarios), `Key Assumptions`, load / wind / solar profiles |
| `original/LEAP Result.xlsx` | LEAP results | report tables and figures (`Tabel 2.x`, `Gambar 2.x`), `LEAP Data`, `Export Key Assumption`, `Data Sources`, `List Data Req` |
| `inputs/*.csv` | Data untuk RUED NTT 2024 | `asumsi_dasar_demografi`, `rumah_tangga`, `transportasi`, `komersial`, `industri`, `lainnya`, `energy_transformation`, `resource`, `power_generation_specification` |
| `keyassumptions/key_assumptions_yearly.csv` | LEAP Result | every Key Assumption as yearly values (2019–2050), with method |
| `calibration/historical_energy_mix_desdm.csv` | DESDM NTT | BBM, coal, gas, EBT and electricity by technology 2021–2025 |
| `calibration/pln_uiw_ntt_actual_sales_2020_2025.csv` | PLN UIW NTT (new) | sales (GWh), connected power, customers, tariff, growth 2020–2025 |
| `calibration/pln_electricity_sales_*.csv` | RUPTL C12.1 / C12.6 | sales 2015–2024 (actual) and 2025–2034 (projection) |
| `power/ruptl/*.csv` | RUPTL NTT | sales, customers, capacity, demand, RE Base and ARED scenarios, project list, potential |
| `power/plexos/plexos_*.csv` | Plexos | capacity by type and plant, 2026–2038: `bau_ruptl_gas`, `moderate_ruptl_re`, `optimis_substitusi_re`; `existing_ntt_power_plants` |
| `power/load_shapes/*.csv` | LEAP | `Kurva_Beban_NTT`, wind and solar profiles, system load, lifecycle (survival) profiles |
| `structure/` *(generated)* | `export_structure.py` | `branch_index`, `variables_current_accounts`, `variables_baseline`, `scenario_overrides`; hand-kept `scenarios.csv` |
| `dataflow/` *(generated)* | `export_structure.py`, `build_flow_tables.py` | `branch_links`, `sector_links`, `key_to_demand_by_source`, `transformation_inputs`, `chain_summary` |
| `results/leap_result/*.csv` | LEAP Result | one CSV per report table / figure sheet, `leap_data.csv` (results by scenario, 2019–2038) |
| `results/ruen_*.csv` | RUEN | Nusa Tenggara region comparison 2030 / 2035 |

Units are those of the source sheet; see the sheet headers. Branch names are Indonesian ([glossary](../docs/glossary.md)).
