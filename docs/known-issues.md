# Known issues and things to check

Found while reading the expressions for this documentation. They are **observations from the exported expressions**, not confirmed errors: open the branch in LEAP and decide.

| # | Where | Observation | Suggested action |
|---|---|---|---|
| <a id="1"></a>1 | `Key\Demografi\Sosioekomi\Jumlah bangunan pedesaan` | divides by `Rata rata jumlah anggota keluarga **perkotaan**` and `keluarga per rumah **perkotaan**` (urban), not the rural series that exist next to them | use the `pedesaan` variables if the intent is rural households |
| <a id="2"></a>2 | `Indicators\Perbandingan demand listrik\Komersial PLN` and `Industri PLN` | `Komersial PLN` = Industri series (42, 38, 35 … ) + Publik series (83, 94 …); **Bisnis (174, 202 …) is missing**. `Industri PLN` = the same Industri series, so `Total_Listrik PLN` counts Industri twice and omits Bisnis | Komersial PLN = Bisnis + Layan Khusus + Publik + Sosial ([PLN data](calibration.md)) |
| 3 | `Indicators\...\*PLN` | series stop at the RUPTL prognosa (2024) and projection (2025 = 1,592 GWh); new PLN UIW NTT actuals for 2024 and 2025 exist | replace with [`pln_uiw_ntt_actual_sales_2020_2025.csv`](../data/calibration/pln_uiw_ntt_actual_sales_2020_2025.csv) |
| 4 | Power sector | Plexos ran on the RUPTL demand; LEAP generation ≠ Plexos generation + losses | [power-plexos.md](power-plexos.md) |
| 5 | `Key\Roadmap NZE\Target kapasitas PLTS\Target kapasitas PLTS atap ongrid` | Baseline = 9.7 MW from 2026; `PLTSA`, `MOD`, `OPT` set `Interp(2028; 1.3)` (smaller than Baseline) | confirm that a quota scenario should lower the rooftop PV |
| 6 | `BIODSL` / `MOD` | `Persentase biodiesel pada solar` = `Step(…; 2024; 35)` while Baseline continues to 40 % in 2025: Moderate has *less* biodiesel than BaU | confirm intent (B35 freeze) |
| 7 | `PTMX`, `GPTMX`, `GPTMXKEN` | identical exported overrides | confirm that the Green Pertamax difference sits in untouched branches |
| 8 | `BIOGAS`, `BUS` scenarios | no expression differs from Baseline | confirm they are placeholders |
| 9 | `Key\Rumah Tangga\Load Factor\Lampu`, `Rice Cooker` | exported as `True` (a boolean) instead of a fraction | set to `1` explicitly |
| 10 | Naming | `Rice Coker` vs `Rice Cooker`, `TV datar` vs `TV Datar` in `Key\Rumah Tangga` | harmless, but breaks name-based matching |
| 11 | Area root | branch paths start with `RUED NTT 20242034`, the file is `RUED NTT 2027-2038 Agustus 2026` | cosmetic |
| 12 | `Key\Roadmap NZE\Target penurunan emisi`, `Target bauran EBT` | reference values only, not read by any branch | none |
| 13 | Files | `All LEAP Data.xlsx` and `Plexos Result to LEAP.xlsx` were open in Excel when the repository was prepared; the copies in `data/` are complete, the loose copies in the project root can be deleted | delete after closing Excel |
| <a id="14"></a>14 | Calibration: PLTP generation | ESDM worksheet generation = capacity × CF (PLTP 24.08 MW × 0.9 = 189.9 GWh in 2025); LEAP `Historical Production` of `PLTP Existing` = 52.06 GWh (PLN actual) | keep PLN actual production for LEAP; treat the worksheet GWh as a theoretical maximum; document which source each process uses |
| 15 | Bauran Energi Daerah workbooks | 2021 includes firewood (5.64 million BOE), 2022-2025 do not; LTSHE 2021 = 312.5 GWh (probably a unit error); Avtur 2025 = 399 kL vs about 32-36 thousand kL in 2022-2024 | see the `README` sheet of `Bauran_Energi_Daerah_NTT_2021-2025.xlsx` and [calibration.md](calibration.md#data-flags-see-the-workbook-readme-sheet) |
