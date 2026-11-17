# Dataflow

How a number travels from a data source to a result, and which part of the model reads which. Link counts come from [`data/dataflow/sector_links.csv`](../data/dataflow/sector_links.csv) (Baseline); every individual link is in [`branch_links.csv`](../data/dataflow/branch_links.csv) and the grouped views are in [`key_to_demand_by_source.csv`](../data/dataflow/key_to_demand_by_source.csv) and [`transformation_inputs.csv`](../data/dataflow/transformation_inputs.csv).

## 1. End to end

```mermaid
flowchart TD
    SRC["Data sources<br/>BPS, Dinas, PLN UIW NTT, ESDM energy-mix worksheets,<br/>RUPTL 2025-2034, ministries"]
    XL["Data untuk RUED NTT 2024.xlsx<br/>(data/inputs/*.csv)"]
    KEY["LEAP Key Assumptions<br/>data blocks 2019-2025<br/>+ projection expressions"]
    DEM["Demand tree<br/>activity x intensity / total energy / device share"]
    TRF["Transformation<br/>T&D, on-grid, off-grid, blending"]
    RES["Resources<br/>primary supply, imports"]
    OUT["Results<br/>final energy, capacity, supply, emissions"]
    REP["data/results<br/>RUED report tables"]
    PLX["Plexos power model<br/>(RUPTL demand, existing NTT grid)"]
    CAL1["Bauran Energi Daerah 2021-2025<br/>ESDM worksheets"]
    CAL2["Penjualan Tenaga Listrik GWh<br/>PLN UIW NTT"]

    SRC --> XL --> KEY
    KEY -->|activity drivers, intensities, shares| DEM
    KEY -->|targets: PV, biodiesel, cofiring| TRF
    DEM -->|final demand by fuel<br/>incl. electricity| TRF
    PLX -->|Exogenous Capacity by technology| TRF
    TRF -->|primary requirements| RES
    DEM --> OUT
    TRF --> OUT
    RES --> OUT
    OUT --> REP
    CAL1 -. Historical Production, Total Energy .-> TRF
    CAL1 -. Total Energy per fuel .-> DEM
    CAL2 -. Indicators: Perbandingan demand listrik .-> OUT
    CAL2 -. T&D losses .-> TRF
```

Solid lines are calculations inside LEAP or data entered into LEAP. Dotted lines are **calibration** or **comparison** links (see [calibration.md](calibration.md)).

## 2. Calculation order inside LEAP

For each year and scenario LEAP:

1. Evaluates the **Key Assumptions** expressions (population → households, GDP → sector value added, vehicle sales …).
2. Evaluates **Demand** from the leaves up: Total Activity of a branch is the product of the activity levels on its path; energy = activity × Final Energy Intensity (or the Total Energy entered directly; or stock × mileage ÷ fuel economy for vehicles). The sum by fuel is the final demand.
3. Runs **Transformation** top to bottom. T&D adds losses to the electricity requirement; the on-grid module meets the requirement with its processes (*FullCapacity* or *PercentShare* dispatch, see [transformation.md](structure/transformation.md)); the off-grid module meets `Offgrid Electricity`; blending modules meet biodiesel / green pertamax.
4. Passes the fuel requirements of the processes to **Resources** (primary supply and imports).
5. Applies the emission factors (**Effects**) to fuel use in Demand and Transformation, and evaluates the **Indicators**.

## 3. Who reads whom

Number of references between trees in the Baseline expressions (from `sector_links.csv`).

