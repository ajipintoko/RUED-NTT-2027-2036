# Scenarios

All scenarios are listed in [`data/structure/scenarios.csv`](../data/structure/scenarios.csv). Only the expressions that differ from Baseline are stored in [`scenario_overrides.csv`](../data/structure/scenario_overrides.csv) (228 rows in total), so you can see exactly what each scenario changes.

## Tree (as in LEAP)

```
Current Accounts (CA)                      calibration 2019-2025
└── Baseline (BAU)                         BaU: RUPTL 2025 + Gas
    ├── Baseline with simulation (BAS)     PercentShare dispatch
    ├── RUPTL plus RE (RUPTLRE)            ── RUP  (with simulation)
    ├── RUPTL plus RE FosCan (RUPTLREF)    ── RUP1 (with simulation)
    ├── Rasio Elektrifikasi: REOFFM / REOFFO (off-grid) · RELTSHEM / RELTSHEO (LTSHE) · REPLNM / REPLNO (PLN)
    ├── Kendaraan Listrik: KLKOTA · KLKOTAIS
    ├── Konversi LPG: LPG · KON (with electric stoves)
    ├── BBM: PTMX · GPTMX → GPTMXKEN · BIODSL · BIODSLKN
    ├── PLTS Atap: PLTSA → PLTSASF
    ├── BIOGAS · BIO (cement biomass) · BUS
    ├── MOD  Moderate  (reported)
    └── OPT  Optimis   (reported)
```

## The three reported scenarios

| | **BaU** (`BAU`) | **Moderat** (`MOD`) | **Optimis** (`OPT`) |
|---|---|---|---|
| Power pathway | **RUPTL 2025 + Gas** (Plexos) | **RUPTL + RE** (Plexos) | **Substitusi RE** (Plexos) |
| Grid | current existing NTT grid | current existing NTT grid | current existing NTT grid |
| Inherits | Current Accounts | BAU + `REOFFM`, `KLKOTA`, `KON`, `PTMX`, `BIODSL`, `PLTSA`, `BIOGAS`, `RUPTLRE` | BAU + `REOFFO`, `KLKOTAIS`, `KON`, `BIODSLKN`, `GPTMXKEN`, `BIOGAS`, `BIO`, `PLTSA`, `RUPTLREF` |
| Electrification | BPS trend | 100 % in 2035 (off-grid route) | 100 % in 2030 |
| EV | target held at 2023 | e-car 62 → +22/yr; e-motor 551/yr by 2035 | same e-car; e-motor 30,000/yr by 2035 |
| Biodiesel | B40 from 2025 | stays B35 after 2024 | B35 → 40 % by 2035 |
| Cooking | trend | LPG remainder, kerosene → 0 (2060), electric stove 147,100 houses (2060) | same |
| Cement biomass | 4,294 : 15,872 (2021) | – | 60 % by 2060 |
| Rooftop PV on-grid | 9.7 MW | 1.3 MW (quota, `Interp(2028; 1.3)`) | same |
| PLTU Alor / Atambua | built | built | **cancelled** (`Pembatalan PLTU = True`) |

Building blocks that touch the same branch overwrite each other in order of the *Additional Scenarios* list in LEAP (see the Inheritance tab of `MOD` and `OPT`). When you add a scenario, check that no later block silently undoes an earlier one.

## Power-pathway scenarios and the "simulation" variants

| Scenario | Plexos pathway | What changes in LEAP |
|---|---|---|
| `BAU` | RUPTL 2025 + Gas | `Exogenous Capacity` of `Existing`, `Rencana` and `Candidate` processes (gas candidates PLTMG reach 820 MW in 2038) |
| `RUPTLRE` | RUPTL + RE | `PLTMG Candidate` = 0; `PLTP/PLTM/PLTBm/PLTS Candidate` and `PLTLaut Rencana` added or raised |
| `RUPTLREF` | Substitusi RE | all processes re-pasted; `PLTU Rencana` = 0, `PLTMG Rencana` = 20 MW, large `PLTS Candidate` (1,417 MW by 2038) |
| `BAS`, `RUP`, `RUP1` | – | `Dispatch Rule` = `PercentShare` on every on-grid process instead of `FullCapacity`; used to explore how LEAP dispatches against the Plexos pathway |

## Adding a scenario

1. In LEAP: *Manage Scenarios* → add under `Baseline`, then change only the branches that differ.
2. Put it in the *Additional Scenarios* of `MOD` / `OPT` if it belongs there.
3. Export All Data, run `scripts/export_structure.py`; the new rows appear in `scenario_overrides.csv`. Add a line to `scenarios.csv` and update this page.
