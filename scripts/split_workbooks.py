"""Dismantle the source workbooks into one small CSV per sheet.

Why: the original .xlsx files are large, binary and hard to diff. The CSV copies are
plain text (values only, formulas are evaluated), easy to review in Git and small.
The original workbooks are kept next to the CSVs for the formulas and formatting.

Usage
    python scripts/split_workbooks.py            # run from the repository root

Layout written (see data/README.md for what every file is):
    data/inputs/              <- data/original/Data untuk RUED NTT 2024.xlsx
    data/keyassumptions/      <- data/original/LEAP Result.xlsx  (sheet 'Export Key Assumption')
    data/results/leap_result/ <- data/original/LEAP Result.xlsx  (all report tables)
    data/results/             <- RUEN for Comparison Nusa Tenggara Region.xlsx
    data/calibration/         <- Historical Energy Mix.xlsx, Penjualan_Tenaga_Listrik_GWh.xlsx
    data/power/ruptl/         <- Data_RUPTL_NTT.xlsx
    data/power/plexos/        <- Plexos Result to LEAP.xlsx
    data/power/load_shapes/   <- data/original/All LEAP Data.xlsx (load / wind / solar profiles, lifecycle)

The 85,000-row 'All Data' sheet of 'All LEAP Data.xlsx' is NOT converted here;
scripts/export_structure.py turns it into data/structure and data/dataflow.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]

# workbook (relative to ROOT) -> (output folder, sheets to skip, optional {sheet: filename})
JOBS = [
    ("data/original/Data untuk RUED NTT 2024.xlsx", "data/inputs", [], {
        "Asumsi Dasar": "asumsi_dasar_demografi",
        "Rumah Tangga": "rumah_tangga",
        "Transportasi": "transportasi",
        "Komersil": "komersial",
        "Industry": "industri",
        "Lainnya": "lainnya",
        "Energy Transformation": "energy_transformation",
        "Resource": "resource",
        "Power Generation Specification": "power_generation_specification",
    }),
    ("data/original/LEAP Result.xlsx", "data/results/leap_result", ["Export Key Assumption"], {}),
    ("data/original/LEAP Result.xlsx", "data/keyassumptions", [s for s in ()], {"Export Key Assumption": "key_assumptions_yearly"}),
    ("data/results/RUEN for Comparison Nusa Tenggara Region.xlsx", "data/results", [], {
        "2030": "ruen_nusa_tenggara_2030", "2035": "ruen_nusa_tenggara_2035",
        "Perbandingan 2030-2035": "ruen_nusa_tenggara_comparison"}),
    ("data/calibration/Historical Energy Mix.xlsx", "data/calibration", [], {"Sheet1": "historical_energy_mix_desdm"}),
    ("data/calibration/PLN_UIW_NTT_kWh_Jual_2020_2025.xlsx", "data/calibration", [], {"Sheet1": "pln_uiw_ntt_actual_sales_2020_2025"}),
    ("data/calibration/Penjualan_Tenaga_Listrik_GWh.xlsx", "data/calibration", [], {
        "Realisasi 2015-2024": "pln_electricity_sales_actual_2015_2024",
        "Proyeksi 2025-2034": "pln_electricity_sales_projection_2025_2034"}),
    ("data/power/ruptl/Data_RUPTL_NTT.xlsx", "data/power/ruptl", [], {}),
    ("data/power/plexos/Plexos Result to LEAP.xlsx", "data/power/plexos", [], {
        "RUPTL 2025 + Gas": "plexos_bau_ruptl_gas",
        "RUPTL + RE": "plexos_moderate_ruptl_re",
        "Substitusi RE": "plexos_optimis_substitusi_re",
        "Existing NTT": "existing_ntt_power_plants"}),
    ("data/original/All LEAP Data.xlsx", "data/power/load_shapes", ["All Data", "Key Assumptions"], {
        "Kurva_Beban_NTT": "load_curve_ntt", "WindProfileNTT": "wind_profile_ntt",
        "SolarProfileNTT": "solar_profile_ntt", "System Load": "system_load", "Lifecycle Profiles": "lifecycle_profiles"}),
]


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def main() -> None:
    for rel, out, skip, names in JOBS:
        src = ROOT / rel
        if not src.exists():
            print("missing:", rel, file=sys.stderr)
            continue
        wb = openpyxl.load_workbook(src, read_only=True, data_only=True)
        folder = ROOT / out
        folder.mkdir(parents=True, exist_ok=True)
        for ws in wb.worksheets:
            if ws.title in skip:
                continue
            if names and ws.title not in names:
                continue
            name = names.get(ws.title) or slug(ws.title)
            path = folder / f"{name}.csv"
            rows = []
            for row in ws.iter_rows(values_only=True):
                row = ["" if v is None else v for v in row]
                while row and row[-1] == "":
                    row.pop()
                rows.append(row)
            while rows and not rows[-1]:
                rows.pop()
            with open(path, "w", newline="", encoding="utf-8") as fh:
                csv.writer(fh).writerows(rows)
            print(f"{path.relative_to(ROOT)}  ({len(rows)} rows)")


if __name__ == "__main__":
    main()