| Reading tree / sector | Reads from | Links | Reading branches |
|---|---|---:|---:|
| Demand \ Komersial | Key \ Bangunan Komersial | 54 | 18 |
| Demand \ Komersial | Key \ Demografi | 8 | 2 |
| Demand \ Komersial | Key \ Populasi | 4 | 4 |
| Demand \ Rumah Tangga | Key \ Rumah Tangga | 30 | 9 |
| Demand \ Rumah Tangga | Key \ Roadmap NZE (biogas, electric stove) | 2 | 2 |
| Demand \ Rumah Tangga | Key \ Demografi (buildings) | 1 | 1 |
| Demand \ Transportasi | Key \ Transportasi | 21 | 12 |
| Demand \ Transportasi | Key \ Roadmap NZE (EV, biofuel) | 8 | 8 |
| Demand \ Industri | Key \ Roadmap NZE (biodiesel, biomass in cement) | 14 | 14 |
| Demand \ Industri | Key \ Makroekonomi (GDP of industry sub-sectors) | 5 | 5 |
| Demand \ Lainnya | Key \ Demografi, Key \ Transportasi | 2 | 2 |
| Transformation \ Ongrid | Key \ Roadmap NZE (rooftop PV, cofiring, biodiesel) · Resources \ Secondary (fuel cost) | 5 + 4 | 5 + 4 |
| Transformation \ Offgrid | Key \ Roadmap NZE (off-grid PV, biodiesel) | 5 | 5 |
| Transformation \ Biodiesel / Bioethanol blending | Key \ Roadmap NZE | 1 + 1 | 1 + 1 |
| Key \ Bangunan Komersial | Key \ Bangunan Komersial (internal) · Demografi · Populasi | 67 · 10 · 5 | 21 · 5 · 5 |
| Key \ Demografi | Key \ Demografi (internal) · Populasi · Urbanisasi | 92 · 12 · 2 | 37 · 12 · 2 |
| Key \ Makroekonomi | Key \ Roadmap NZE (GDP growth) · Populasi · Makroekonomi | 1 each | 1 each |
| Key \ Transportasi | Key \ Roadmap NZE (EV share) · Transportasi | 3 + 3 | 3 + 3 |
| Indicators | Demand, Key (Populasi, Makroekonomi) | – | see CSV |

Two things to notice:

* **Roadmap NZE is the policy hub.** The 24 branches under `Key\Roadmap NZE` (EV sales, electric stoves, biogas, biodiesel and bioethanol blend, biomass share in cement, rooftop PV, PLTU cancellation …) are what the building-block scenarios change. They feed Demand, Transformation and Key.
* **Demand → Key feedback**: `Key\Roadmap NZE\...\Target pengguna kompor listrik` reads `Demand\Rumah Tangga\Aktivitas Memasak:Total Activity`, and `Key\Rumah Tangga\Rumah dengan Daya Besar\...` reads the electric-stove share of Demand. These are resolved inside the year calculation.

## 4. Sector flows (Key assumption → Demand → fuel)

Each block shows the chain as written in the expressions. Detailed branch lists are in the sector pages.

### 4.1 Rumah Tangga (households)

```mermaid
flowchart LR
    POP["Key\Populasi<br/>Growth(Pertumbuhan penduduk)"] --> HH
    URB["Key\Urbanisasi %"] --> HH
    FAM["Anggota keluarga,<br/>keluarga per rumah"] --> HH["Key\Demografi\Sosioekomi<br/>Jumlah bangunan (urban + rural)"]
    ELEC["Key\Rumah Tangga<br/>Rumah berlistrik PLN / non PLN<br/>LogisticForecast"] --> ACT
    HH -->|Total Activity<br/>Building| ACT["Demand\Rumah Tangga<br/>Aktivitas Lainnya, Aktivitas Memasak"]
    APP["Key\Rumah Tangga<br/>kepemilikan x daya x load factor<br/>x jam harian"] -->|Final Energy Intensity| APPL["PLN households:<br/>AC, Kulkas, Lampu, TV ... "]
    ACT --> APPL
    NZE["Key\Roadmap NZE<br/>kompor listrik, biogas"] --> COOK["Memasak:<br/>LPG, Kerosene, Wood,<br/>Kompor Listrik, Biogas"]
    ACT --> COOK
    APPL -->|PLN Electricity Ongrid| T1["T&D → On-grid"]
    ACT -->|nonPLN: Offgrid Electricity, LTSHE| T2["Off-grid"]
    COOK -->|LPG, Kerosene, Biomass| R1["Resources"]
```

### 4.2 Transportasi

