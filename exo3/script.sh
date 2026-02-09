#!/usr/bin/env python3
set -euo pipefail

# --------- CHEMINS A ADAPTER ----------
GEM5="$HOME/gem5/build/RISCV/gem5.opt"
CFG="$HOME/ES201-TP/se_cache.py"

BIN_DIR="$HOME/ES201-TP/TP4/exo3/"   # là où sont les .riscv
# -------------------------------------

PROGS=("normale" "pointer" "tempo" "unrol")
CONFS=("C1" "C2")

run_one () {
  local prog=$1
  local conf=$2
  local outdir=$3

  # $GEM5 -d "$outdir" "$CFG" \
  #   --cmd="$BIN_DIR/${prog}.riscv" \
  #   --cpu-type=timing --caches \
  #   --conf="$conf" --line-size=32

  local imiss dmiss l2miss
  imiss=$(grep -m1 -E "icache.*MissRate::total|icache.*overallMissRate::total" "$outdir/stats.txt" | awk '{print $2}' || true)
  dmiss=$(grep -m1 -E "dcache.*MissRate::total|dcache.*overallMissRate::total" "$outdir/stats.txt" | awk '{print $2}' || true)
  l2miss=$(grep -m1 -E "l2cache.*MissRate::total|l2cache.*overallMissRate::total" "$outdir/stats.txt" | awk '{print $2}' || true)

  printf "%-10s %-4s %-12s %-12s %-12s\n" \
    "$prog" "$conf" "${imiss:-NA}" "${dmiss:-NA}" "${l2miss:-NA}" >> results_matrix_cache.txt
}

echo "PROG       CONF I_miss       D_miss       L2_miss" > results_matrix_cache.txt

for p in "${PROGS[@]}"; do
  for c in "${CONFS[@]}"; do
    echo "==> RUN $p / $c"
    run_one "$p" "$c" "m5out_${p}_${c}"
  done
done

echo "Wrote results_matrix_cache.txt"
