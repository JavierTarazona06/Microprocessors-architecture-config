## Objectif
Mesurer les performances d'un programme en utilisant un simulateur de processeur
RISC-V (gem5 en mode SE - System Call Emulation). Les informations d'installation
de gem5 se trouvent en Annexe 3. (A completer pour WSL)

## Pre-requis
- gem5 compile pour RISC-V.
- Outil de cross-compilation `riscv64-linux-gnu-gcc`.
- Un dossier de travail, par exemple `~/tp1`.

## Etapes
1. Ecrire un programme en C effectuant la somme de deux vecteurs de taille N = 50
   initialises de maniere aleatoire.
2. Compiler le programme en binaire RISC-V :
```bash
riscv64-linux-gnu-gcc -O2 -static -o vadd.riscv vadd.c

# Eviter que le compilateur ne suroptimse pas
riscv64-linux-gnu-gcc -O0 -static -o conv_int.riscv conv_int.c

# From ASM
riscv64-linux-gnu-gcc -x assembler -march=rv64g -mabi=lp64 -no-pie -static -nostdlib -o tp2/pt1_a.riscv tp2/pt1_a.asm

# Imposer des calculs
riscv64-linux-gnu-gcc -O2 -static -fno-lto -I/home/javit/gem5/include conv_m5.c /home/javit/gem5/util/m5/build/riscv/out/libm5.a -o conv_m5.riscv

```
3. Lancer le simulateur avec un CPU in-order (MinorCPU) :
```bash
# RISC 
cd ~/gem5
build/RISCV/gem5.opt /home/javit/microprocesseurs/RISCV_se.py -b /home/javit/microprocesseurs/tp1/vadd.riscv

# Original
cd ~/gem5
build/RISCV/gem5.opt configs/deprecated/example/se.py -c /home/javit/microprocesseurs/tp1/vadd.riscv

# High Level execution, more expensive
cd ~/gem5
build/RISCV/gem5.opt configs/deprecated/example/se.py \
  --cpu-type=MinorCPU --caches --l2cache -c /home/javit/microprocesseurs/tp1/vadd.riscv


```

## Resultats
Les resultats se trouvent dans `m5out/stats.txt`. Pour extraire les metriques utiles :
```bash
grep -E "simInsts|system.cpu.numCycles|numCycles|ipc|cpi" m5out/stats.txt

grep -E "simInsts|numLoadInsts|numStoreInsts|numBranches|numIntInsts|numFpInsts" m5out/stats.txt
```

## Notes
- Adaptez le chemin du binaire si votre dossier de travail est different.
- Si `m5out/` existe deja, gem5 ecrasera les fichiers precedents.

## Block 0 (TP4 Ex4) — Dijkstra + BlowFish (A7/A15)

Script recommande (reproductible) :
```bash
cd /home/meneses/microprocesseur/Microprocessors-architecture-config
bash tp4/scripts/block0_setup_and_smoketest.sh
```

Points importants :
- Les executions gem5 utilisent `-d <outdir>`, donc `config.ini` et `stats.txt` sont produits dans ce dossier.
- Pour BlowFish, passer les arguments via une seule chaine :
  `--options="e <repo>/Projet/blowfish/input_small.asc <outdir>/output.enc 0123456789ABCDEF"`.
- `command.txt` doit etre present dans chaque dossier de run. Si gem5 ne le genere pas, le script Block 0 le cree avec la commande exacte executee.

## Q5 (TP4 Ex4) — Cortex A15 L1 sweep

Script recommande (compile + 10 runs + extraction + figures) :
```bash
cd /home/javit/microprocesseurs/Microprocessors-architecture-config
bash tp4/scripts/q5_a15_l1_sweep.sh
```

Ce script effectue :
- Compilation RISC-V statique de `dijkstra_small.riscv` et `bf.riscv`.
- Sweep A15 avec `I-L1 = D-L1 = {2,4,8,16,32}kB` et `L2=512kB` fixe.
- 10 runs gem5 dans `tp4/runs/gem5/A15/{dijkstra,blowfish}_L1_*k/`.
- Extraction des metriques et generation des figures Q5.

Sorties generees :
- CSV detaille : `docs/results/q5_a15/q5_a15_l1_sweep.csv`
- Resume meilleur L1 : `docs/results/q5_a15/q5_a15_best_config.csv`
- Parametres gem5 utilises : `docs/results/q5_a15/q5_a15_gem5_params.txt`
- Figures PNG : `docs/results/q5_a15/figures/`
