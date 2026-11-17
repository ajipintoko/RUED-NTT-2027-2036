# Calibration

Three data sets are used to make Current Accounts (2019–2025) reproduce reality.

| Data set | Provider | File | Calibrates |
|---|---|---|---|
| **Bauran Energi Daerah NTT 2021–2025** (ESDM worksheets, compiled) | ESDM template filled for NTT (Provinsi / DESDM) | [`Bauran_Energi_Daerah_NTT_2021-2025.xlsx`](../data/calibration/Bauran_Energi_Daerah_NTT_2021-2025.xlsx) (+ [CSV](../data/calibration/bauran_energi/), [5 source workbooks](../data/calibration/source_worksheets/)) | **off-grid** supply and the **overall (primary) energy consumption** by fuel, 2021–2025 |
| **Penjualan Tenaga Listrik (GWh)** | PLN UIW NTT / RUPTL C12 | [`pln_electricity_sales_*.csv`](../data/calibration/) and [`pln_uiw_ntt_actual_sales_2020_2025.csv`](../data/calibration/pln_uiw_ntt_actual_sales_2020_2025.csv) | **electricity load** (final demand of electricity, by customer group) |
| RUPTL | PLN | [`data/power/ruptl/`](../data/power/ruptl/) | on-grid capacity and the load basis of Plexos |

## 1. Bauran Energi Daerah (ESDM calibration, 2021–2025)

This replaces the earlier *Historical Energy Mix* workbook. The five yearly workbooks *Worksheet Perhitungan Bauran Energi Daerah – Provinsi NTT* (2021 … 2025) were compiled by [`scripts/compile_bauran_energi.py`](../scripts/compile_bauran_energi.py) into one workbook:

| Sheet | Content |
|---|---|
| `README` | sources, units, method differences and data flags |
| `Ringkasan_Bauran` | energy mix per year (EBT, Minyak Bumi, Gas Bumi, Batubara): BOE, TOE, MTOE, %; plus a block without firewood |
| `Pivot_Konsumsi` | fuels by year in original unit (KL, ton, mscf, m³/yr) and in BOE |
| `Pivot_Listrik` | renewable capacity (MW) and generation (GWh) by technology, **on-grid and off-grid**, by year |
| `Worksheet_Long` | every row of every yearly worksheet (tidy; source file and row, BOE factor, CF / efficiency, note) |
| `DataEnergi_Input` | non-empty inputs of the `Data Energi` sheets |
| `Kegiatan_2022` | 2022 programme list (PLTS/LTSHE, biogas, rooftop PV, PLTMH) |

Conversion in the worksheets: original unit × BOE factor (e.g. RON 92 and 90 = 5.8275 BOE/kL, Solar and Biosolar = 6.4871, kerosene 5.9274, MFO 6.9612, avtur 5.8907, LPG 8.5246 BOE/Mton, coal 3.4417 BOE/ton, gas 0.1796 BOE/mscf) → TOE.

### Energy mix by year (BOE)

| | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---:|---:|---:|---:|---:|
| Minyak Bumi | 4,767,181 | 4,989,985 | 5,173,073 | 5,267,308 | 5,044,137 |
| Batubara | 1,387,456 | 1,760,584 | 2,283,552 | 1,708,901 | 1,934,913 |
| Gas Bumi | 0 | 0 | 0 | 0 | 0 |
| EBT | 6,982,047 | 1,261,155 | 1,601,306 | 1,665,281 | 2,265,905 |
| **Total** | **13,136,684** | **8,011,725** | **9,057,930** | **8,641,489** | **9,244,956** |
| EBT share | 53.1 % | 15.7 % | 17.7 % | 19.3 % | 24.5 % |
| EBT share without firewood | 17.9 % | 15.7 % | 17.7 % | 19.3 % | 24.5 % |

**Break in 2021**: only the 2021 workbook includes firewood (2,200,020 ton = 5.64 million BOE). From 2022 firewood is 0 (the 2023–2025 files are *tanpa kayu bakar*). Use the "without firewood" line to compare years, and do not calibrate household biomass to the 2021 value without deciding how firewood is treated in `Demand\Rumah Tangga\Aktivitas Memasak\Wood`.

Key fuel volumes (original units): ron 90/88/89 326,079 → 341,654 kL; biosolar 244,299 → 259,042 kL (blend B30 → B40); kerosene 108,412 → 110,641 kL; LPG 1,559 → 2,341 Mton; coal for PLTU 403,131 → 559,968 ton; biomass 131 → 167,485 ton; household biogas 1,052,262 → 616,140 m³/yr.

Renewable capacity 2025 (MW on-grid / off-grid): PLTP 24.08 / 0, PLTMH 6.17 / 2.71, PLTM 3.0 / 0, PLTS 20.37 / 4.06, PLTS Atap 0 / 0.59. Generation 2025 (GWh): PLTP 189.9, PLTMH 32.4 + 14.2, PLTM 15.8, PLTS 35.7 + 7.1, PLTS Atap 1.0 (off-grid).

### How it enters LEAP

