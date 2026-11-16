# RE Potential Map NTT: filters and grid-gap analysis

The map [`data/power/re_potential/RE Potential Map NTT (standalone).html`](../data/power/re_potential/) is a self-contained Leaflet page (IESR). It holds **102 utility-scale potential sites**, the existing grid (ESDM), the Gridfinder predicted grid and HOTOSM settlements. The Excel export of the filtered sites corresponds to [`RE Utility Scale Potential Site.xlsx`](../data/power/re_potential/).

## 1. All filter features

| Panel | Filter | Options | Effect |
|---|---|---|---|
| **RE Potential** | Technology → sub-technology checklist (each technology has a master tick) | **Solar**: Ground-mounted (14), FPV onshore/lakes (3), FPV offshore/marine (30) · **Wind**: Onshore (29), Offshore (9) · **Hydro**: Mini-hydro run-off (7), Dam (3) · **Geothermal**: Dry steam (3), Flash (4). The counter shows `(all)`, `(n/m)` or `(none)` | shows or hides sites; bubble size ∝ √MW (capacity AC, else DC) |
| **Economic filter (EIRR)** | radio | `All technical potential` · `EIRR > WACC (viable)` · `EIRR ≥ 10 % (strong)` | WACC per technology (editable in the code): Ground-mounted 6.96 %, FPV inland 6.04 %, FPV nearshore 7.58 %, Wind onshore 7 %, Wind offshore 7.58 %, Mini-hydro and Dam 6 %, Geothermal 9 %. Sites without a financial model (21 of 102 have no EIRR) are excluded by both EIRR filters |
| **Territory filter** | three levels, each a checklist | `Pulau / sistem` (island/system) → `Kabupaten / kota` → `Kecamatan` | applies to sites, substations, plants, settlements and to all counts |
| **Grid infrastructure** | Substations (GI) by voltage; Transmission lines by voltage; Existing power plants by fuel | voltage classes ≥500 kV, 275, 150, 70, ≤30 kV (MV); fuels Coal, Gas, Diesel/Oil, Hydro, Geothermal, Solar, Wind, Bioenergy, Other | each group has a master tick; plants are off by default |
| | **Gridfinder predicted grid** | on/off | teal lines, predicted from night-light analysis |
| **Settlements & grid gap** | Human settlements (HOTOSM) | on/off + `Place type` checklist: city, town, village, hamlet, isolated_dwelling, neighbourhood, other | purple points, shades by place type |
| | Kecamatan boundaries | on/off | dashed sub-regency outline |
| **Find nearest GI & sites** | click on the map or enter `lat`, `lon` + **Go** | search radius **10 km · 50 km · custom (1–500 km)** | snaps to the nearest substation and lists up to 30 in-scope sites within the radius, sorted by distance |
| **Download data (Excel)** | button | exports the *currently filtered* sites | Summary sheet (by technology / sub-technology / territory, nearest GI, total capacity per economic filter) plus a full-parameter sheet |
| **Insight (filtered)** | live panel | – | count and GW by technology, settlements in scope |

All filters combine (AND): a site is shown when its sub-technology, economic class and territory are all selected.

### Site attributes (columns of the Excel)

`tech, subcat, site_id, name, province, region, kab_kota, lat, lon, loc_src` (location source; `GI-snap` = approximate, snapped to the nearest GI) · `cap_dc, cap_ac` (+ units), `cf, aep_gwh` · resource: `irradiance, pr` (solar), `wind_speed, power_density` (wind), `head_m, flowrate, surface_runoff, volume_m3, retention_days` (hydro), `temp_reservoir, tech_type` (geothermal) · land: `land_status, area_ha, land_unit_cost_m2, land_total_cost` · grid: `voltage_level, nearest_gi, dist_gi_km, interconnection_cost, t_int_cost` · economics: `capex, opex` (+ units), `eirr, pirr, npv, der, prof_index, payback_yrs` · admin: `island, kabupaten, kecamatan`.

## 2. Estimating the un-accessed areas (grid gap)

**Idea**: a settlement is *probably not on a grid* when there is **no predicted or existing line near it**. Three layers are overlaid:

