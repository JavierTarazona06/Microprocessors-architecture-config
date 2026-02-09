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
