# Transformation

177 branches in 9 modules. Order matters in LEAP (top to bottom): `Transmisi dan Distribusi` → on-grid → off-grid → blending/biogas/pellet/charcoal/RDF.

| Module | Branches | Output fuel | Role |
|---|---:|---|---|
| `Transmisi dan Distribusi` | 2 | `PLN Electricity Ongrid` | loss between final demand and generation: `Losses = Interp(2019; 9.13; 2020; 5.79; 2021; 8.23; 2022; 12.08; 2023; 10.81)` % |
| `Pembangkit Listrik Ongrid` | 127 | `PLN Electricity Ongrid` | grid plants, capacity from Plexos (below) |
| `Pembangkit Listrik Offgrid` | 27 | `Offgrid Electricity`, `IUPTLS Electricity` | isolated systems |
| `Biodiesel Blending` | 6 | `Biodiesel` | blend % from `Key\Roadmap NZE` |
| `Bioethanol Blending` | 5 | `Green Pertamax` | blend % from `Key\Roadmap NZE` |
| `Biogas Production` | 4 | `Biogas` | `Animal Wastes` |
| `Biomass Pellet Production`, `Charcoal Production`, `RDF Production` | 4 each | pellet, charcoal, RDF | placeholders for fuel substitution |

All modules have `Optimize = No` (*Energy System Optimization* is off): capacities are exogenous.

## Pembangkit Listrik Ongrid

Processes follow the convention `<technology> Existing | Rencana | Candidate`:

| Technology | Existing | Rencana (RUPTL) | Candidate (Plexos extra) |
|---|:-:|:-:|:-:|
| PLTU (coal) | ✔ | ✔ | |
| PLTD (diesel) | ✔ | | |
| PLTMG (gas engine) | ✔ | ✔ | ✔ |
| PLTP (geothermal) | ✔ | ✔ | ✔ |
| PLTM (mini-hydro) | ✔ | ✔ | ✔ |
| PLTBm (biomass) | | ✔ | ✔ |
| PLTS (solar) | ✔ | ✔ | ✔ |
| PLTB (wind) | ✔ | ✔ | ✔ |
| PLT Laut (ocean) | | ✔ | ✔ |
| PLTS Atap (rooftop PV) | one process, capacity = `Key\Roadmap NZE\Target kapasitas PLTS atap ongrid` | | |
| BESS 4 Hours | | Planned | Candidate |

Key variables of every process (see [`variables_baseline.csv`](../../data/structure/variables_baseline.csv)):

| Variable | Use here |
|---|---|
| `Exogenous Capacity` | MW by year. **Current Accounts**: historical (e.g. PLTU `Step(2023; 147; 2024; 177; 2025; 177)`). **Scenarios**: `Step(2026; …; 2038; …)` pasted from Plexos ([power-plexos.md](../power-plexos.md)) |
| `Historical Production` | GWh 2021–2025 per technology, used to calibrate Current Accounts ([calibration.md](../calibration.md)) |
| `Dispatch Rule` | `FullCapacity` (Baseline, Moderate, Optimis) or `PercentShare` (`*with simulation` scenarios) |
| `Merit Order`, `Maximum Availability`, `Capacity Credit` | dispatch order and availability; PLTS / PLTB use yearly shapes `SolarProfileNTT`, `WindProfileNTT` |
| `Process Efficiency` | PLTU 30 %, PLTD 40 %, PLTS 13 % (rooftop) … |
| `Capital Cost`, `Fixed OM`, `Variable OM`, `Stranded Cost` | from sheet `Power Generation Specification` |
| `Feedstock Fuels\*` | fuel per process (coal, diesel, natural gas, hydrogen option for PLTMG, biomass cofiring in PLTU from `Roadmap NZE`) |

### Capacity in 2030 and 2038 (MW) from the three Plexos runs

| Technology | BaU 2030 | BaU 2038 | Moderate 2030 | Moderate 2038 | Optimis 2030 | Optimis 2038 |
|---|---:|---:|---:|---:|---:|---:|
| PLTU | 207 | 180 | 207 | 180 | 177 | 144 |
| PLTD | 156.7 | 0 | 156.7 | 0 | 156.7 | 0 |
| PLTGas | 390 | 820 | 370 | 450 | 120 | 120 |
| PLTP | 70 | 180 | 75 | 190 | 75 | 195 |
| PLTM/MH | 35.4 | 35.4 | 47.4 | 47.4 | 47.4 | 47.4 |
| PLTBio | 5 | 5 | 30.5 | 30.5 | 30.5 | 30.5 |
| PLTS | 107.7 | 207.7 | 432.7 | 782.7 | 457.7 | 1,417.7 |
| PLTB | 28.3 | 50.3 | 28.3 | 50.3 | 28.3 | 50.3 |
| PLT Laut | 20 | 20 | 20 | 20 | 20 | 20 |
| BESS | 126.3 | 248.3 | 310.3 | 440.3 | 314.3 | 669.3 |

Source: [`data/power/plexos/`](../../data/power/plexos/) (top table of each sheet).

## Pembangkit Listrik Offgrid

Processes: `PLTS`, `PLTD`, `PLTM`, `PLTMH`, `PLTS Atap`, `PLTHybrid`, `PLTS Komunal Candidate`, `BESS`, `BESS PLTS Komunal`.

* `PLTD` is the balancing plant (`Process Share = Remainder(100)`, `PercentShare` dispatch, 108.5 MW, merit order 2, fuel `Biodiesel`). Its availability is calibrated: `90 × Interp(2021; 0.32; 2022; 0.36; 2023; 0.99)`.
* `PLTS`, `PLTS Atap`, `PLTS Komunal Candidate` read `Key\Roadmap NZE\Target kapasitas PLTS\Target kapasitas PLTS atap offgrid`.
* `PLTM`, `PLTMH`, `PLTHybrid` carry the historical capacities of the Bauran Energi Daerah worksheets (e.g. PLTMH `Step(2021; 2.58; 2022; 2.68; 2023; 3.51; 2025; 2.71)`).
* Off-grid is calibrated with the **Bauran Energi Daerah worksheets** (on/off-grid capacity and generation by technology); there is no Plexos run for off-grid.

## Load Shapes

| Shape | Fuel | Variable |
|---|---|---|
| `PLN Electricity Ongrid` | grid | `YearlyShape(Kurva_Beban_NTT)` |
| `Offgrid Electricity` | off-grid | `YearlyShape(Kurva_Beban_NTT)` |
| `IUPTLS Electricity` | private utilities | `ShapeFlat` |

`Kurva_Beban_NTT` has 100 time slices (wet/dry × weekday/weekend × 24 hours …), see [`data/power/load_shapes/`](../../data/power/load_shapes/). Solar and wind profiles (`SolarProfileNTT`, `WindProfileNTT`) set the maximum availability of PLTS / PLTB.
