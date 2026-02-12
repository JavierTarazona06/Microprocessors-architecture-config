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
