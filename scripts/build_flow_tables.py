"""Summarise the branch-to-branch links for the documentation.

Reads   data/dataflow/branch_links.csv   (written by export_structure.py)
Writes  data/dataflow/key_to_demand_by_source.csv
            one row per source branch group (Key branch, 4 levels deep) x reading sector:
            how many branches read it and one example reading branch
        data/dataflow/transformation_inputs.csv
            every Key / Resources / Demand branch read by a Transformation branch
        data/dataflow/chain_summary.csv
            number of links per (from tree/sector -> to tree/sector), Baseline only

Usage   python scripts/build_flow_tables.py   (run from the repository root)
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def group_path(p: str, depth: int = 4) -> str:
    return "\\".join(p.split("\\")[:depth])


def main() -> None:
    L = pd.read_csv(ROOT / "data/dataflow/branch_links.csv")
    B = L[L.scenario == "Baseline"].copy()

    d = B[(B.from_tree == "Key Assumptions") & (B.to_tree == "Demand")].copy()
    d["source_group"] = d.from_path.map(group_path)
    out = (d.groupby(["from_sector", "source_group", "to_sector"])
             .agg(n_links=("to_path", "size"), n_reading_branches=("to_path", "nunique"),
                  example_reader=("to_path", "first"), example_variable=("to_variable", "first"))
             .reset_index().sort_values(["to_sector", "from_sector", "source_group"]))
    out.to_csv(ROOT / "data/dataflow/key_to_demand_by_source.csv", index=False)

    t = B[B.to_tree == "Transformation"][["from_tree", "from_sector", "from_path", "from_variable",
                                          "to_sector", "to_path", "to_variable"]]
    t.to_csv(ROOT / "data/dataflow/transformation_inputs.csv", index=False)

    s = (B.groupby(["from_tree", "from_sector", "to_tree", "to_sector"])
          .agg(n_links=("to_path", "size"), n_reading_branches=("to_path", "nunique")).reset_index())
    s.to_csv(ROOT / "data/dataflow/chain_summary.csv", index=False)
    print(len(out), len(t), len(s))


if __name__ == "__main__":
    main()
