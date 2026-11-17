"""Compile the yearly 'Worksheet Perhitungan Bauran Energi Daerah - Provinsi NTT' workbooks (2021-2025)
into one workbook used for the ESDM calibration of the LEAP model.

Each yearly workbook (ESDM template filled for NTT) has a sheet 'Data Energi' (input template, mostly the
province totals) and a sheet 'Worksheet' (calculation: original unit -> BOE -> TOE, and the energy mix).
This script reads the *values* of the 'Worksheet' sheets by label (row positions differ slightly between
years), normalises the item names and writes:

    data/calibration/Bauran_Energi_Daerah_NTT_2021-2025.xlsx
        README                 what is what, and method differences between years
        Ringkasan_Bauran       energy mix per year (EBT, Minyak Bumi, Gas Bumi, Batubara): BOE, TOE, MTOE, %
        Pivot_Konsumsi         fuels by year: value in original unit and in BOE
        Pivot_Listrik          capacity (on/off grid, MW) and generation (on/off grid, GWh) by technology
        Worksheet_Long         every row of every yearly worksheet (tidy, with source file and row)
        DataEnergi_Input       non-empty inputs of the 'Data Energi' sheets (tidy)
        Kegiatan_2022          programme list of 2022 ('keg 2022')
    data/calibration/bauran_energi/*.csv   the same sheets as CSV (text, diff-able)

Usage   python scripts/compile_bauran_energi.py [--dir-2021 ... ] (defaults to the five files of the project)
Requires pandas and openpyxl.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import openpyxl
import pandas as pd
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = {
    2021: r"D:\2025\Modelling\RUED\Worksheet Perhitungan Bauran Energi Daerah -- Provinsi NTT 2021-edit sas.xlsx",
    2022: r"D:\2025\Modelling\RUED\Worksheet Perhitungan Bauran Energi Daerah -- Provinsi NTT- 2022 ok.xlsx",
    2023: r"D:\2025\Modelling\RUED\Worksheet Perhitungan Bauran Energi Daerah -- Provinsi New tanpa kayu bakar 2023.xlsx",
    2024: r"D:\2026\RUED NTT\Update data\Worksheet Perhitungan Bauran Energi Daerah -- Provinsi New tanpa kayu bakar 2024.xlsx",
    2025: r"D:\2026\RUED NTT\Update data\Worksheet Perhitungan Bauran Energi Daerah -- Provinsi New 2025.xlsx",
}
SECTIONS = {"MINYAK BUMI": "Minyak Bumi", "GAS BUMI": "Gas Bumi", "BATUBARA": "Batubara",
            "ENERGI BARU TERBARUKAN": "EBT"}
MIX_ORDER = ["EBT", "Minyak Bumi", "Gas Bumi", "Batubara"]


def clean(v):
    if isinstance(v, str):
        v = v.replace("\n", " ").replace("\xa0", " ").strip()
        return v or None
    return v


def norm_item(section: str, group: str, item: str) -> tuple[str, str]:
    """-> (normalised item, blend label). Blends (B20/B30/B35/B40, E5) change between years."""
    s = (item or "").strip()
    blend = ""
    m = re.search(r"\bB(\d{2})\b", s)
    if m:
        blend = "B" + m.group(1)
    low = s.lower()
    if group and group.strip().upper() == "FAME":
        return "FAME (semua campuran B)", blend or s
    if group and group.strip().lower() == "etanol":
        return "Etanol (E5)", s
    if "solar" in low and "murni" in low:
        return "Solar 48/51/53 (murni)", ""
    if "solar" in low:
        return "Biosolar 48/51 (campuran B)", blend
    if low.startswith("ron 98"):
        return "Ron 98/95", ""
    if low.startswith("ron 90"):
        return "Ron 90/88/89", ""
    if low.startswith("minyak bakar"):
        return "Minyak Bakar 180/380 (MFO)", ""
    return s, blend


def read_year(year: int, path: str):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb["Worksheet"]
    rows = [[clean(v) for v in r] + [None] * 14 for r in ws.iter_rows(values_only=True)]
    file_year = None
    for r in rows[:5]:
        if r[1] and str(r[1]).strip().upper().startswith("TAHUN"):
            file_year = r[4]
    assert file_year in (None, year), f"{path}: TAHUN={file_year}"
    recs, mix = [], []
    section = group_no = group = block = None
    for n, r in enumerate(rows, 1):
        b, c, d, e, f, g, h, i, j, k, l = r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11]
        if isinstance(b, str) and b.upper() in SECTIONS and not isinstance(h, (int, float)):
            section, group, block = SECTIONS[b.upper()], None, "Konsumsi"
            continue
        if isinstance(b, str) and b.upper().startswith("BAURAN ENERGI"):
            block, section = "Bauran", None
            continue
        if block == "Bauran":
            if isinstance(e, (int, float)) and (c or b):
                mix.append(dict(Tahun=year, Sumber=str(c or b).strip(), BOE=e, TOE=f, MTOE=g, Persen=h))
            continue
        if isinstance(c, str) and c.startswith("Total Kapasitas"):
            block, group = "Kapasitas terpasang", None
            continue
        if isinstance(c, str) and c.startswith("Total Produksi"):
            block, group = "Produksi listrik", None
            continue
        if isinstance(b, str) and (b.startswith("Total Pasokan") or b.startswith("Total")):
            recs.append(dict(Tahun=year, Baris=n, Bagian=section or "", Blok="Total", Grup="", No="", Item=b.strip(),
                             Satuan="", Faktor_BOE=None, CF_Efisiensi=None, Nilai=None, Off_grid=None, BOE=j, TOE=k, Catatan=None))
            continue
        if isinstance(c, str) and c.startswith("Subtotal"):
            recs.append(dict(Tahun=year, Baris=n, Bagian=section or "", Blok="Subtotal", Grup="", No="", Item=c.strip(),
                             Satuan="", Faktor_BOE=None, CF_Efisiensi=None, Nilai=None, Off_grid=None, BOE=j, TOE=k, Catatan=None))
            continue
        # group rows: roman number in B and label in C (may carry its own values: gas, coal, EBT)
        if isinstance(b, str) and re.fullmatch(r"[IVX]+\s*", b) and c:
            group_no, group = b.strip(), str(c).strip()
            if group == "Pembangkit Energi Terbarukan":
                continue
            if isinstance(i, (int, float)) or isinstance(h, (int, float)):
                recs.append(dict(Tahun=year, Baris=n, Bagian=section or "", Blok=block, Grup=group, No=group_no, Item=group,
                                 Satuan=g, Faktor_BOE=h, CF_Efisiensi=None, Nilai=i, Off_grid=None, BOE=j, TOE=k, Catatan=l))
            continue
        # item rows: running number in D and label in E
        if isinstance(d, (int, float)) and e:
            item = str(e).strip()
            if block == "Kapasitas terpasang":
                recs.append(dict(Tahun=year, Baris=n, Bagian="EBT", Blok=block, Grup="Pembangkit Energi Terbarukan", No=d, Item=item,
                                 Satuan="MW", Faktor_BOE=None, CF_Efisiensi=f, Nilai=h, Off_grid=i, BOE=None, TOE=None, Catatan=None))
            elif block == "Produksi listrik":
                recs.append(dict(Tahun=year, Baris=n, Bagian="EBT", Blok=block, Grup="Pembangkit Energi Terbarukan", No=d, Item=item,
                                 Satuan="GWh", Faktor_BOE=None, CF_Efisiensi=f, Nilai=h, Off_grid=i, BOE=j, TOE=k, Catatan=None))
            else:
                recs.append(dict(Tahun=year, Baris=n, Bagian=section or "", Blok=block, Grup=group or "", No=d, Item=item,
                                 Satuan=g, Faktor_BOE=h, CF_Efisiensi=None, Nilai=i, Off_grid=None, BOE=j, TOE=k, Catatan=l))
    return recs, mix


def read_inputs(year: int, path: str) -> list[dict]:
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb["Data Energi"]
    out, sec, grp = [], None, None
    for n, row in enumerate(ws.iter_rows(values_only=True), 1):
        r = [clean(v) for v in row] + [None] * 16
        if r[2] and isinstance(r[2], str) and not r[3] and r[2] in ("Minyak Bumi", "Batubara", "Gas Bumi", "Energi Baru Terbarukan (EBT)", "Listrik"):
            sec = r[2]
        label = r[4] if isinstance(r[3], (int, float)) else (r[3] if r[3] else r[2])
        vals = [(idx, v) for idx, v in enumerate(r[5:16], 5) if isinstance(v, (int, float)) and idx != 3]
        if isinstance(label, str) and vals and "......" not in label and "dst" not in label:
            out.append(dict(Tahun=year, Baris=n, Bagian=sec, Item=label, Satuan=r[7],
                            Nilai_1=vals[0][1], Nilai_2=vals[1][1] if len(vals) > 1 else None, Kolom_sumber=vals[0][0]))
    return out


def autosize(ws):
    ws.freeze_panes = "A2"
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="1B5E20")
    for i, col in enumerate(ws.columns, 1):
        w = max((len(str(c.value)) for c in col[:200] if c.value is not None), default=8)
        ws.column_dimensions[get_column_letter(i)].width = min(max(10, w + 2), 60)


README = [
    ["Bauran Energi Daerah Provinsi NTT 2021-2025: compiled ESDM calibration data"],
    [""],
    ["Source", "5 yearly workbooks 'Worksheet Perhitungan Bauran Energi Daerah - Provinsi NTT' (ESDM template filled for NTT), one per year 2021-2025"],
    ["Use", "Calibration of Current Accounts in the RUED NTT LEAP model: overall (primary) energy consumption by fuel and off-grid / on-grid renewable generation. Replaces the former 'Historical Energy Mix' workbook."],
    ["Units", "Original unit (KL, ton, mscf, m3/year, MW, GWh) -> BOE using the 'Faktor_BOE' column -> TOE (1 TOE = 7.1429 BOE as in the worksheets) -> MTOE."],
    ["Sheets", "Ringkasan_Bauran, Pivot_Konsumsi, Pivot_Listrik, Worksheet_Long, DataEnergi_Input, Kegiatan_2022"],
    [""],
    ["Method differences between years (read before comparing)"],
    ["Kayu bakar", "Only 2021 includes firewood (Kayu Bakar 2,200,020 ton = 5.64 million BOE, which makes EBT 53 % that year). In 2022-2025 firewood is 0 (the 2023, 2024 and 2025 workbooks are 'tanpa kayu bakar'). The 2021 EBT share and total are NOT comparable with later years; use Ringkasan_Bauran (block 'tanpa kayu bakar')."],
    ["Biodiesel blend", "Biosolar blend changes by year (B30 in 2021, B35 in 2023-2024, B40 in 2025; see the Campuran column of Worksheet_Long). Pivot_Konsumsi sums the blends into one line."],
    ["BOE factors", "Coal is 3.442 BOE/ton in 2021 and 3.455 in 2025 (check the 'Faktor_BOE' column); fuel factors can differ slightly between years."],
    ["Biomass", "2021 biomass is 131 ton, 2025 is 167,485 ton (PLTU co-firing): a real change, not a method change."],
    ["Electricity", "Capacity and generation are split on-grid / off-grid. PJUTS and LTSHE are small solar items listed with the generation."],
    ["Data flags", "(1) LTSHE 2021 = 312.5 GWh (191,563 BOE) while other years are ~0.002 GWh: probably a unit error in the 2021 workbook. (2) Avtur falls from 36,452 KL (2023) and 32,646 KL (2024) to 399 KL (2025), and is 0 in 2021: check with Pertamina / ESDM. (3) PLTS Atap on-grid is 0 in 2025 while 0.59 MW appears off-grid."],
    ["Status", "Values are as in the source workbooks; not independently verified. Sheets in the yearly files that are templates (Data Energi) are mostly empty: only non-empty inputs are kept."],
]


def main() -> None:
    ap = argparse.ArgumentParser()
    for y, p in DEFAULT.items():
        ap.add_argument(f"--f{y}", default=p)
    a = ap.parse_args()
    files = {y: getattr(a, f"f{y}") for y in DEFAULT}

    long_, mix, inputs = [], [], []
    for y, p in files.items():
        r, m = read_year(y, p)
        long_ += r
        mix += m
        inputs += read_inputs(y, p)
    L = pd.DataFrame(long_)
    L["Item_normal"], L["Campuran"] = zip(*[norm_item(s, g, i) for s, g, i in zip(L.Bagian, L.Grup, L.Item)])
    L["Sumber_file"] = L.Tahun.map(lambda y: Path(files[y]).name)
    order = ["Tahun", "Baris", "Bagian", "Blok", "Grup", "No", "Item", "Item_normal", "Campuran", "Satuan", "Faktor_BOE",
             "CF_Efisiensi", "Nilai", "Off_grid", "BOE", "TOE", "Catatan", "Sumber_file"]
    L = L[order]

    M = pd.DataFrame(mix)
    M["Sumber"] = M.Sumber.str.strip()
    summary = M.pivot_table(index="Sumber", columns="Tahun", values=["BOE", "TOE", "MTOE", "Persen"], aggfunc="first")
    summary = summary.swaplevel(axis=1).sort_index(axis=1)
    summary.columns = [f"{y} {v}" for y, v in summary.columns]
    summary = summary.reset_index()
    summary["_o"] = summary.Sumber.map({s: i for i, s in enumerate(MIX_ORDER)}).fillna(9)
    summary = summary.sort_values("_o").drop(columns="_o")

    # EBT excluding firewood for comparability
    kb = L[(L.Item_normal.str.lower().str.startswith("kayu bakar")) & (L.Blok == "Konsumsi")].set_index("Tahun")["BOE"]
    ebt = M[M.Sumber == "EBT"].set_index("Tahun")["BOE"]
    tot = M[M.Sumber.str.lower() == "total"].set_index("Tahun")["BOE"]
    extra = pd.DataFrame({"Tahun": list(ebt.index), "Kayu bakar (BOE)": [kb.get(y, 0) or 0 for y in ebt.index],
                          "EBT (BOE)": list(ebt.values), "Total (BOE)": [tot.get(y) for y in ebt.index]})
    extra["EBT tanpa kayu bakar (BOE)"] = extra["EBT (BOE)"] - extra["Kayu bakar (BOE)"]
    extra["Total tanpa kayu bakar (BOE)"] = extra["Total (BOE)"] - extra["Kayu bakar (BOE)"]
    extra["Pangsa EBT tanpa kayu bakar (%)"] = (100 * extra["EBT tanpa kayu bakar (BOE)"] / extra["Total tanpa kayu bakar (BOE)"]).round(1)

    C = L[(L.Blok == "Konsumsi") & L.Nilai.notna()].copy()
    C["Kunci"] = C.Bagian + " | " + C.Grup + " | " + C.Item_normal
    pv = (C.groupby(["Kunci", "Bagian", "Grup", "Item_normal", "Tahun"]).agg(Nilai=("Nilai", "sum"), BOE=("BOE", "sum"), Satuan=("Satuan", "first")).reset_index())
    val = pv.pivot_table(index=["Bagian", "Grup", "Item_normal", "Satuan"], columns="Tahun", values="Nilai", aggfunc="sum")
    boe = pv.pivot_table(index=["Bagian", "Grup", "Item_normal", "Satuan"], columns="Tahun", values="BOE", aggfunc="sum")
    val.columns = [f"Nilai {y}" for y in val.columns]
    boe.columns = [f"BOE {y}" for y in boe.columns]
    P = val.join(boe).reset_index().rename(columns={"Item_normal": "Item"})

    E = L[L.Blok.isin(["Kapasitas terpasang", "Produksi listrik"])].copy()
    ev = E.pivot_table(index=["Item_normal"], columns=["Blok", "Tahun"], values=["Nilai", "Off_grid"], aggfunc="first")
    cols = []
    for (var, blok, y) in ev.columns:
        unit = "MW" if blok.startswith("Kap") else "GWh"
        cols.append(f"{unit} {'on-grid' if var == 'Nilai' else 'off-grid'} {y}")
    ev.columns = cols
    ev = ev.reset_index().rename(columns={"Item_normal": "Teknologi"})
    ev = ev[["Teknologi"] + sorted([c for c in ev.columns if c != "Teknologi"], key=lambda c: (c.split()[0] != "MW", c.split()[1], c.split()[2]))]

    I = pd.DataFrame(inputs)
    K = pd.read_excel(files[2022], sheet_name="keg 2022", header=None, dtype=object)
    K.columns = ["Jenis", "Jumlah (Unit)", "Lokasi", "Total Kapasitas (kW)", "Sumber Dana", "Status", "Catatan"][:K.shape[1]]
    K = K.iloc[2:].reset_index(drop=True) if str(K.iloc[0, 0]).lower() != "jenis" else K.iloc[1:].reset_index(drop=True)

    out = ROOT / "data/calibration"
    xlsx = out / "Bauran_Energi_Daerah_NTT_2021-2025.xlsx"
    with pd.ExcelWriter(xlsx, engine="openpyxl") as xw:
        pd.DataFrame(README).to_excel(xw, sheet_name="README", header=False, index=False)
        summary.to_excel(xw, sheet_name="Ringkasan_Bauran", index=False)
        extra.to_excel(xw, sheet_name="Ringkasan_Bauran", index=False, startrow=len(summary) + 3)
        P.to_excel(xw, sheet_name="Pivot_Konsumsi", index=False)
        ev.to_excel(xw, sheet_name="Pivot_Listrik", index=False)
        L.to_excel(xw, sheet_name="Worksheet_Long", index=False)
        I.to_excel(xw, sheet_name="DataEnergi_Input", index=False)
        K.to_excel(xw, sheet_name="Kegiatan_2022", index=False)
        for name, ws in xw.sheets.items():
            if name == "README":
                ws.column_dimensions["A"].width = 22
                ws.column_dimensions["B"].width = 140
                ws["A1"].font = Font(bold=True, size=13)
                ws["A8"].font = Font(bold=True)
            else:
                autosize(ws)
    csvd = out / "bauran_energi"
    csvd.mkdir(exist_ok=True)
    for name, df in [("ringkasan_bauran", summary), ("ringkasan_tanpa_kayu_bakar", extra), ("pivot_konsumsi", P), ("pivot_listrik", ev),
                     ("worksheet_long", L), ("dataenergi_input", I), ("kegiatan_2022", K)]:
        df.to_csv(csvd / f"{name}.csv", index=False)
    print(xlsx, len(L), "rows;", len(P), "fuels;", len(ev), "technologies")
    print(summary.to_string())
    print(extra.to_string())


if __name__ == "__main__":
    main()
