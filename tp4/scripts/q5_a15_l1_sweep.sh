#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

GEM5_BIN="${GEM5_BIN:-$HOME/gem5/build/RISCV/gem5.opt}"
CFG_A15="$REPO_ROOT/se_A15.py"

CLOCK="${CLOCK:-2GHz}"
MEM_SIZE="${MEM_SIZE:-2GB}"
MAXINSTS="${MAXINSTS:-0}"
MPLCONFIGDIR="${MPLCONFIGDIR:-/tmp/mplconfig_gem5_q5}"

RUN_BASE="$REPO_ROOT/tp4/runs/gem5/A15"
RESULTS_DIR="$REPO_ROOT/docs/results/q5_a15"
FIG_DIR="$RESULTS_DIR/figures"
OUT_CSV="$RESULTS_DIR/q5_a15_l1_sweep.csv"
SUMMARY_CSV="$RESULTS_DIR/q5_a15_best_config.csv"
PARAMS_TXT="$RESULTS_DIR/q5_a15_gem5_params.txt"

if [[ ! -x "$GEM5_BIN" ]]; then
  echo "ERROR: gem5 binary not found or not executable: $GEM5_BIN" >&2
  exit 1
fi

echo "[Q5] Compiling benchmarks (RISC-V static)..."
make -C "$REPO_ROOT/Projet/dijkstra"
make -C "$REPO_ROOT/Projet/blowfish"

DIJKSTRA_BIN="$REPO_ROOT/Projet/dijkstra/dijkstra_small.riscv"
BLOWFISH_BIN="$REPO_ROOT/Projet/blowfish/bf.riscv"

if [[ ! -f "$DIJKSTRA_BIN" ]]; then
  echo "ERROR: missing binary $DIJKSTRA_BIN" >&2
  exit 1
fi
if [[ ! -f "$BLOWFISH_BIN" ]]; then
  echo "ERROR: missing binary $BLOWFISH_BIN" >&2
  exit 1
fi

mkdir -p "$RUN_BASE" "$RESULTS_DIR" "$FIG_DIR"
mkdir -p "$MPLCONFIGDIR"
export MPLCONFIGDIR

run_one() {
  local outdir="$1"
  local bin="$2"
  local options="$3"
  local l1_size="$4"

  local -a cmd=(
    "$GEM5_BIN"
    -d "$outdir"
    "$CFG_A15"
    "--cmd=$bin"
    "--l1i-size=$l1_size"
    "--l1d-size=$l1_size"
    "--clock=$CLOCK"
    "--mem-size=$MEM_SIZE"
  )

  if [[ "$MAXINSTS" != "0" ]]; then
    cmd+=("--maxinsts=$MAXINSTS")
  fi
  cmd+=("--options=$options")

  mkdir -p "$outdir"
  "${cmd[@]}"

  if [[ ! -f "$outdir/command.txt" ]]; then
    printf '%q ' "${cmd[@]}" > "$outdir/command.txt"
    printf '\n' >> "$outdir/command.txt"
  fi
}

for k in 2 4 8 16 32; do
  l1="${k}kB"
  out_dij="$RUN_BASE/dijkstra_L1_${k}k"
  out_bf="$RUN_BASE/blowfish_L1_${k}k"

  echo "[Q5] Running A15 dijkstra L1=$l1"
  run_one "$out_dij" "$DIJKSTRA_BIN" "$REPO_ROOT/Projet/dijkstra/input.dat" "$l1"

  bf_opts="e $REPO_ROOT/Projet/blowfish/input_small.asc $out_bf/output.enc 0123456789ABCDEF"
  echo "[Q5] Running A15 blowfish L1=$l1"
  run_one "$out_bf" "$BLOWFISH_BIN" "$bf_opts" "$l1"
done

echo "[Q5] Extracting metrics and generating figures..."
python3 "$REPO_ROOT/tp4/scripts/q5_a15_extract_plot.py" \
  --runs-base "$RUN_BASE" \
  --out-csv "$OUT_CSV" \
  --summary-csv "$SUMMARY_CSV" \
  --figures-dir "$FIG_DIR" \
  --params-txt "$PARAMS_TXT"

echo "[Q5] Done."
echo "[Q5] CSV: $OUT_CSV"
echo "[Q5] Summary: $SUMMARY_CSV"
echo "[Q5] Figures: $FIG_DIR"
