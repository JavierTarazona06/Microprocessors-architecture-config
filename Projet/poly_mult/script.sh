#!/bin/bash
# run_poly_mult.sh — RISC-V / (A15-like config script) / gem5 SE
set -euo pipefail

GEM5="$HOME/gem5/build/RISCV/gem5.opt"
CFG="$HOME/ES201-TP/TP4/se_A7.py"
BASE="$HOME/ES201-TP/TP4/Projet/poly_mult"

BIN="$BASE/poly_mult.riscv"
OUTDIR="$BASE/m5out_poly_mult_rv"

rm -rf "$OUTDIR"

echo "==> RUN poly_mult (RISC-V, gem5 SE)"

"$GEM5" -d "$OUTDIR" "$CFG" \
  --cmd="$BIN"

echo
echo "==> Simulation terminée"

if [ -f "$OUTDIR/stats.txt" ]; then
  echo "==> Stats principales"
  grep -E "sim_seconds|sim_ticks|sim_insts|numCycles|ipc|cpi" "$OUTDIR/stats.txt" || true

  echo
  echo "==> Miss rates cache (gem5 naming variants)"
  # Selon les scripts, les objets peuvent s'appeler icache/dcache/l2cache OU cpu.icache/cpu.dcache
  grep -E "MissRate|miss_rate" "$OUTDIR/stats.txt" \
    | grep -Ei "icache|dcache|l2" || true

  echo
  echo "==> Hits/Misses (si présents)"
  grep -E "overallHits|overallMisses|demandHits|demandMisses|hits::total|misses::total" "$OUTDIR/stats.txt" \
    | grep -Ei "icache|dcache|l2" || true
else
  echo "ERREUR: stats.txt absent"
fi

echo
echo "Résultats dans $OUTDIR"
