#!/usr/bin/env python3
import argparse
import csv
import math
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mplconfig_gem5_q5")
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


L1_SIZES_KB = [2, 4, 8, 16, 32]
APPS = ["dijkstra", "blowfish"]
STATS_KEYS = [
    "simInsts",
    "system.cpu.numCycles",
    "system.cpu.ipc",
    "system.cpu.icache.overallMissRate::total",
    "system.cpu.dcache.overallMissRate::total",
    "system.l2cache.overallMissRate::total",
    "system.cpu.branchPred.condIncorrect",
    "system.cpu.branchPred.condPredicted",
    "system.cpu.commit.branchMispredicts",
    "system.cpu.branchPred.BTBHitRatio",
]


def read_selected_stats(stats_path: Path):
    values = {}
    with stats_path.open("r", encoding="utf-8", errors="ignore") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            key = parts[0]
            if key not in STATS_KEYS:
                continue
            token = parts[1]
            try:
                values[key] = float(token)
            except ValueError:
                continue
    return values


def collect_rows(runs_base: Path):
    rows = []
    missing = []
    for app in APPS:
        for l1_kb in L1_SIZES_KB:
            run_dir = runs_base / f"{app}_L1_{l1_kb}k"
            stats_path = run_dir / "stats.txt"
            if not stats_path.exists():
                missing.append(str(stats_path))
                continue

            stats = read_selected_stats(stats_path)
            cond_pred = stats.get("system.cpu.branchPred.condPredicted", float("nan"))
            cond_inc = stats.get("system.cpu.branchPred.condIncorrect", float("nan"))
            if cond_pred and not math.isnan(cond_pred):
                branch_rate = cond_inc / cond_pred
            else:
                branch_rate = float("nan")

            rows.append(
                {
                    "app": app,
                    "l1_kb": l1_kb,
                    "run_path": str(run_dir),
                    "simInsts": stats.get("simInsts", float("nan")),
                    "numCycles": stats.get("system.cpu.numCycles", float("nan")),
                    "ipc": stats.get("system.cpu.ipc", float("nan")),
                    "il1_miss_rate": stats.get("system.cpu.icache.overallMissRate::total", float("nan")),
                    "dl1_miss_rate": stats.get("system.cpu.dcache.overallMissRate::total", float("nan")),
                    "l2_miss_rate": stats.get("system.l2cache.overallMissRate::total", float("nan")),
                    "branch_cond_incorrect": cond_inc,
                    "branch_cond_predicted": cond_pred,
                    "branch_mispred_rate": branch_rate,
                    "commit_branch_mispredicts": stats.get("system.cpu.commit.branchMispredicts", float("nan")),
                    "btb_hit_ratio": stats.get("system.cpu.branchPred.BTBHitRatio", float("nan")),
                }
            )
    return rows, missing


def write_csv(rows, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "app",
        "l1_kb",
        "run_path",
        "simInsts",
        "numCycles",
        "ipc",
        "il1_miss_rate",
        "dl1_miss_rate",
        "l2_miss_rate",
        "branch_cond_incorrect",
        "branch_cond_predicted",
        "branch_mispred_rate",
        "commit_branch_mispredicts",
        "btb_hit_ratio",
    ]
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in sorted(rows, key=lambda item: (item["app"], item["l1_kb"])):
            writer.writerow(row)


def summarize_best(rows):
    summary = []
    for app in APPS:
        app_rows = [row for row in rows if row["app"] == app]
        if not app_rows:
            continue

        best_ipc = max(app_rows, key=lambda row: (row["ipc"], -row["l1_kb"]))
        best_cycles = min(app_rows, key=lambda row: (row["numCycles"], row["l1_kb"]))
        max_ipc = max(row["ipc"] for row in app_rows)
        plateau_threshold = max_ipc * 0.99
        plateau_rows = [row for row in app_rows if row["ipc"] >= plateau_threshold]
        plateau_choice = min(plateau_rows, key=lambda row: row["l1_kb"])

        summary.append(
            {
                "app": app,
                "best_l1_by_ipc_kb": int(best_ipc["l1_kb"]),
                "best_ipc": best_ipc["ipc"],
                "best_l1_by_cycles_kb": int(best_cycles["l1_kb"]),
                "min_cycles": best_cycles["numCycles"],
                "plateau_1pct_l1_kb": int(plateau_choice["l1_kb"]),
                "plateau_1pct_threshold_ipc": plateau_threshold,
            }
        )
    return summary


