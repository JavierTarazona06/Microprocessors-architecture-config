#!/bin/bash
set -euo pipefail

GEM5="$HOME/gem5/build/RISCV/gem5.opt"
CFG="$HOME/ES201-TP/pred_se_fu.py"

BIN="$HOME/ES201-TP/TP4/SHA/sha.riscv"
INPUT_LARGE="$HOME/ES201-TP/TP4/SHA/input_large.asc"

# tailles demandées
RUU_LIST=(16 32 64 128)

echo "RUU numCycles CPI" > results_ruu.txt

for RUU in "${RUU_LIST[@]}"; do
  OUT="m5out_ruu_${RUU}"

  $GEM5 -d "$OUT" "$CFG" \
    --cmd="$BIN" --args="$INPUT_LARGE"\
    --cpu-type=O3 --caches \
    --ialu=4 --imult=1 --fpalu=1 --fpmult=1 --memport=2 \
    --ruu="$RUU" --iq="$RUU" --lq=32 --sq=32

  CYCLES=$(grep -m1 "system.cpu.numCycles" "$OUT/stats.txt" | awk '{print $2}')
  CPI=$(grep -m1 "system.cpu.cpi" "$OUT/stats.txt" | awk '{print $2}')

  echo "$RUU $CYCLES $CPI" >> results_ruu.txt
done
