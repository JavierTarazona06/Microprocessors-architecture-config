#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

GEM5_DEFAULT="$HOME/microprocesseur/sourceCode/gem5/build/RISCV/gem5.opt"
CFG_DEFAULT="$REPO_ROOT/pred_se_fu.py"
BIN_DEFAULT="$SCRIPT_DIR/sha.riscv"
if [[ ! -f "$BIN_DEFAULT" && -f "$HOME/microprocesseur/repo_Pierron/ES201-TP/TP4/SHA/sha.riscv" ]]; then
  BIN_DEFAULT="$HOME/microprocesseur/repo_Pierron/ES201-TP/TP4/SHA/sha.riscv"
fi

GEM5="${GEM5:-$GEM5_DEFAULT}"
CFG="${CFG:-$CFG_DEFAULT}"
BIN="${BIN:-$BIN_DEFAULT}"
INPUT_SMALL="${INPUT_SMALL:-$SCRIPT_DIR/input_small.asc}"
INPUT_LARGE="${INPUT_LARGE:-$SCRIPT_DIR/input_large.asc}"
OUT_FILE="${OUT_FILE:-$SCRIPT_DIR/results_sha.txt}"

require_file() { [[ -f "$1" ]] || { echo "ERROR: missing file: $1" >&2; exit 1; }; }
require_exec() { [[ -x "$1" ]] || { echo "ERROR: not executable: $1" >&2; exit 1; }; }

require_exec "$GEM5"
require_file "$CFG"
require_file "$BIN"
require_file "$INPUT_SMALL"
require_file "$INPUT_LARGE"

cd "$SCRIPT_DIR"

BP_LIST=("nottaken" "taken" "bimod" "2lev" "tournament")

run_one() {
  local tag=$1
  local bp=$2
  local input=$3
  local outdir=$4

  if ! "$GEM5" -d "$outdir" "$CFG" \
    --cmd="$BIN" --args="$input" \
    --cpu-type=O3 --caches \
    --bpred="$bp" \
    --ialu=4 --imult=1 --fpalu=1 --fpmult=1 --memport=2; then
    printf "%-20s %-10s %-12s %-12s\n" "$tag" "$bp" "ERROR" "ERROR" >> "$OUT_FILE"
    echo "WARN: gem5 run failed for $tag/$bp (see $outdir)." >&2
    return 0
  fi

  local stats_file="$outdir/stats.txt"
  if [[ ! -s "$stats_file" ]]; then
    printf "%-20s %-10s %-12s %-12s\n" "$tag" "$bp" "NA" "NA" >> "$OUT_FILE"
    echo "WARN: missing or empty stats file for $tag/$bp ($stats_file)." >&2
    return 0
  fi

  local cycles cpi
  cycles=$(awk '/^system\.cpu\.numCycles[[:space:]]/ {print $2; exit}' "$stats_file" || true)
  cpi=$(awk '/^system\.cpu\.cpi[[:space:]]/ {print $2; exit}' "$stats_file" || true)

  printf "%-20s %-10s %-12s %-12s\n" \
    "$tag" "$bp" "${cycles:-NA}" "${cpi:-NA}" >> "$OUT_FILE"
}

printf "RUN                  BP         numCycles     CPI\n" > "$OUT_FILE"

for bp in "${BP_LIST[@]}"; do
  run_one "sha_small" "$bp" "$INPUT_SMALL" "m5out_sha_small_${bp}"
done

for bp in "${BP_LIST[@]}"; do
  run_one "sha_large" "$bp" "$INPUT_LARGE" "m5out_sha_large_${bp}"
done

echo "Wrote $OUT_FILE"