| Layer | What it is | Source |
|---|---|---|
| Settlements | OSM `place` nodes (HOTOSM export 2026-05-05): name, place type, population (mostly empty), no admin attributes | `hotosm_idn_populated_places_points_geojson`; the NTT map carries 3,858 NTT places already tagged with island, kabupaten and kecamatan |
| Gridfinder | predicted electricity grid lines from night-light analysis (Indonesia file `gridfinder_indonesia.geojson`, 10.8 MB; NTT clip in the map: 870 lines) | Gridfinder (night lights + road/land-use prediction) |
| ESDM lines / GI | known 70 and 150 kV lines (22) and substations (17) in NTT | ESDM, embedded in the map |

**Interactive use** in the map: tick *Human settlements* and *Gridfinder predicted grid* together (and ESDM lines + GI if wanted), filter by territory and place type; populated places with no teal line close by are the candidates. Click a place to read its distance in the popup panel and use *Find nearest GI* to list RE sites around it.

**Reproducible use**: [`scripts/grid_gap_analysis.py`](../scripts/grid_gap_analysis.py) computes the distance of every settlement to the nearest grid point (Gridfinder national file clipped to NTT, map Gridfinder and ESDM lines, lines densified to 0.5 km, numpy only) and classifies it:

| Class | Distance to nearest grid | Reading |
|---|---|---|
| `near-grid` | ≤ 1 km | likely reached by the grid |
| `gap-extension` | 1 – 5 km | extension candidate (MV line) |
| `remote` | > 5 km | candidate for mini-grid / stand-alone RE (`Offgrid`, PLTS komunal, PLTMH) |

```bash
python scripts/grid_gap_analysis.py \
  --html "data/power/re_potential/RE Potential Map NTT (standalone).html" \
  --gridfinder "D:/2026/FPV Crux/shp/gridfinder_indonesia.geojson" --near 1 --far 5
```

Outputs in [`data/power/re_potential/grid_gap/`](../data/power/re_potential/grid_gap/): `settlements_grid_distance.csv`, `summary_by_kabupaten.csv`, `summary_by_island.csv`, `summary_by_place_type.csv`.

### First result (thresholds 1 km / 5 km, 3,858 places)

| Island | Places | near-grid | gap-extension | remote | % remote |
|---|---:|---:|---:|---:|---:|
| Flores | 1,731 | 641 | 743 | 347 | 20.0 |
| Timor | 824 | 236 | 440 | 148 | 18.0 |
| Sumba | 636 | 47 | 71 | 518 | 81.4 |
| Alor | 320 | 93 | 143 | 84 | 26.2 |
| Lembata | 194 | 18 | 13 | 163 | 84.0 |
| Rote | 89 | 25 | 44 | 20 | 22.5 |
| Sabu | 64 | 12 | 28 | 24 | 37.5 |
| **NTT** | **3,858** | **1,072** | **1,482** | **1,304** | **33.8** |

Highest remote counts by kabupaten: Sumba Timur 306 (100 %), Lembata 163, Sumba Barat 143, Manggarai Barat 100, Alor 84, TTS 67, Flores Timur 64.

### How to read it (limits)

* **Screening, not a measurement.** Gridfinder predicts where a grid *probably* is from night lights; it under-detects in dim, low-demand areas. The 100 % remote of Sumba Timur is mostly the absence of any predicted line there, and the ESDM dataset in the map has no line or substation on Sumba. Treat very high shares as "no evidence of grid", and validate with PLN data (`Rasio Elektrifikasi`, desa berlistrik) before use.
* **Settlements are points, not population.** HOTOSM `population` is mostly empty, and OSM coverage is uneven (many hamlets unmapped). Count of places ≠ households.
* **Distance ≠ access.** A place close to a line may still be unconnected (and the reverse). Pick thresholds per voltage: 1 km ≈ low-voltage reach, 5 km ≈ MV extension.
* **Only 70/150 kV ESDM lines** are in the map; MV networks are represented by Gridfinder only.

### Use in the RUED LEAP model

The `remote` places give the pool for the **off-grid** pathway: `Rumah belum berlistrik` and `Rumah berlistrik nonPLN` in `Demand\Rumah Tangga` ([demand-rumah-tangga.md](structure/demand-rumah-tangga.md)) and the `PLTS Komunal Candidate`, `PLTMH` and `BESS` processes of `Pembangkit Listrik Offgrid` ([transformation.md](structure/transformation.md)). Scale the place counts to households with BPS data per kecamatan, compare with the electrification-ratio scenarios (`REOFF*`, `REPLN*`, [scenarios.md](scenarios.md)), and use the potential sites near `remote` places (use *Find nearest GI & sites* with a 10 km radius) as candidate locations.
