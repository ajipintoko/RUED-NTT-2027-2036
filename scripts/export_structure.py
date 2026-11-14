"""Turn the LEAP 'Export to Excel' workbook into text tables for the repo.

Input  (LEAP > Analysis > Export to Excel, all scenarios, sheet 'All Data'):
    data/original/All LEAP Data.xlsx   (header on row 3)

Outputs
    data/structure/branch_index.csv                one row per branch (tree, sector, type, variables)
    data/structure/variables_current_accounts.csv  branch x variable, Current Accounts (calibration, 2019-2025)
    data/structure/variables_baseline.csv          branch x variable, Baseline (BAU)
    data/structure/scenario_overrides.csv          only the expressions that differ from Baseline, per scenario
    data/dataflow/branch_links.csv                 every branch-to-branch reference found in the expressions
    data/dataflow/sector_links.csv                 the same links counted by sector (who reads whom)

Usage
    python scripts/export_structure.py [--xlsx "data/original/All LEAP Data.xlsx"] [--out .]

Requires pandas and openpyxl. Never edit the outputs by hand; re-run after each LEAP export.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

LEVELS = [f"Level {i}" for i in range(1, 8)] + ["Level 8..."]
KEEP = ["BranchID", "VariableID", "ScenarioID", "Branch Path", "Variable", "Scenario",
        "Scale", "Units", "Per...", "Expression"]
EFFECT_VARS = {"Avg Environmental Loading", "New Device Environmental Loading"}
CA_ID, BASE_ID = 1, 2

# Reference to another branch, e.g.
#   Key\Populasi[Thousand Penduduk]
#   Key\Roadmap NZE\Target kapasitas PLTS\Target kapasitas PLTS atap offgrid:Activity Level[MW]
#   Demand\Komersial\Retail:Total Activity[No data]
REF = re.compile(r"(Key|Demand|Transformation|Resources)\\([^\[\]:;*/+]+?)"
                 r"(?::([A-Za-z][A-Za-z ]*?))?\[([^\]]*)\]")
ROOT_NAME = {"Key": "Key Assumptions"}


def read_export(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="All Data", header=2)
    df = df[[c for c in KEEP + LEVELS if c in df.columns]]
    df = df.dropna(subset=["Branch Path"])
    df["BranchID"] = df["BranchID"].astype(int)
    df["ScenarioID"] = df["ScenarioID"].astype(int)
    return df


def classify(tree: str, vars_: set[str], is_leaf_child_of_fuel: bool) -> str:
    v = vars_ - EFFECT_VARS - {"Demand Cost"}
    if tree == "Key Assumptions":
        return "Key assumption"
    if tree == "Demand":
        if not v and vars_ & EFFECT_VARS:
            return "Emission factor"
        if "Total Energy" in v:
            return "Total energy"
        if "Final Energy Intensity" in v:
            return "Activity x intensity"
        return "Category / activity"
    if tree == "Transformation":
        if v & {"Exogenous Capacity", "Process Efficiency", "Dispatch Rule"}:
            return "Process"
        if "Feedstock Fuel Share" in v:
            return "Feedstock fuel"
        if v & {"Shortfall Rule", "Usage Rule"}:
            return "Output fuel"
        return "Module / other"
    if tree == "Resources":
        return "Resource"
    return tree


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", default="data/original/All LEAP Data.xlsx")
    ap.add_argument("--out", default=".")
    a = ap.parse_args()
    out = Path(a.out)
    (out / "data/structure").mkdir(parents=True, exist_ok=True)
    (out / "data/dataflow").mkdir(parents=True, exist_ok=True)

    df = read_export(Path(a.xlsx))
    df["tree"] = df["Level 1"]
    df["sector"] = df["Level 2"]

    ca = df[df.ScenarioID == CA_ID].copy()
    base = df[df.ScenarioID == BASE_ID].copy()
    keepv = ["BranchID", "VariableID", "Branch Path", "tree", "sector", "Variable", "Scale", "Units", "Per...", "Expression"]
    ca[keepv].to_csv(out / "data/structure/variables_current_accounts.csv", index=False)
    base[keepv].to_csv(out / "data/structure/variables_baseline.csv", index=False)

    # scenario overrides = rows whose expression differs from Baseline
    b = base.set_index(["BranchID", "VariableID"])["Expression"].astype(str)
    rows = []
    for (sid, sname), g in df[~df.ScenarioID.isin([CA_ID, BASE_ID])].groupby(["ScenarioID", "Scenario"]):
        g = g.set_index(["BranchID", "VariableID"])
        j = g.join(b.rename("baseline_expression"), how="left")
        j = j[j["Expression"].astype(str) != j["baseline_expression"]].reset_index()
        j["ScenarioID"], j["Scenario"] = sid, sname
        rows.append(j[["ScenarioID", "Scenario", "BranchID", "Branch Path", "Variable", "Expression", "baseline_expression"]]
                    .rename(columns={"Expression": "scenario_expression"}))
    pd.concat(rows).to_csv(out / "data/structure/scenario_overrides.csv", index=False)

    # branch index (union of CA and Baseline)
    idx = []
    for bid, g in df[df.ScenarioID.isin([CA_ID, BASE_ID])].groupby("BranchID"):
        r = g.iloc[0]
        vs_ca = sorted(set(g[g.ScenarioID == CA_ID]["Variable"]))
        vs_b = sorted(set(g[g.ScenarioID == BASE_ID]["Variable"]))
        depth = str(r["Branch Path"]).count("\\")
        parent = str(r["Branch Path"]).rpartition("\\")[0]
        idx.append(dict(branch_id=bid, branch_path=r["Branch Path"], tree=r["tree"], sector=r["sector"],
                        depth=depth, parent_path=parent,
                        branch_type=classify(r["tree"], set(vs_ca) | set(vs_b), False),
                        units=r["Units"], variables_current_accounts="; ".join(vs_ca), variables_baseline="; ".join(vs_b)))
    bi = pd.DataFrame(idx).sort_values("branch_path")
    bi.to_csv(out / "data/structure/branch_index.csv", index=False)
    known = {p.lower(): (t, s) for p, t, s in zip(bi.branch_path, bi.tree, bi.sector)}

    # dataflow
    links = []
    for scen, g in (("Current Accounts", ca), ("Baseline", base)):
        for _, r in g.iterrows():
            expr = str(r["Expression"])
            if "\\" not in expr:
                continue
            for m in REF.finditer(expr):
                root, rest, var, unit = m.groups()
                src = f"{root}\{rest}".strip()
                st = known.get(src.lower())
                links.append(dict(scenario=scen,
                                  from_tree=ROOT_NAME.get(root, root), from_sector=(st[1] if st else rest.split("\\")[0]),
                                  from_path=src, from_variable=var or "Activity Level",
                                  to_tree=r["tree"], to_sector=r["sector"], to_path=r["Branch Path"],
                                  to_variable=r["Variable"], resolved=bool(st)))
    L = pd.DataFrame(links).drop_duplicates()
    L.to_csv(out / "data/dataflow/branch_links.csv", index=False)
    S = (L.groupby(["scenario", "from_tree", "from_sector", "to_tree", "to_sector"])
          .agg(n_links=("to_path", "size"), n_reading_branches=("to_path", "nunique")).reset_index())
    S.to_csv(out / "data/dataflow/sector_links.csv", index=False)
    print(f"branches={len(bi)} links={len(L)} resolved={L.resolved.mean():.1%} overrides={sum(len(r) for r in rows)}")


if __name__ == "__main__":
    main()
