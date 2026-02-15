#!/usr/bin/env python3
import argparse
import csv
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mplconfig_q9_surface")
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


L1_ALLOWED = {
    "A7": {1, 2, 4, 8, 16},
    "A15": {2, 4, 8, 16, 32},
}
APPS = ["dijkstra", "blowfish"]


def read_rows(path: Path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_area_map(path: Path):
    area_rows = read_rows(path)
    area_map = {}
    for row in area_rows:
        proc = row["proc"]
        l1_kb = int(row["L1_kB"])
        if l1_kb not in L1_ALLOWED.get(proc, set()):
            continue
        area_map[(proc, l1_kb)] = float(row["A_total_new_28"])
    return area_map


def build_efficiency_rows(a7_ipc_csv: Path, a15_ipc_csv: Path, area_csv: Path):
    area_map = load_area_map(area_csv)

    rows = []
    missing = []

    for proc, ipc_csv in [("A7", a7_ipc_csv), ("A15", a15_ipc_csv)]:
        for row in read_rows(ipc_csv):
            app = row["app"]
            l1_kb = int(float(row["l1_kb"]))
            if app not in APPS:
                continue
            if l1_kb not in L1_ALLOWED[proc]:
                continue

            key = (proc, l1_kb)
            if key not in area_map:
                missing.append((proc, app, l1_kb, "area"))
                continue

            ipc = float(row["ipc"])
            area_total_28 = area_map[key]
            if area_total_28 <= 0:
                missing.append((proc, app, l1_kb, "area<=0"))
                continue

            surf_eff = ipc / area_total_28
            rows.append(
                {
                    "proc": proc,
                    "app": app,
                    "l1_kb": l1_kb,
                    "ipc": ipc,
                    "area_total_28": area_total_28,
                    "surf_eff_ipc_per_mm2": surf_eff,
                }
            )

    if missing:
        details = "\n".join(str(item) for item in missing[:25])
        raise ValueError(f"Join issues detected ({len(missing)} rows). First entries:\n{details}")

    rows.sort(key=lambda r: (r["app"], r["proc"], r["l1_kb"]))
    return rows


def write_csv(rows, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["proc", "app", "l1_kb", "ipc", "area_total_28", "surf_eff_ipc_per_mm2"]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            out = dict(row)
            out["ipc"] = f"{row['ipc']:.6f}"
            out["area_total_28"] = f"{row['area_total_28']:.9f}"
            out["surf_eff_ipc_per_mm2"] = f"{row['surf_eff_ipc_per_mm2']:.9f}"
            w.writerow(out)


def summarize_best(rows):
    summary = []
    for app in APPS:
        for proc in ("A7", "A15"):
            group = [r for r in rows if r["app"] == app and r["proc"] == proc]
            if not group:
                continue
            best = max(group, key=lambda r: (r["surf_eff_ipc_per_mm2"], -r["l1_kb"]))
            summary.append(
                {
                    "proc": proc,
                    "app": app,
                    "best_l1_kb": best["l1_kb"],
                    "best_ipc": best["ipc"],
                    "best_area_total_28": best["area_total_28"],
                    "best_surf_eff_ipc_per_mm2": best["surf_eff_ipc_per_mm2"],
                }
            )
    summary.sort(key=lambda r: (r["app"], r["proc"]))
    return summary


def write_summary(rows, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["proc", "app", "best_l1_kb", "best_ipc", "best_area_total_28", "best_surf_eff_ipc_per_mm2"]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            out = dict(row)
            out["best_ipc"] = f"{row['best_ipc']:.6f}"
            out["best_area_total_28"] = f"{row['best_area_total_28']:.9f}"
            out["best_surf_eff_ipc_per_mm2"] = f"{row['best_surf_eff_ipc_per_mm2']:.9f}"
            w.writerow(out)


def plot_efficiency(rows, fig_dir: Path):
    fig_dir.mkdir(parents=True, exist_ok=True)
    for app in APPS:
        plt.figure(figsize=(7, 4))
        for proc in ("A7", "A15"):
            group = sorted([r for r in rows if r["app"] == app and r["proc"] == proc], key=lambda r: r["l1_kb"])
            x = [r["l1_kb"] for r in group]
            y = [r["surf_eff_ipc_per_mm2"] for r in group]
            plt.plot(x, y, marker="o", label=proc)
        plt.title(f"Q9 {app}: efficacite surfacique vs L1")
        plt.xlabel("L1 size (KB)")
        plt.ylabel("Efficacite surfacique (IPC/mm^2)")
        plt.grid(True, linestyle="--", alpha=0.4)
        plt.legend()
        plt.tight_layout()
        plt.savefig(fig_dir / f"q9_{app}_se_vs_l1.png", dpi=180)
        plt.close()


def write_params(path: Path, a7_ipc_csv: Path, a15_ipc_csv: Path, area_csv: Path, sample_value: float):
    path.parent.mkdir(parents=True, exist_ok=True)
    content = f"""Q9 surface efficiency parameters
- Formula: surf_eff = IPC / area_total_28
- IPC A7 source: {a7_ipc_csv}
- IPC A15 source: {a15_ipc_csv}
- Area source: {area_csv} (column A_total_new_28, mm^2 @ 28nm)
- Domains:
  - A7 L1: 1,2,4,8,16 KB
  - A15 L1: 2,4,8,16,32 KB
- Validation sample:
  - A15 dijkstra L1=8KB -> surf_eff = {sample_value:.9f} IPC/mm^2
"""
    path.write_text(content, encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(description="Compute Q9 surface efficiency from IPC and area data.")
    parser.add_argument("--a7-ipc-csv", required=True, help="CSV from Q4 A7 extraction")
    parser.add_argument("--a15-ipc-csv", required=True, help="CSV from Q5 A15 extraction")
    parser.add_argument("--area-csv", required=True, help="CSV from Q8 area flow")
    parser.add_argument("--out-csv", required=True, help="Output Q9 detailed CSV")
    parser.add_argument("--best-csv", required=True, help="Output Q9 best-by-app/proc CSV")
    parser.add_argument("--figures-dir", required=True, help="Output directory for Q9 figures")
    parser.add_argument("--params-txt", required=True, help="Output text file with Q9 parameters")
    return parser.parse_args()


def main():
    args = parse_args()
    a7_ipc_csv = Path(args.a7_ipc_csv).resolve()
    a15_ipc_csv = Path(args.a15_ipc_csv).resolve()
    area_csv = Path(args.area_csv).resolve()

    rows = build_efficiency_rows(a7_ipc_csv, a15_ipc_csv, area_csv)
    write_csv(rows, Path(args.out_csv))

    best_rows = summarize_best(rows)
    write_summary(best_rows, Path(args.best_csv))

    plot_efficiency(rows, Path(args.figures_dir))

    sample = None
    for row in rows:
        if row["proc"] == "A15" and row["app"] == "dijkstra" and row["l1_kb"] == 8:
            sample = row["surf_eff_ipc_per_mm2"]
            break
    if sample is None:
        raise RuntimeError("Validation sample A15/dijkstra/8KB not found in Q9 rows.")
    write_params(Path(args.params_txt), a7_ipc_csv, a15_ipc_csv, area_csv, sample)


if __name__ == "__main__":
    main()
