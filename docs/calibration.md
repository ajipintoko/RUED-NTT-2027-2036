# Calibration

Three data sets are used to make Current Accounts (2019–2025) reproduce reality.

| Data set | Provider | File | Calibrates |
|---|---|---|---|
| **Historical Energy Mix** | DESDM NTT | [`historical_energy_mix_desdm.csv`](../data/calibration/historical_energy_mix_desdm.csv) | **off-grid** supply and the **overall (primary) energy consumption** by fuel, 2021–2025 |
| **Penjualan Tenaga Listrik (GWh)** | PLN UIW NTT / RUPTL C12 | [`pln_electricity_sales_*.csv`](../data/calibration/) and [`pln_uiw_ntt_actual_sales_2020_2025.csv`](../data/calibration/pln_uiw_ntt_actual_sales_2020_2025.csv) | **electricity load** (final demand of electricity, by customer group) |
| RUPTL | PLN | [`data/power/ruptl/`](../data/power/ruptl/) | on-grid capacity and the load basis of Plexos |

## 1. Historical Energy Mix (DESDM NTT)

Structure of the sheet (one block per energy type, columns 2021–2025):

| Block | Contents | Conversion |
|---|---|---|
| **Minyak Bumi** | BBM by product (Avgas, Avtur, MFO, RON 88–98, Kerosene, Solar CN 48/51/53, Biogasoil B20–B40 …) in kL | × BOE per kL (e.g. RON 92 = 5.8275, Solar = 6.4871); `Calibrated` flag `Ok` |
| **Batubara** | coal for PLTU (ton) and industry | × 3.4417 BOE/ton; PLTU capacity and efficiency 30 % → GWh |
| **Gas** | gas for PLTG/MG and industry (MSCF) | – |
| **EBT / Non Listrik** | FAME, ethanol, biomass (PLTU co-firing, industry, wood), household biogas | – |
| **Listrik** | capacity (MW) by technology (PLTA, PLTB, PLTM, PLTMH, PLTP, PLTS, PLTS Atap, Hybrid …) and **CF** → GWh; separate block for **off-grid** capacities | capacity × CF × 8.76 |
| **Listrik by user** | Industry, Komersial … | cross-check with PLN |

How it enters LEAP:

* `Pembangkit Listrik Ongrid\Processes\*` (**Current Accounts**): `Exogenous Capacity` 2019–2025 and `Historical Production` (GWh) per technology, e.g. `PLTP Existing` `Step(2021; 56.44; 2022; 55.37; 2023; 58.14; 2024; 54.78; 2025; 52.06)`.
* `Pembangkit Listrik Offgrid\Processes\*`: capacities from the off-grid block (PLTMH `Step(2021; 2.58; 2022; 2.68; 2023; 3.51; 2025; 2.71)`, PLTS komunal, PLTD) and `Maximum Availability` of the PLTD tuned to reproduce the diesel fuel (`90 × Interp(2021; 0.32; 2022; 0.36; 2023; 0.99)`).
* Demand `Total Energy` / intensity data blocks for fuels, so that total final energy and **primary supply** (`Resources`) match the mix.

**Check**: run Current Accounts, then compare (a) `Resources:Primary Supply` per fuel and (b) generation by technology with the sheet; the `Calibrated` column (`Ok`, `?`) in the sheet marks lines already checked.

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
| 3 | Primary supply by fuel (oil, coal, gas, EBT) vs Historical Energy Mix | ±5 % |
| 4 | Off-grid generation and PLTD fuel vs off-grid block of the Energy Mix | ±5 % |
| 5 | T&D losses vs PLN | as PLN reports |
| 6 | 2025→2026 step: no discontinuity larger than the growth assumption (check `Komersial`, tourists 20 %/yr) | judgement |

Open issues found while documenting are in [known-issues.md](known-issues.md).