def write_summary(summary_rows, out_csv: Path):
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "app",
        "best_l1_by_ipc_kb",
        "best_ipc",
        "best_l1_by_cycles_kb",
        "min_cycles",
        "plateau_1pct_l1_kb",
        "plateau_1pct_threshold_ipc",
    ]
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in summary_rows:
            writer.writerow(row)


def _plot_common(fig_path: Path, title: str, x_label: str, y_label: str):
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(fig_path, dpi=160)
    plt.close()


def create_plots(rows, figures_dir: Path):
    figures_dir.mkdir(parents=True, exist_ok=True)
    for app in APPS:
        app_rows = sorted([row for row in rows if row["app"] == app], key=lambda row: row["l1_kb"])
        if not app_rows:
            continue
        x = [row["l1_kb"] for row in app_rows]

        plt.figure(figsize=(7, 4))
        plt.plot(x, [row["ipc"] for row in app_rows], marker="o")
        _plot_common(
            figures_dir / f"q5_a15_{app}_ipc_vs_l1.png",
            f"A15 {app}: IPC vs L1",
            "L1 size (KB)",
            "IPC",
        )

        plt.figure(figsize=(7, 4))
        plt.plot(x, [row["numCycles"] for row in app_rows], marker="o")
        _plot_common(
            figures_dir / f"q5_a15_{app}_cycles_vs_l1.png",
            f"A15 {app}: numCycles vs L1",
            "L1 size (KB)",
            "numCycles",
        )

        plt.figure(figsize=(7, 4))
        plt.plot(x, [row["il1_miss_rate"] * 100.0 for row in app_rows], marker="o", label="I-L1 miss rate")
        plt.plot(x, [row["dl1_miss_rate"] * 100.0 for row in app_rows], marker="o", label="D-L1 miss rate")
        plt.plot(x, [row["l2_miss_rate"] * 100.0 for row in app_rows], marker="o", label="L2 miss rate")
        plt.legend()
        _plot_common(
            figures_dir / f"q5_a15_{app}_miss_rates_vs_l1.png",
            f"A15 {app}: miss rates vs L1",
            "L1 size (KB)",
            "Miss rate (%)",
        )

        plt.figure(figsize=(7, 4))
        plt.plot(x, [row["branch_mispred_rate"] * 100.0 for row in app_rows], marker="o")
        _plot_common(
            figures_dir / f"q5_a15_{app}_branch_mispred_vs_l1.png",
            f"A15 {app}: branch misprediction rate vs L1",
            "L1 size (KB)",
            "Misprediction rate (%)",
        )


def write_run_params(path: Path, runs_base: Path):
    content = f"""Q5 A15 gem5 run parameters
- CPU model: DerivO3CPU (out-of-order)
- Config script: se_A15.py
- L2 cache: 512kB, assoc=16, block=64B (fixed)
- L1 sweep: I-L1 = D-L1 = 2kB, 4kB, 8kB, 16kB, 32kB
- Branch predictor: LocalBP/BranchPredictor wrapper with BTB=256
- Decode/Issue/Commit: 4/8/4
- RUU/LSQ (gem5 mapping): ROB=16, LQ=16, SQ=16
- Fetch queue: 8
- Memory: DDR3_1600_8x8, mem-size=2GB
- Clock: 2GHz
- Dataset: dijkstra input.dat, blowfish input_small.asc
- Run directories: {runs_base}
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(description="Extract Q5 A15 metrics and generate plots.")
    parser.add_argument("--runs-base", required=True, help="Base directory containing A15 run folders")
    parser.add_argument("--out-csv", required=True, help="Output CSV path")
    parser.add_argument("--summary-csv", required=True, help="Output summary CSV path")
    parser.add_argument("--figures-dir", required=True, help="Output directory for PNG figures")
    parser.add_argument("--params-txt", required=True, help="Output text file with gem5 parameters")
    return parser.parse_args()


def main():
    args = parse_args()
    runs_base = Path(args.runs_base).resolve()
    rows, missing = collect_rows(runs_base)
    if missing:
        missing_list = "\n".join(missing)
        raise FileNotFoundError(f"Missing stats.txt files:\n{missing_list}")

    write_csv(rows, Path(args.out_csv))
    summary = summarize_best(rows)
    write_summary(summary, Path(args.summary_csv))
    create_plots(rows, Path(args.figures_dir))
    write_run_params(Path(args.params_txt), runs_base)


if __name__ == "__main__":
    main()
