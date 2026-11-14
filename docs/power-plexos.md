# Power system: RUPTL → Plexos → LEAP

## Principle

RUED NTT creates the **final energy demand** of the province; electricity is one of the fuels. The power system is, for now, **not optimised in LEAP** (`Optimize = No`). It is optimised in **Plexos**, using the **RUPTL** demand as the load basis, and the resulting capacities are pasted into LEAP as `Exogenous Capacity`:

| LEAP scenario | Plexos run (sheet in [`plexos_*.csv`](../data/power/plexos/)) | Meaning |
|---|---|---|
| **BaU** (`BAU`) | `RUPTL 2025 + Gas` | RUPTL 2025-2034 plus gas for additional capacity |
| **Moderat** (`MOD`) | `RUPTL + RE` | RUPTL plus renewable energy |
| **Optimis** (`OPT`) | `Substitusi RE` | RE substitutes fossil additions (PLTU Alor, Atambua cancelled) |

All three run on the **current existing NTT grid** (61 plants, [`existing_ntt_power_plants.csv`](../data/power/plexos/existing_ntt_power_plants.csv): node, region Flores / Timor / Sumba …, type, technology, fuel, net capacity, coordinates, Plexos name).

## Inputs

| File | Content | Used for |
|---|---|---|
| [`data/power/ruptl/c12_8_kebutuhan_listrik.csv`](../data/power/ruptl/c12_8_kebutuhan_listrik.csv) | RUPTL growth, sales (1,591 GWh in 2025 → 3,104 in 2034), production (1,831 → 3,534), peak load (317 → 586 MW), customers | Plexos load basis |
| `c12_1`, `c12_2`, `c12_6`, `c12_7` | sales and customers by group, actual and projected | calibration, indicators |
| `c12_3_kapasitas_pembangkit.csv` | installed, net and peak capacity by system | existing plants |
| `c12_9_skenario_re_base.csv`, `c12_10_skenario_ared.csv` | capacity additions per year by developer (PLN, PLN SH, IPP) and technology | `Rencana` processes |
| `c12_11_rincian_pembangunan.csv` | project list with COD, status, developer | `Rencana` processes |
| `potensi_pengembangan.csv` | RE development potential | Candidate limits |
| [`data/power/load_shapes/`](../data/power/load_shapes/) | load curve, solar and wind profiles | Plexos and LEAP load shapes |

## From Plexos to LEAP (procedure)

1. Open the Plexos result sheet (top table: **MW by type and year 2026–2038**; below it per-plant `Installed Capacity` and `Generation Capacity`, plus `Candidate` / `Planned` blocks for BESS, PLTB, PLTBio, …).
2. Map types to LEAP processes:

   | Plexos type | LEAP process(es) |
   |---|---|
   | PLTU | `PLTU Existing` + `PLTU Rencana` |
   | PLTD | `PLTD Existing` |
   | PLTGas | `PLTMG Existing` + `PLTMG Rencana` + `PLTMG Candidate` |
   | PLTP | `PLTP Existing` + `Rencana` + `Candidate` |
   | PLTM/MH | `PLTM Existing` + `Rencana` + `Candidate` |
   | PLTBio | `PLTBm Rencana` + `PLTBm Candidate` |
   | PLTS | `PLTS Existing` + `Rencana` + `Candidate` |
   | PLTB | `PLTB Existing` + `Rencana` + `Candidate` |
   | PLTLaut | `PLTLaut Rencana` + `PLTLaut Candidate` |
   | BESS | `BESS 4 Hours Planned` + `Candidate` |

   *Existing* = plants in the existing grid file, *Rencana* = RUPTL projects, *Candidate* = what Plexos adds beyond them. Check: BaU PLTGas in 2026 is 130 MW = `PLTMG Existing` 100 + `PLTMG Rencana` 30.
3. Paste as `Step(2026; x; 2027; y; …; 2038; z)` into `Exogenous Capacity` of the scenario (BAU for BaU; `RUPTLRE` for Moderat; `RUPTLREF` for Optimis).
4. Keep Current Accounts (2019–2025) as the historical capacity; 2026 is the first scenario year.

## The open gap: LEAP demand ≠ Plexos generation + losses

Plexos was run on the **RUPTL demand**, LEAP builds demand bottom-up. Therefore:

| | Plexos | LEAP |
|---|---|---|
| Demand basis | RUPTL sales / production / peak load | RUED bottom-up final demand |
| Losses | RUPTL loss assumption inside production | T&D `Losses` (5.8–12 %) |
| Capacity | optimised for RUPTL peak | exogenous copy |
| Result | generation by plant | generation = f(LEAP demand), dispatch rule |

So generation in LEAP **will not** equal Plexos generation. The indicators `Perbandingan demand listrik` show the demand difference to PLN/RUPTL by customer group.

### How to explore and close the gap

1. Run the `… with simulation` scenarios (`BAS`, `RUP`, `RUP1`): they use `PercentShare` dispatch so the LEAP generation shares can be compared with Plexos.
2. Export the **LEAP electricity demand** (`Demand: Final Energy Demand`, fuels `PLN Electricity Ongrid`, `Offgrid Electricity`, `IUPTLS Electricity`) for BaU, Moderat and Optimis, add T&D losses and use it as the **new load basis in Plexos** (scale the Plexos load by LEAP ÷ RUPTL per year, keep the `Kurva_Beban_NTT` shape).
3. Re-run the three Plexos pathways and paste the new capacities (procedure above). Repeat until the LEAP generation + losses ≈ Plexos generation.
4. Compare with [`calibration.md`](calibration.md): historical years must still reproduce PLN sales.

Until step 3 is done, treat generation, capacity factor and emission results of the power sector as **RUPTL-based**, and demand results as **RUED-based**.
