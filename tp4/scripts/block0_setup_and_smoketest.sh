#!/usr/bin/env bash
set -euo pipefail

# Script para Block 0:
# 1) crear carpetas
# 2) compilar Dijkstra y BlowFish (RISC-V estatico)
# 3) correr 4 smoke tests (A7/A15 x Dijkstra/BlowFish)

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

GEM5_BIN="${GEM5_BIN:-$HOME/gem5/build/RISCV/gem5.opt}"
CFG_A7="$REPO_ROOT/se_A7.py"
CFG_A15="$REPO_ROOT/se_A15.py"

BIN_DIR="$REPO_ROOT/tp4/bin"
DIJKSTRA_BIN="$BIN_DIR/dijkstra_small.riscv"
BLOWFISH_BIN="$BIN_DIR/blowfish.riscv"

RUN_A7_DIJ="$REPO_ROOT/tp4/runs/gem5/A7/dijkstra_small"
RUN_A7_BF="$REPO_ROOT/tp4/runs/gem5/A7/blowfish_small"
RUN_A15_DIJ="$REPO_ROOT/tp4/runs/gem5/A15/dijkstra_small"
RUN_A15_BF="$REPO_ROOT/tp4/runs/gem5/A15/blowfish_small"

mkdir -p \
  "$BIN_DIR" \
  "$RUN_A7_DIJ" \
  "$RUN_A7_BF" \
  "$RUN_A15_DIJ" \
  "$RUN_A15_BF"

riscv64-linux-gnu-gcc -O2 -static \
  -o "$DIJKSTRA_BIN" \
  "$REPO_ROOT/Projet/dijkstra/dijkstra_small.c"

riscv64-linux-gnu-gcc -O2 -static -I "$REPO_ROOT/Projet/blowfish" \
  -o "$BLOWFISH_BIN" \
  "$REPO_ROOT/Projet/blowfish/bf.c" \
  "$REPO_ROOT/Projet/blowfish/bf_skey.c" \
  "$REPO_ROOT/Projet/blowfish/bf_ecb.c" \
  "$REPO_ROOT/Projet/blowfish/bf_enc.c" \
  "$REPO_ROOT/Projet/blowfish/bf_cbc.c" \
  "$REPO_ROOT/Projet/blowfish/bf_cfb64.c" \
  "$REPO_ROOT/Projet/blowfish/bf_ofb64.c"

run_one() {
  local cfg="$1"
  local outdir="$2"
  local bin="$3"
  local options="$4"

  "$GEM5_BIN" -d "$outdir" "$cfg" \
    "--cmd=$bin" \
    "--options=$options"

  # Si gem5 no crea command.txt, lo dejamos manual.
  if [ ! -f "$outdir/command.txt" ]; then
    printf '%s\n' "$GEM5_BIN -d $outdir $cfg --cmd=$bin --options=$options" > "$outdir/command.txt"
  fi
}

DIJKSTRA_OPT="$REPO_ROOT/Projet/dijkstra/input.dat"
A7_BLOWFISH_OPT="e $REPO_ROOT/Projet/blowfish/input_small.asc $RUN_A7_BF/output.enc 0123456789ABCDEF"
A15_BLOWFISH_OPT="e $REPO_ROOT/Projet/blowfish/input_small.asc $RUN_A15_BF/output.enc 0123456789ABCDEF"

run_one "$CFG_A7" "$RUN_A7_DIJ" "$DIJKSTRA_BIN" "$DIJKSTRA_OPT"
run_one "$CFG_A7" "$RUN_A7_BF" "$BLOWFISH_BIN" "$A7_BLOWFISH_OPT"
run_one "$CFG_A15" "$RUN_A15_DIJ" "$DIJKSTRA_BIN" "$DIJKSTRA_OPT"
run_one "$CFG_A15" "$RUN_A15_BF" "$BLOWFISH_BIN" "$A15_BLOWFISH_OPT"

echo "Block 0 terminado."
