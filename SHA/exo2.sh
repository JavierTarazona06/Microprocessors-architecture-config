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
INPUT_LARGE="${INPUT_LARGE:-$SCRIPT_DIR/input_large.asc}"
OUT_FILE="${OUT_FILE:-$SCRIPT_DIR/results_ruu.txt}"

require_file() { [[ -f "$1" ]] || { echo "ERROR: missing file: $1" >&2; exit 1; }; }
require_exec() { [[ -x "$1" ]] || { echo "ERROR: not executable: $1" >&2; exit 1; }; }

require_exec "$GEM5"
require_file "$CFG"
require_file "$BIN"
require_file "$INPUT_LARGE"

cd "$SCRIPT_DIR"

RUU_LIST=(16 32 64 128)

printf "RUU numCycles CPI\n" > "$OUT_FILE"

for RUU in "${RUU_LIST[@]}"; do
  OUT="m5out_ruu_${RUU}"

  if ! "$GEM5" -d "$OUT" "$CFG" \
    --cmd="$BIN" --args="$INPUT_LARGE" \
    --cpu-type=O3 --caches \
    --ialu=4 --imult=1 --fpalu=1 --fpmult=1 --memport=2 \
    --ruu="$RUU" --iq="$RUU" --lq=32 --sq=32; then
    echo "$RUU ERROR ERROR" >> "$OUT_FILE"
    echo "WARN: gem5 run failed for RUU=$RUU (see $OUT)." >&2
    continue
  fi

  STATS_FILE="$OUT/stats.txt"
  CYCLES=$(awk '/^system\.cpu\.numCycles[[:space:]]/ {print $2; exit}' "$STATS_FILE" || true)
  CPI=$(awk '/^system\.cpu\.cpi[[:space:]]/ {print $2; exit}' "$STATS_FILE" || true)

  echo "$RUU ${CYCLES:-NA} ${CPI:-NA}" >> "$OUT_FILE"
done

echo "Wrote $OUT_FILE"