```mermaid
flowchart LR
    ST["Key\Transportasi\Darat\Stok<br/>Mobil, Bus, Truk, Sepeda Motor"] --> VEH
    SL["Key\Transportasi\Darat\Penjualan<br/>Roda 2, Roda 4, Roda 6 (LinForecast)"] --> SH["Share_Penjualan<br/>bensin / diesel / listrik"]
    NZE["Key\Roadmap NZE<br/>target mobil, motor, bus listrik"] --> SH
    SH -->|Sales| VEH["Demand\Transportasi\Darat<br/>vehicle type: Stock, Sales, Mileage"]
    VEH --> FUEL["fuel: Device Share, Fuel Economy<br/>Pertalite, Pertamax, Green Pertamax,<br/>Diesel, Biodiesel, PLN Electricity"]
    BL["Key\Roadmap NZE<br/>% biodiesel, % bioethanol"] --> FUEL
    SEA["Key\Transportasi\Laut<br/>penumpang, per trip, L per trip"] --> LAUT["Demand\Transportasi\Laut<br/>Diesel, MFO"]
    AIR["Key\Transportasi\Udara<br/>penumpang, per trip, L per trip"] --> UDARA["Demand\Transportasi\Udara<br/>Jet Kerosene"]
    FUEL --> BLD["Blending modules<br/>Biodiesel, Green Pertamax"]
    FUEL -->|PLN Electricity Ongrid| TD["T&D → On-grid"]
```

### 4.3 Komersial

```mermaid
flowchart LR
    POP["Key\Populasi"] --> SCH
    AGE["Key\Demografi\Angkatan Sekolah<br/>usia, APS"] --> SCH["Key\Bangunan Komersial\Sekolah<br/>pelajar → kelas → luasan"]
    POP --> HOS["Key\...\Fasilitas Kesehatan<br/>tempat tidur, unit, luasan"]
    TOUR["Key\Roadmap NZE<br/>pertumbuhan wisatawan"] --> HOT["Key\...\Akomodasi dan Hotel<br/>wisatawan → bed → kamar → m2"]
    LAB["Key\Demografi\Ketenagakerjaan<br/>% sektor komersial"] --> OFF["Kantor: pekerja x m2"]
    EXP["Key\Makroekonomi\Expense per Capita"] --> RET["Key\...\Retail<br/>jumlah unit x ukuran"]
    SCH --> DC["Demand\Komersial<br/>Sekolah, Faskes, Hotel, Kantor, Retail<br/>Activity = floor area (m2)"]
    HOS --> DC
    HOT --> DC
    OFF --> DC
    RET --> DC
    PUB["Program: KDMP, SPPG<br/>(Fasilitas Publik, entered directly)"] --> DC
    DC -->|"Final Energy Intensity (kWh/m2)"| EL["PLN Electricity Ongrid, BBM"]
```

### 4.4 Industri

```mermaid
flowchart LR
    GDP["Key\Roadmap NZE\Pertumbuhan PDB"] --> PDB["Key\Makroekonomi\PDB harga konstan 2010"]
    PDB --> SUB["Kontribusi PDB per sektor<br/>PDB subsektor industri"]
    SUB -->|Activity Level| IND["Demand\Industri<br/>Makanan, Minuman, Tekstil, Furnitur,<br/>Karet dan Plastik, Barang Galian Bukan Logam"]
    UM["UMKM (by PLN tariff class)"] --> IND
    HIST["Total Energy per fuel<br/>2019-2025 (data block)<br/>then GrowthAs(Total Activity)"] --> IND
    NZE["Key\Roadmap NZE<br/>% biodiesel, % biomass di semen"] --> IND
    IND --> F["Fuels: PLN Electricity, IUPTLS Electricity, Diesel,<br/>Gasoline, LPG, Coal, Biomass, Biodiesel ..."]
```

### 4.5 Lainnya

