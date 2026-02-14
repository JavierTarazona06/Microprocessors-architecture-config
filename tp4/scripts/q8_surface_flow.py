#!/usr/bin/env python3
"""Q8 surface sweep (CACTI): A7/A15 L1 area and total core area with fixed L2.

Generates:
  - CACTI outputs for all L1 sweep points and fixed L2 points
  - Consolidated CSV with 32nm and normalized 28nm areas
  - Two figures required by Q8
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import subprocess
from pathlib import Path

# Avoid writing under ~/.cache in restricted environments.
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mplconfig_q8_surface")

import matplotlib.pyplot as plt


L1_SWEEP_KB = {
    # Q4 uses up to 16KB for A7; we also include 32KB for direct visual comparison
    # against A15 in Q8 area-only exploration.
    "A7": [1, 2, 4, 8, 16, 32],
    "A15": [2, 4, 8, 16, 32],
}

L1_BLOCK_BYTES = {"A7": 32, "A15": 64}
L1_ASSOC = {"A7": 2, "A15": 2}
L2_ASSOC = {"A7": 8, "A15": 16}
L2_BLOCK_BYTES = {"A7": 32, "A15": 64}

TECH_NM = 32.0
TARGET_NM = 28.0
AREA_SCALE_32_TO_28 = (TARGET_NM / TECH_NM) ** 2

# Derived in Q7 with homogeneous 28nm basis.
CORE_NO_L1_28 = {
    "A7": 0.378825005,
    "A15": 1.928552447,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Q8 CACTI area flow and plot results.")
    parser.add_argument(
        "--repo-root",
        default=str(Path(__file__).resolve().parents[2]),
        help="Repository root (default: inferred from script location).",
    )
    parser.add_argument(
        "--out-dir",
        default="docs/results/q8_surface",
        help="Output directory (relative to repo root).",
    )
    return parser.parse_args()


def _set_active_numeric_line(line: str, key: str, value: int | float) -> str:
    prefix = f"-{key} "
    if isinstance(value, float):
        return f"{prefix}{value:.3f}\n"
    return f"{prefix}{value}\n"


def build_cfg(
    template_text: str,
    size_bytes: int,
    block_bytes: int,
    assoc: int,
    tech_um: float,
    cache_level: str,
) -> str:
    out: list[str] = []
    for line in template_text.splitlines(keepends=True):
        stripped = line.lstrip()

        if re.match(r"^(//)?-size \(bytes\)\s+\d+", stripped):
            if stripped.startswith("-size (bytes)"):
                out.append(_set_active_numeric_line(line, "size (bytes)", size_bytes))
            else:
                out.append(line)
            continue

        if re.match(r"^(//)?-block size \(bytes\)\s+\d+", stripped):
            if stripped.startswith("-block size (bytes)"):
                out.append(_set_active_numeric_line(line, "block size (bytes)", block_bytes))
            else:
                out.append(line)
            continue

        if re.match(r"^(//)?-associativity\s+\d+", stripped):
            if stripped.startswith("-associativity"):
                out.append(_set_active_numeric_line(line, "associativity", assoc))
            else:
                out.append(line)
            continue

        if re.match(r"^(//)?-technology \(u\)\s+[0-9.]+", stripped):
            if stripped.startswith("-technology (u)"):
                out.append(_set_active_numeric_line(line, "technology (u)", tech_um))
            else:
                out.append(line)
            continue

        if "cache type \"cache\"" in stripped:
            out.append("-cache type \"cache\"\n")
            continue
        if "cache type \"ram\"" in stripped:
            out.append("//-cache type \"ram\"\n")
            continue
        if "cache type \"main memory\"" in stripped:
            out.append("//-cache type \"main memory\"\n")
            continue

        if re.match(r"^(//)?-Cache level \(L2/L3\)\s+-\s+\"(L1|L2|L3)\"", stripped):
            out.append(f"-Cache level (L2/L3) - \"{cache_level}\"\n")
            continue

        out.append(line)

    return "".join(out)


def run_cacti(cacti_dir: Path, cfg_path: Path, out_path: Path) -> None:
    cmd = [str(cacti_dir / "cacti"), "-infile", str(cfg_path)]
    proc = subprocess.run(cmd, cwd=cacti_dir, text=True, capture_output=True)
    full_output = proc.stdout
    if proc.stderr:
        full_output += "\n[stderr]\n" + proc.stderr
    out_path.write_text(full_output, encoding="utf-8")
    if proc.returncode != 0:
        raise RuntimeError(f"CACTI failed for {cfg_path.name} -> {out_path.name}")


def parse_cacti_output(path: Path) -> dict[str, float]:
    text = path.read_text(encoding="utf-8", errors="replace")

    m_size = re.search(r"Total cache size \(bytes\):\s*([0-9]+)", text)
    m_block = re.search(r"Block size \(bytes\):\s*([0-9]+)", text)
    m_assoc = re.search(r"Associativity:\s*([0-9]+)", text)
    m_tech = re.search(r"Technology size \(nm\):\s*([0-9.]+)", text)
    m_hw = re.search(r"Cache height x width \(mm\):\s*([0-9.]+)\s*x\s*([0-9.]+)", text)

    if not (m_size and m_block and m_assoc and m_tech and m_hw):
        raise ValueError(f"Could not parse expected fields from {path}")

    height = float(m_hw.group(1))
    width = float(m_hw.group(2))
    return {
        "size_bytes": float(m_size.group(1)),
        "block_bytes": float(m_block.group(1)),
        "assoc": float(m_assoc.group(1)),
        "tech_nm": float(m_tech.group(1)),
        "height_mm": height,
        "width_mm": width,
        "area_mm2": height * width,
    }


def validate_cfg(parsed: dict[str, float], size: int, block: int, assoc: int) -> None:
    if int(parsed["size_bytes"]) != size:
        raise ValueError(f"Unexpected cache size: got {parsed['size_bytes']}, expected {size}")
    if int(parsed["block_bytes"]) != block:
        raise ValueError(f"Unexpected block size: got {parsed['block_bytes']}, expected {block}")
    if int(parsed["assoc"]) != assoc:
        raise ValueError(f"Unexpected associativity: got {parsed['assoc']}, expected {assoc}")
    if int(round(parsed["tech_nm"])) != int(TECH_NM):
        raise ValueError(f"Unexpected technology: got {parsed['tech_nm']}nm, expected {TECH_NM}nm")


def write_csv(path: Path, rows: list[dict[str, float | int | str]]) -> None:
    fieldnames = [
        "proc",
        "L1_kB",
        "A_L1_single_32",
        "A_L1_total_32",
        "A_L1_total_28",
        "A_L2_32",
        "A_L2_28",
        "A_core_noL1_28",
        "A_total_new_28",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_params(path: Path, a_l2_32: dict[str, float]) -> None:
    content = f"""Q8 surface flow parameters
