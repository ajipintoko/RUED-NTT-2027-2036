# Demand: Lainnya (other)

39 branches for loads that are not households, commercial buildings, industry or transport, many of which are **programmes** of the RUED (productive-use electrification, fisheries, salt, aquaculture, smelter).

| Group | Branches | Activity (units) | Intensity |
|---|---|---|---|
| Akses Air | PDAM, SWPS | 100 % | 0 (placeholder) |
| Chest Freezer Kantong Stunting | Chest Freezer | `Interp(2025; 3; 2026; 86; … 2030; 242)` units | 12 W × 8,766 h |
| Chest Freezer Pulau Kecil | Chest Freezer 600 lt, Es Flake 1.5 Ton | `Interp(2023; 0; 2025; 12 …)` units | 0.3 kW, 15 kW × 8,766 h |
| Cold Storage PPI | ABF 2 Ton, Cold Storage 10 Ton, IFM 2 Ton | units from 2019 (2 → 6 …) | 10–15 kW × 8,766 h |
| Industri Garam | Dewatering, Drying, Ionisation Packaging, Seawater Pumping | `Interp(2026; 0; 2027; 200000)` | 10–25 |
| Konstruksi dan Event | Layanan Khusus | *Total Energy* history | – |
| Penerangan | PJUTS (solar street lights), Penerangan Jalan Listrik PLN | PJU PLN: `Interp(2020; 36792 …)` | 424.86 |
| Perikanan | Perahu Nelayan | `Key\Transportasi\Laut\Rasio kepemilikan perahu motor nelayan` × `Key\Demografi\Sosioekomi\Jumlah bangunan_total` | 90–126 |
| Pertambangan | Smelter Ferromangan (Electricity Need, Kokas) | `Interp(2027; 300; 2030; 2000)` | 2,900 |
| Pertanian | Alsistan, Mesin Pencacah, PATS | 100 % | 0 (placeholder) |
| Tambak Udang | Aerasi, IPAL, Lighting, Processing Cold Storage, Water Pumping | `Interp(2026; 0; 2028; 52800)` | 200–5,000 |

Where an intensity is `0` the branch is only a structural placeholder (no data yet). The `Lainnya` electricity is added to `Industri` in the PLN comparison (`Industri RUED`).