* `Pembangkit Listrik Ongrid\Processes\*` (**Current Accounts**): `Exogenous Capacity` 2019–2025 and `Historical Production` (GWh) per technology, e.g. `PLTP Existing` `Step(2021; 56.44; 2022; 55.37; 2023; 58.14; 2024; 54.78; 2025; 52.06)`. Compare with `Pivot_Listrik`: the worksheets give renewable plants only; thermal plants (PLTU, PLTD, PLTMG) come from fuel use (`Pivot_Konsumsi`, coal 3.4417 BOE/ton, efficiency 30 %) and PLN data.
* `Pembangkit Listrik Offgrid\Processes\*`: capacities from the off-grid columns of `Pivot_Listrik` (PLTMH `Step(2021; 2.58; 2022; 2.68; 2023; 3.51; 2025; 2.71)`, PLTS komunal, PLTS Atap) and `Maximum Availability` of the PLTD tuned to reproduce the diesel fuel (`90 × Interp(2021; 0.32; 2022; 0.36; 2023; 0.99)`).
* Demand `Total Energy` / intensity data blocks for fuels, so that total final energy and **primary supply** (`Resources`) match the mix.

The **capacities** already typed in LEAP (PLTP 24.08 MW, PLTMH 2.71 MW off-grid …) agree with these worksheets. The **generation** does not always: the worksheets estimate GWh as capacity × a fixed capacity factor (PLTP CF 0.9 → 189.9 GWh in 2025), while LEAP `Historical Production` of `PLTP Existing` uses PLN actual production (52.06 GWh in 2025). Use the worksheet generation as an upper-bound cross-check for renewables, and PLN production for the calibration of the on-grid processes (see [known issue 14](known-issues.md)). If you change a value in LEAP, change it in the worksheet too and re-run the compile script.

**Check**: run Current Accounts, then compare (a) `Resources:Primary Supply` per fuel with `Ringkasan_Bauran` / `Pivot_Konsumsi` and (b) generation by technology with `Pivot_Listrik`.

### Data flags (see the workbook `README` sheet)

* LTSHE 2021 = 312.5 GWh (191,563 BOE) vs about 0.002 GWh in other years: probably a unit error.
* Avtur: 0 (2021), 31,024 (2022), 36,452 (2023), 32,646 (2024) and only 399 kL (2025): verify the 2025 value.
* PLTS Atap on-grid is 0 in 2025 while 0.59 MW appears off-grid.
* BOE factors differ slightly between years (coal 3.442 in 2021, 3.455 in 2025).

## 2. Electricity load (PLN UIW NTT)

Actual sales (GWh), from [`pln_uiw_ntt_actual_sales_2020_2025.csv`](../data/calibration/pln_uiw_ntt_actual_sales_2020_2025.csv) (new data from PLN UIW NTT, with connected power, customers, tariff and growth):

| Group | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---:|---:|---:|---:|---:|---:|
| Rumah Tangga | 729.3 | 749.0 | 759.4 | 808.8 | 897.1 | 966.1 |
| Bisnis + Layan Khusus | 232.2 | 238.7 | 270.6 | 316.2 | 317.4 | 340.8 |
| Publik + Sosial | 124.0 | 131.3 | 148.7 | 165.0 | 197.2 | 192.0 |
| Industri | 48.0 | 41.2 | 28.3 | 43.2 | 42.5 | 43.3 |
| **Total** | **1,133.5** | **1,160.2** | **1,206.9** | **1,333.3** | **1,454.1** | **1,542.2** |

The RUPTL table ([`pln_electricity_sales_actual_2015_2024.csv`](../data/calibration/pln_electricity_sales_actual_2015_2024.csv)) gives 2015–2024 (2024 is a *prognosa*: 1,450 GWh) and the projection 2025–2034 (1,592 → 3,105 GWh). The new data replaces the prognosa for 2024 (1,454) and the projection for 2025 (1,542 vs 1,592).

Where it is used:

* `Indicators\Perbandingan demand listrik\*` holds PLN sales by group and the RUED result of the same group (`Rumah Tangga RUED`, `Komersial RUED`, `Industri RUED`, totals). The PLN series are typed with `Interp(2015; …; 2034; …)`: **update them with the 2024 and 2025 actuals** above.
* `Transmisi dan Distribusi` `Losses` (9.13, 5.79, 8.23, 12.08, 10.81 % for 2019–2023): extend with 2024–2025 PLN loss data.
* Group mapping: LEAP `Rumah Tangga` (PLN + off-grid houses + EV) ↔ PLN *Rumah Tangga*; LEAP `Komersial` ↔ *Bisnis + Layan Khusus* + *Publik + Sosial*; LEAP `Industri` + `Lainnya` ↔ *Industri*.

## 3. Calibration checklist (every update)

| # | Check | Tolerance suggestion |
|---|---|---|
| 1 | Total PLN-grid electricity demand 2020–2025 vs PLN sales | ±3 % per group |
| 2 | Generation by technology vs `Historical Production` | exact by construction (Current Accounts) |
| 3 | Primary supply by fuel (oil, coal, gas, EBT) vs Bauran Energi Daerah (`Ringkasan_Bauran`, `Pivot_Konsumsi`) | ±5 % |
| 4 | Off-grid generation and PLTD fuel vs off-grid block of the Energy Mix | ±5 % |
| 5 | T&D losses vs PLN | as PLN reports |
| 6 | 2025→2026 step: no discontinuity larger than the growth assumption (check `Komersial`, tourists 20 %/yr) | judgement |

Open issues found while documenting are in [known-issues.md](known-issues.md).
