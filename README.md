# Microprocessors-architecture-config

Jeu de scripts/configs pour les TP d’architecture microprocesseurs (gem5, RISC-V, CACTI).

## Arborescence 
- `/runs/` : sorties gem5/CACTI par run (`command.txt`, `config.ini`, `stats.txt`…).
- `docs/results/` : CSV consolidés (dont `manifest.csv`).
- `docs/figures/` : graphiques exportés.
- `docs/report/` : sources et PDF du rapport.

## Fichier `docs/results/manifest.csv`
Catalogue des runs gem5. Chaque ligne = un run, traçable via `run_path`.

- `ex` : exercice/série (ex3, ex4, cacti…)
- `core` : config cible (C1, C2, A7, A15…)
- `app` : binaire exécuté (P1, P2, dijkstra, blowfish…)
- `config` : label lisible de la config (ex : `C1_directmap`)
- `l1i_kb`, `l1d_kb`, `l2_kb` : tailles IL1/DL1/L2 (kB)
- `blk_b` : taille de ligne (B)
- `l1i_assoc`, `l1d_assoc`, `l2_assoc` : associativité
- `cpu_type` : CPU gem5 (TimingSimpleCPU, MinorCPU, O3…)
- `simInsts` : instructions simulées
- `numCycles` : cycles simulés
- `ipc` : instructions par cycle
- `il1_miss`, `dl1_miss`, `l2_miss` : miss rates `overallMissRate`
- `notes` : commentaires libres (params, anomalies)
- `run_path` : dossier du run contenant `config.ini`, `stats.txt`, `command.txt`


## Exercice 3

## Contenu de `exo3/`
- `exo3/Makefile` : compile les 4 variantes de multiplication de matrices (`normale`, `pointer`, `tempo`, `unrol`) en natif et en RISC-V statique (`*.riscv`) pour gem5. Para compilar RISC corre exo3/compilationRISC.sh
- `exo3/mm.c` : source historique de tests de multiplication de matrices (commentaires sur variantes et temporisation).
- `exo3/normale.c`, `exo3/pointer.c`, `exo3/tempo.c`, `exo3/unrol.c` : implémentations des 4 variantes (ex : `pointer.c` utilise des pointeurs et vérifie le résultat).
- `exo3/normale`, `exo3/pointer`, `exo3/tempo`, `exo3/unrol` : binaires natifs déjà générés (les versions RISC-V sont `*.riscv` après compilation).
- `exo3/script.sh` : ébauche de script pour lancer des runs gem5 et extraire les miss rates depuis `stats.txt`.


## Exercice 4

Objectif : exécuter les sweeps gem5/CACTI et produire les résultats/graphes de Q4, Q8 et Q9.

### Prérequis
- Avoir `g++`, `make` et `python3`.
- Depuis la racine du repo : `Microprocessors-architecture-config`.

### Compiler CACTI
```bash
cd Projet/cacti65
make CXX=g++ CC=gcc
```

### Exécuter CACTI manuellement
```bash
cd Projet/cacti65
./cacti -infile cache.cfg
```

Exemples utiles :
```bash
./cacti -infile cache_L1_A7.cfg
./cacti -infile cache_L1_A15.cfg
```

### Exécuter le flux complet Q8
Depuis la racine du repo :
```bash
python3 tp4/scripts/q8_surface_flow.py
```

Ce script :
- lance les runs CACTI pour le sweep L1 (A7/A15) et L2 fixe (512KB),
- extrait les surfaces,
- normalise 32nm -> 28nm,
- génère CSV + figures.

Sorties principales :
- `docs/results/q8_surface/q8_surface_summary.csv`
- `docs/results/q8_surface/q8_surface_params.txt`
- `docs/results/q8_surface/figures/q8_l1_total_area_vs_size_28nm.png`
- `docs/results/q8_surface/figures/q8_total_area_with_l2_vs_size_28nm.png`

### Exécuter le sweep Q4 (A7)
Depuis la racine du repo :
```bash
tp4/scripts/q4_a7_l1_sweep.sh
```

Ce script :
- lance gem5 A7 pour `L1 = 1,2,4,8,16 kB` (I-L1 = D-L1),
- exécute `dijkstra` et `blowfish`,
- extrait automatiquement les métriques (IPC, cycles, miss rates, branchement).

Sorties principales :
- `docs/results/q4_a7/q4_a7_l1_sweep.csv`
- `docs/results/q4_a7/q4_a7_best_config.csv`
- `docs/results/q4_a7/q4_a7_gem5_params.txt`
- `docs/results/q4_a7/figures/`

### Calculer Q9 (efficacité surfacique IPC/mm²)
Depuis la racine du repo :
```bash
python3 tp4/scripts/q9_surface_efficiency.py \
  --a7-ipc-csv docs/results/q4_a7/q4_a7_l1_sweep.csv \
  --a15-ipc-csv docs/results/q5_a15/q5_a15_l1_sweep.csv \
  --area-csv docs/results/q8_surface/q8_surface_summary.csv \
  --out-csv docs/results/q9_surface/q9_surface_efficiency.csv \
  --best-csv docs/results/q9_surface/q9_surface_best_by_app_proc.csv \
  --figures-dir docs/results/q9_surface/figures \
  --params-txt docs/results/q9_surface/q9_surface_params.txt
```

Sorties principales :
- `docs/results/q9_surface/q9_surface_efficiency.csv`
- `docs/results/q9_surface/q9_surface_best_by_app_proc.csv`
- `docs/results/q9_surface/q9_surface_params.txt`
- `docs/results/q9_surface/figures/q9_dijkstra_se_vs_l1.png`
- `docs/results/q9_surface/figures/q9_blowfish_se_vs_l1.png`
