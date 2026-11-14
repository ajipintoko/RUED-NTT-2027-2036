# Resources, Effects and Indicators

## Resources (35)

| Type | Fuels |
|---|---|
| **Primary** (15) | Animal Wastes, Biogas, Biomass, Coal Sub bituminous, Ethanol, Geothermal, Hydro, Municipal Solid Waste, Natural Gas, RDF, Solar, Tidal, Wind, Wood, Woodchip Sawdust |
| **Secondary** (20) | Avtur, Biodiesel, Charcoal, Diesel, Hydrogen, … electricity fuels and refined products |

Price and cost data come from sheet `Resource` (coal, crude oil, natural gas price 1990–2060, and *Potensi EBT*: wind 29.6 GW, micro-hydro 693 MW, biomass 139 MW, biomass residues of cacao, coffee, paddy). `Resources\Secondary\Hydrogen` and `Diesel` *Production Cost* feed the fuel cost of the PLTMG processes.

## Effects

One effect, **Carbon Dioxide** (GWP from the effects screen). Emission factors are stored on the Demand and Transformation fuel branches (`Avg Environmental Loading`, `New Device Environmental Loading`; 517 emission-factor branches in Demand). Biofuel blends split CO2 into fossil and `Carbon Dioxide Biogenic` using the blend % of `Key\Roadmap NZE`, e.g. `((100 − biodiesel %)/100) × 20.2 × FractionOxidized × (CO2/C)`.

## Indicators (35)

| Group | Content |
|---|---|
| `Emisi GRK`, `Emisi GRK per kapita` | total and per-capita emissions |
| `Energi Final`, `Energi final per kapita`, `Intensitas energi final` | final demand (TOE) |
| `Energi Primer`, `Intensitas energi primer` | `Resources:Primary Supply` |
| `Konsumsi listrik per kapita` | electricity per capita, per household (PLN and off-grid), target lines (SEB, KEN) |
| `Indikator Lainnya` | e.g. energy per m² of retail |
| **`Perbandingan demand listrik`** | **RUED vs PLN electricity by customer group**: `Rumah Tangga / Komersial / Industri` × `PLN` (typed from PLN sales and RUPTL projection 2015–2034) and `RUED` (LEAP results, GWh); totals `Total_Listrik PLN` and `Total_Listrik RUED` |

`Perbandingan demand listrik` is the on-screen electricity calibration check; see [calibration.md](../calibration.md).
