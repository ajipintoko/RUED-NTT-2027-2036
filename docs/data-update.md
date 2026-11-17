# Updating the data (next year: 2026)

The Key Assumptions already hold **2019–2025**. For the next update:

## 1. Collect

| Data | Provider | Where to put it | LEAP target |
|---|---|---|---|
| Population, urbanisation, age, school, labour | BPS NTT | `Data untuk RUED NTT 2024.xlsx` → `Asumsi Dasar` | `Key\Populasi`, `Urbanisasi`, `Demografi\*` |
| PDRB by sector / industry sub-sector | BPS NTT | `Asumsi Dasar`, `Industry` | `Key\Makroekonomi\*` |
| Household electricity access, cooking fuel | BPS (Susenas / Kesra) | `Rumah Tangga` | `Key\Rumah Tangga\*`, `Demand\Rumah Tangga\Aktivitas Memasak` |
| Vehicle stock, sales, passengers | BPS / Dinas | `Transportasi` | `Key\Transportasi\*` |
| Schools, health facilities, hotels, retail, tourists | BPS / Dinas | `Komersil` | `Key\Bangunan Komersial\*` |
| Industry fuel use | survey / Dinas | `Industry` | `Demand\Industri\*\Total Energy` |
| Plants, capacity, production, fuel | ESDM worksheet for NTT (Provinsi, DESDM) | `Worksheet Perhitungan Bauran Energi Daerah` of the new year → add to `scripts/compile_bauran_energi.py` | `Transformation` processes (Current Accounts), Demand fuels |
| Electricity sales, customers, losses | PLN UIW NTT | `kWh Jual` workbook | `Indicators\Perbandingan demand listrik`, T&D `Losses` |

## 2. Write into LEAP

1. Select **Current Accounts**. For each Key Assumption add the new year as one more point inside the existing function, e.g. `Interp(2019; 7.97; …; 2025; 8.41)` → `Interp(2019; 7.97; …; 2025; 8.41; 2026; x)`. `Step`, `LinForecast` and `LogisticForecast` take extra pairs the same way.
2. Move the **anchor** of growth expressions: `Key\Populasi` and others use `Growth(...)` from the last data year; make sure the projection starts after the new last year.
3. Update calibration blocks: `Historical Production`, `Exogenous Capacity` (CA) and `Losses` (T&D).
4. Update the Plexos pathways if the RUPTL or the grid changed ([power-plexos.md](power-plexos.md)), then paste the capacities.
5. Update the PLN series in `Perbandingan demand listrik`.

## 3. Check

Run **Current Accounts + BAU + MOD + OPT**, then follow the [calibration checklist](calibration.md#3-calibration-checklist-every-update).

## 4. Refresh the repository

```bash
# LEAP: Analysis > Export to Excel (all scenarios) -> data/original/All LEAP Data.xlsx, sheet "All Data"
python scripts/export_structure.py
python scripts/build_flow_tables.py
python scripts/split_workbooks.py
git diff --stat data/structure data/dataflow
```

Update the counts in the README and the sector pages if the structure changed, and save the new `.leap` in `model/` with a dated name.
