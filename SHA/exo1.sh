#!/bin/bash
# run_pred_sha.sh
set -euo pipefail

GEM5="$HOME/gem5/build/RISCV/gem5.opt"
CFG="$HOME/ES201-TP/pred_se_fu.py"

BIN="$HOME/ES201-TP/TP4/SHA/sha.riscv"
INPUT_SMALL="$HOME/ES201-TP/TP4/SHA/input_small.asc"
INPUT_LARGE="$HOME/ES201-TP/TP4/SHA/input_large.asc"

BP_LIST=("nottaken" "taken" "bimod" "2lev" "tournament")

run_one () {
  local tag=$1
  local bp=$2
  local input=$3
  local outdir=$4

  $GEM5 -d "$outdir" "$CFG" \
    --cmd="$BIN" --args="$input" \
    --cpu-type=O3 --caches \
    --bpred="$bp" \
    --ialu=4 --imult=1 --fpalu=1 --fpmult=1 --memport=2

  local cycles cpi
  cycles=$(grep -m1 "system.cpu.numCycles" "$outdir/stats.txt" | awk '{print $2}' || true)
  cpi=$(grep -m1 "system.cpu.cpi" "$outdir/stats.txt" | awk '{print $2}' || true)

  printf "%-20s %-10s %-12s %-12s\n" \
    "$tag" "$bp" "${cycles:-NA}" "${cpi:-NA}" >> results_sha.txt
}

echo "RUN                  BP         numCycles     CPI" > results_sha.txt

for bp in "${BP_LIST[@]}"; do
  run_one "sha_small" "$bp" "$INPUT_SMALL" "m5out_sha_small_${bp}"
done

for bp in "${BP_LIST[@]}"; do
  run_one "sha_large" "$bp" "$INPUT_LARGE" "m5out_sha_large_${bp}"
done

echo "Wrote results_sha.txt"
