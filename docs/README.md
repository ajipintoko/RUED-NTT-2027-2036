# RUED NTT Model Documentation

Read in this order: **Overview → Dataflow → the sector page you work on → Power / Calibration**.

| Section | Page | What it answers |
|---|---|---|
| Overview | [overview.md](overview.md) | what the model is: trees, years, scenarios, conventions |
| Dataflow | [dataflow.md](dataflow.md) | block diagrams: data source → Key Assumptions → Demand (per sector) → Transformation; calibration; Plexos link |
| Structure | [Key Assumptions](structure/key-assumptions.md) | inputs 2019–2025 and projection expressions, Roadmap NZE levers |
| | [Rumah Tangga](structure/demand-rumah-tangga.md) · [Transportasi](structure/demand-transportasi.md) · [Komersial](structure/demand-komersial.md) · [Industri](structure/demand-industri.md) · [Lainnya](structure/demand-lainnya.md) | demand sectors |
| | [Transformation](structure/transformation.md) | T&D, on-grid, off-grid, blending; Plexos capacities |
| | [Resources, Effects, Indicators](structure/resources-effects.md) | fuels, emissions, comparison indicators |
| Scenarios | [scenarios.md](scenarios.md) | CA, BaU, Moderat, Optimis and 25 building blocks |
| Power | [power-plexos.md](power-plexos.md) | RUPTL → Plexos → LEAP and the open demand-generation gap |
| Calibration | [calibration.md](calibration.md) | Historical Energy Mix (DESDM) and PLN sales (UIW NTT) |
| RE potential | [re-potential-map.md](re-potential-map.md) | map filters; grid-gap analysis with Gridfinder and HOTOSM |
| Maintenance | [data-update.md](data-update.md) · [how-to.md](how-to.md) · [known-issues.md](known-issues.md) · [glossary.md](glossary.md) | yearly update, tracing, issues, terms |

Numbers on these pages come from the LEAP export of the area `RUED NTT 2027-2038 Agustus 2026` (`All LEAP Data.xlsx`). Re-run the scripts after a new export and update counts that change.
