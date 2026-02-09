## Lundi 09/02 — Javier
- Créer l’arborescence `tp4/{runs,results,figures,report}` et `tp4/runs/{bin,gem5}`.
- Générer le gabarit `tp4/results/manifest.csv` avec l’en-tête : `ex,core,app,config,l1i_kb,l1d_kb,l2_kb,blk_b,l1i_assoc,l1d_assoc,l2_assoc,cpu_type,simInsts,numCycles,ipc,il1_miss,dl1_miss,l2_miss,notes,run_path`.
- Compiler **P1 (matmul)** en binaire RISC-V statique dans `tp4/runs/bin/P1.riscv` (`riscv64-linux-gnu-gcc -O2 -static -march=rv64gc -mabi=lp64 -fno-lto`).
- Lancer un smoke run gem5 (config **C1**: IL1 4KB DM, DL1 4KB DM, L2 32KB DM, bloc 32B) avec `se.py` et garder les sorties dans `tp4/runs/gem5/<run_id>/`.
- Extraer y verificar en `stats.txt` los miss rates: `icache.overallMissRate`, `dcache.overallMissRate`, `l2cache.overallMissRate`, y registrar la línea correspondiente en `manifest.csv`.
