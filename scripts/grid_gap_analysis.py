"""Estimate settlements without a (predicted) grid nearby: HOTOSM places x Gridfinder x ESDM lines.

Method (same logic as the 'Settlements & grid gap' panel of the NTT map):
  1. Settlements   HOTOSM populated places (OSM 'place' nodes); the NTT map already carries island /
                   kabupaten / kecamatan for each one.
  2. Grid          Gridfinder predicted grid (night-light analysis, lines) + ESDM transmission lines
                   (+ optionally the national gridfinder_indonesia.geojson clipped to NTT).
                   Lines are densified to <= 0.5 km so that the nearest vertex is a good proxy for the
                   nearest point on the line.
  3. Distance      to the nearest grid point (km, equirectangular approximation, fine at NTT latitudes).
  4. Classes       within --near km (default 1)  : likely reached
                   --near..--far (default 1-5)   : near-grid gap (extension candidate)
                   beyond --far  km (default 5)  : remote -> candidate for mini-grid / stand-alone RE

Usage
    python scripts/grid_gap_analysis.py --html "data/power/re_potential/RE Potential Map NTT (standalone).html" \
        [--gridfinder "D:/2026/FPV Crux/shp/gridfinder_indonesia.geojson"] [--near 1] [--far 5]

Outputs (data/power/re_potential/grid_gap/)
    settlements_grid_distance.csv   one row per settlement with distance and class
    summary_by_kabupaten.csv        counts per class per kabupaten
    summary_by_island.csv           same per island
    summary_by_place_type.csv       same per OSM place type
Requires only numpy.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/power/re_potential/grid_gap"
NTT_BBOX = (118.9, -11.2, 125.3, -8.0)  # lon_min, lat_min, lon_max, lat_max
KM_LAT = 111.19


def load_map_data(html: Path) -> dict:
    t = html.read_text(encoding="utf-8")
    i = t.index("window.DATA=") + len("window.DATA=")
    data, _ = json.JSONDecoder().raw_decode(t[i:])
    return data


def densify(coords, step_km=0.5):
    pts = []
    for (x0, y0), (x1, y1) in zip(coords[:-1], coords[1:]):
        d = np.hypot((x1 - x0) * KM_LAT * np.cos(np.radians((y0 + y1) / 2)), (y1 - y0) * KM_LAT)
        n = max(1, int(np.ceil(d / step_km)))
        for k in range(n):
            pts.append((x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n))
    pts.append(tuple(coords[-1][:2]))
    return pts


def line_points(features, bbox=None):
    pts = []
    for f in features:
        g = f["geometry"]
        lines = [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"] if g["type"] == "MultiLineString" else []
        for ln in lines:
            if bbox and not any(bbox[0] <= c[0] <= bbox[2] and bbox[1] <= c[1] <= bbox[3] for c in ln):
                continue
            pts.extend(densify([c[:2] for c in ln]))
    return np.array(pts)


def nearest_km(src, grid):
    """min distance (km) from every src point (lon, lat) to the grid points."""
    out = np.empty(len(src))
    cos = np.cos(np.radians(-9.5))
    gx, gy = grid[:, 0] * KM_LAT * cos, grid[:, 1] * KM_LAT
    for i in range(0, len(src), 200):
        sx = src[i:i + 200, 0, None] * KM_LAT * cos
        sy = src[i:i + 200, 1, None] * KM_LAT
        out[i:i + 200] = np.sqrt(((sx - gx) ** 2 + (sy - gy) ** 2).min(axis=1))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", default=str(ROOT / "data/power/re_potential/RE Potential Map NTT (standalone).html"))
    ap.add_argument("--gridfinder", default=None, help="national gridfinder_indonesia.geojson (optional)")
    ap.add_argument("--near", type=float, default=1.0)
    ap.add_argument("--far", type=float, default=5.0)
    a = ap.parse_args()

    D = load_map_data(Path(a.html))
    S = D["settlements"]
    fields = S["fields"]
    rows = [dict(zip(fields, r)) for r in S["rows"]]
    src = np.array([[r["lon"], r["lat"]] for r in rows])

    gf_map = line_points(D["gridfinder"]["features"])
    esdm = line_points(D["esdm_lines"]["features"])
    layers = {"gridfinder_map": gf_map, "esdm_lines": esdm}
    if a.gridfinder:
        nat = json.load(open(a.gridfinder, encoding="utf-8"))
        layers["gridfinder_national"] = line_points(nat["features"], NTT_BBOX)
    gi = np.array([[f["geometry"]["coordinates"][0], f["geometry"]["coordinates"][1]] for f in D["esdm_gi"]["features"]])
    print({k: len(v) for k, v in layers.items()}, "GI", len(gi), "settlements", len(rows))

    dist = {k: nearest_km(src, v) for k, v in layers.items()}
    d_gi = nearest_km(src, gi)
    gf_key = "gridfinder_national" if "gridfinder_national" in layers else "gridfinder_map"
    d_any = np.minimum(dist[gf_key], dist["esdm_lines"])

    def cls(d):
        return "near-grid" if d <= a.near else ("gap-extension" if d <= a.far else "remote")

    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "settlements_grid_distance.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["name", "place", "island", "kabupaten", "kecamatan", "lon", "lat"] +
                   [f"km_to_{k}" for k in layers] + ["km_to_nearest_GI", "km_to_any_grid", "class"])
        for i, r in enumerate(rows):
            w.writerow([r["name"], r["place"], r["island"], r["kabupaten"], r["kecamatan"], r["lon"], r["lat"]] +
                       [round(float(dist[k][i]), 2) for k in layers] + [round(float(d_gi[i]), 2), round(float(d_any[i]), 2), cls(d_any[i])])

    def summarise(key, name):
        agg = defaultdict(lambda: defaultdict(int))
        for i, r in enumerate(rows):
            g = agg[r[key]]
            g["settlements"] += 1
            g[cls(d_any[i])] += 1
        with open(OUT / f"summary_by_{name}.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow([key, "settlements", "near-grid", "gap-extension", "remote", "pct_remote"])
            for k, g in sorted(agg.items(), key=lambda kv: -kv[1]["remote"]):
                w.writerow([k, g["settlements"], g["near-grid"], g["gap-extension"], g["remote"],
                            round(100 * g["remote"] / g["settlements"], 1)])
        return agg

    summarise("kabupaten", "kabupaten")
    summarise("island", "island")
    tot = summarise("place", "place_type")
    n = len(rows)
    c = {k: int(sum(1 for d in d_any if cls(d) == k)) for k in ("near-grid", "gap-extension", "remote")}
    print(n, c)


if __name__ == "__main__":
    main()