`Lainnya` collects the sectors that do not fit the others and many *programme-driven* loads: Akses Air (PDAM, SWPS), Chest Freezer, Cold Storage PPI, Industri Garam, Konstruksi dan Event, Penerangan (PJUTS, PJU PLN), Perikanan, Pertambangan (Smelter Ferromangan), Pertanian, Tambak Udang. Activity is mostly entered as `Interp(...)` of units and the intensity as kW × 8,766 h. Only Perikanan (`Key\Transportasi\Laut\Rasio kepemilikan perahu motor nelayan`) and one building count (`Key\Demografi\Sosioekomi\Jumlah bangunan_total`) read from Key.

## 5. Demand to Transformation

```mermaid
flowchart LR
    subgraph D["Demand: final energy by fuel"]
        E1["PLN Electricity Ongrid"]
        E2["Offgrid Electricity"]
        E3["IUPTLS Electricity"]
        F1["Diesel / Biodiesel"]
        F2["Pertalite / Pertamax / Green Pertamax"]
        F3["LPG, Kerosene, Wood, Biomass, Coal ..."]
    end
    E1 --> TD["Transmisi dan Distribusi<br/>Losses (%)"] --> ON["Pembangkit Listrik Ongrid<br/>PLTU, PLTD, PLTMG, PLTP, PLTM, PLTBm,<br/>PLTS, PLTB, PLT Laut, BESS"]
    E2 --> OFF["Pembangkit Listrik Offgrid<br/>PLTD, PLTS, PLTS Atap, PLTM(H),<br/>PLTHybrid, BESS"]
    E3 --> IU["no module: flat load shape"]
    F1 --> BD["Biodiesel Blending<br/>(% from Key\Roadmap NZE)"]
    F2 --> BE["Bioethanol Blending"]
    ON --> RS["Resources (coal, gas, geothermal,<br/>hydro, solar, wind, biomass)"]
    OFF --> RS
    F3 --> RS
```

## 6. Calibration flow

| What is calibrated | Against | Where it enters LEAP | Years |
|---|---|---|---|
| Overall energy consumption and **primary energy** per fuel (BBM, coal, EBT, biomass, biogas) | **Bauran Energi Daerah worksheets** (ESDM template, NTT 2021–2025): BBM in kL → BOE, coal, gas, EBT | Demand data blocks (`Total Energy`, `Interp` / `Step` series) in Current Accounts; checked against Resources primary supply | 2021–2025 |
| **Off-grid** (and on-grid) generation by technology | Bauran Energi Daerah, electricity part (installed MW on/off-grid, generation GWh) | `Exogenous Capacity` and `Historical Production` of each process in Current Accounts; Offgrid capacities | 2021–2025 |
| Electricity load | **Penjualan Tenaga Listrik GWh** (PLN UIW NTT; RUPTL C12.1/C12.6) | Indicators `Perbandingan demand listrik` (RUED vs PLN by customer group); T&D `Losses` | 2015–2034 |
| Load shape | RUPTL / PLN hourly load (`Kurva_Beban_NTT`) | `Load Shapes` branches | typical year |

See [calibration.md](calibration.md) for the step-by-step check.

## 7. Power system flow (Plexos ↔ LEAP)

```mermaid
flowchart LR
    RUPTL["RUPTL 2025-2034<br/>sales, production, peak load,<br/>projects, RE Base / ARED"] --> PLX
    EX["Existing NTT plants<br/>(existing_ntt_power_plants.csv)"] --> PLX
    PLX["Plexos (3 runs)"] --> BAU["RUPTL 2025 + Gas"]
    PLX --> MOD["RUPTL + RE"]
    PLX --> OPT["Substitusi RE"]
    BAU -->|MW by technology, 2026-2038| LB["LEAP Baseline<br/>Exogenous Capacity<br/>Existing / Rencana / Candidate"]
    MOD --> LM["LEAP Moderate<br/>(RUPTLRE overrides)"]
    OPT --> LO["LEAP Optimis<br/>(RUPTLREF + new Candidates)"]
    LB --> GEN["LEAP generation = f(LEAP demand)"]
    LM --> GEN
    LO --> GEN
    GEN -. "does not yet equal Plexos generation + losses" .- PLX
```

Details and the procedure to close the gap: [power-plexos.md](power-plexos.md).