- CACTI node used for runs: {int(TECH_NM)}nm
- Normalization target node: {int(TARGET_NM)}nm
- Area scaling factor: ({int(TARGET_NM)}/{int(TECH_NM)})^2 = {AREA_SCALE_32_TO_28:.6f}
- L1 sweep A7 (KB): {L1_SWEEP_KB['A7']}
- L1 sweep A15 (KB): {L1_SWEEP_KB['A15']}
- L2 fixed A7: 512KB / 32B / 8, area_32 = {a_l2_32['A7']:.6f} mm^2
- L2 fixed A15: 512KB / 64B / 16, area_32 = {a_l2_32['A15']:.6f} mm^2
- Core_no_L1_28 A7: {CORE_NO_L1_28['A7']:.6f} mm^2
- Core_no_L1_28 A15: {CORE_NO_L1_28['A15']:.6f} mm^2
"""
    path.write_text(content, encoding="utf-8")


def plot_curves(rows: list[dict[str, float | int | str]], fig_dir: Path) -> None:
    proc_order = ["A7", "A15"]

    plt.figure(figsize=(7.0, 4.4))
    for proc in proc_order:
        proc_rows = [r for r in rows if r["proc"] == proc]
        x = [int(r["L1_kB"]) for r in proc_rows]
        y = [float(r["A_L1_total_28"]) for r in proc_rows]
        plt.plot(x, y, marker="o", linewidth=2, label=proc)
    plt.title("Q8: Surface totale L1 (I-L1 + D-L1) vs taille L1")
    plt.xlabel("Taille L1 (KB)")
    plt.ylabel("Surface (mm^2, normalisee a 28nm)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(fig_dir / "q8_l1_total_area_vs_size_28nm.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7.0, 4.4))
    for proc in proc_order:
        proc_rows = [r for r in rows if r["proc"] == proc]
        x = [int(r["L1_kB"]) for r in proc_rows]
        y = [float(r["A_total_new_28"]) for r in proc_rows]
        plt.plot(x, y, marker="o", linewidth=2, label=proc)
    plt.title("Q8: Surface totale coeur + L1 + L2 vs taille L1")
    plt.xlabel("Taille L1 (KB)")
    plt.ylabel("Surface (mm^2, normalisee a 28nm)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(fig_dir / "q8_total_area_with_l2_vs_size_28nm.png", dpi=180)
    plt.close()


def main() -> None:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    cacti_dir = repo_root / "Projet" / "cacti65"
    out_dir = repo_root / args.out_dir
    cfg_dir = out_dir / "generated_cfg"
    cacti_out_dir = out_dir / "cacti_outputs"
    fig_dir = out_dir / "figures"

    for d in (out_dir, cfg_dir, cacti_out_dir, fig_dir):
        d.mkdir(parents=True, exist_ok=True)

    cacti_bin = cacti_dir / "cacti"
    if not cacti_bin.exists():
        raise FileNotFoundError(
            f"Missing CACTI binary at {cacti_bin}. Compile first with: make CXX=g++ CC=gcc"
        )

    templates = {
        "A7": (cacti_dir / "cache_L1_A7.cfg").read_text(encoding="utf-8"),
        "A15": (cacti_dir / "cache_L1_A15.cfg").read_text(encoding="utf-8"),
    }

    # Fixed L2 area for each processor.
    a_l2_32: dict[str, float] = {}
    for proc in ("A7", "A15"):
        cfg_text = build_cfg(
            templates[proc],
            size_bytes=512 * 1024,
            block_bytes=L2_BLOCK_BYTES[proc],
            assoc=L2_ASSOC[proc],
            tech_um=0.032,
            cache_level="L2",
        )
        cfg_path = cfg_dir / f"{proc.lower()}_L2_512KB.cfg"
        out_path = cacti_out_dir / f"{proc.lower()}_L2_512KB.txt"
        cfg_path.write_text(cfg_text, encoding="utf-8")
        run_cacti(cacti_dir, cfg_path, out_path)
        parsed = parse_cacti_output(out_path)
        validate_cfg(parsed, 512 * 1024, L2_BLOCK_BYTES[proc], L2_ASSOC[proc])
        a_l2_32[proc] = parsed["area_mm2"]

    # L1 sweeps and derived totals.
    rows: list[dict[str, float | int | str]] = []
    for proc in ("A7", "A15"):
        for l1_kb in L1_SWEEP_KB[proc]:
            size_bytes = l1_kb * 1024
            cfg_text = build_cfg(
                templates[proc],
                size_bytes=size_bytes,
                block_bytes=L1_BLOCK_BYTES[proc],
                assoc=L1_ASSOC[proc],
                tech_um=0.032,
                cache_level="L1",
            )
            cfg_path = cfg_dir / f"{proc.lower()}_L1_{l1_kb}KB.cfg"
            out_path = cacti_out_dir / f"{proc.lower()}_L1_{l1_kb}KB.txt"
            cfg_path.write_text(cfg_text, encoding="utf-8")
            run_cacti(cacti_dir, cfg_path, out_path)
            parsed = parse_cacti_output(out_path)
            validate_cfg(parsed, size_bytes, L1_BLOCK_BYTES[proc], L1_ASSOC[proc])

            a_l1_single_32 = parsed["area_mm2"]
            a_l1_total_32 = 2.0 * a_l1_single_32
            a_l1_total_28 = a_l1_total_32 * AREA_SCALE_32_TO_28
            a_l2_28 = a_l2_32[proc] * AREA_SCALE_32_TO_28
            a_total_new_28 = CORE_NO_L1_28[proc] + a_l2_28 + a_l1_total_28

            rows.append(
                {
                    "proc": proc,
                    "L1_kB": l1_kb,
                    "A_L1_single_32": round(a_l1_single_32, 9),
                    "A_L1_total_32": round(a_l1_total_32, 9),
                    "A_L1_total_28": round(a_l1_total_28, 9),
                    "A_L2_32": round(a_l2_32[proc], 9),
                    "A_L2_28": round(a_l2_28, 9),
                    "A_core_noL1_28": round(CORE_NO_L1_28[proc], 9),
                    "A_total_new_28": round(a_total_new_28, 9),
                }
            )

    rows.sort(key=lambda r: (str(r["proc"]), int(r["L1_kB"])))

    csv_path = out_dir / "q8_surface_summary.csv"
    params_path = out_dir / "q8_surface_params.txt"
    write_csv(csv_path, rows)
    write_params(params_path, a_l2_32)
    plot_curves(rows, fig_dir)

    print(f"Q8 flow completed.")
    print(f"CSV: {csv_path}")
    print(f"Params: {params_path}")
    print(f"Figures: {fig_dir}")


if __name__ == "__main__":
    main()
