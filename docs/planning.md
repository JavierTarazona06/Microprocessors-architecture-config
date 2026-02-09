# TP4 — Planning (quadrinôme Javier / Carlos / Maeva / Jair)

Période de réalisation visée : **du lundi 9/02/2026 au lundi 16/02/2026** (7 jours de production + 1 jour tampon).  
Objectif : terminer **Exercice 3** (caches + miss rate avec gem5) et **Exercice 4** (A7/A15 : profiling, sweep L1→perf, CACTI surface, énergie, choix big.LITTLE), avec **répartition équitable** et **maximum de parallélisation**.

---

## A) Work Packages (WP)

### WP0 — Cadre commun (outillage, conventions, squelette de rapport)
- **Questions couvertes** : transverses (reproductibilité, paramètres gem5, organisation).
- **Inputs** : consigne (TP4), installation gem5 (ISA **RISCV** en SE), `riscv64-linux-gnu-gcc`, sources (MiBench : **Dijkstra**, **BlowFish**) + codes matrice (P1–P4).
- **Outputs** :
  - Arborescence de travail (`runs/`, `results/`, `figures/`, `report/`).
  - Convention de nommage des expériences + gabarit CSV “manifest”.
  - Scripts/config gem5 **paramétrables** (Ex3 : C1/C2 ; Ex4 : A7/A15 + taille L1).
  - Squelette du rapport (sections Ex3/Ex4, emplacements des figures/tableaux).
- **Definition of Done (DoD)** :
  - Chaque run gem5 produit un dossier avec `command.txt`, `config.ini`, `stats.txt`.
  - Un fichier `results/manifest.csv` existe et peut être rempli par tous.
  - Deux personnes différentes peuvent relancer **un** run “smoke test” et obtenir des stats cohérentes.

### WP1 — Exercice 3 : caches & miss rates (Q1–Q3)
- **Consigne / artefacts demandés**
  - **Q1** : compléter **Tableau 8** (paramètres gem5 pour C1/C2).
  - **Q2** : compléter **Tableaux 9–11** (miss rates) à partir de gem5 :
    - `icache.overallMissRate`, `dcache.overallMissRate`, `l2cache.overallMissRate`.
  - **Q3** : analyse (localité code) sur les 4 algorithmes.
- **Paramètres clés (extraits)**
  - Config **C1** : IL1 4KB direct-mapped ; DL1 4KB direct-mapped ; L2 32KB direct-mapped ; block **32B** ; remplacement **LRU**.
  - Config **C2** : IL1 4KB direct-mapped ; DL1 4KB **2-way** ; L2 32KB **4-way** ; block **32B** ; remplacement **LRU**.
  - Programmes : **P1 (normale), P2 (pointeur), P3 (tempo), P4 (unrol)**.
- **Inputs** : binaires P1–P4 (multiplication matrices), gem5 + script/CLI caches.
- **Outputs** : Tableau 8 + Tableaux 9–11 complétés + texte Q3 (~½ page max) + `results/ex3_missrates.csv`.
- **DoD** : 8 runs (4 programmes × 2 configs) terminés, stats tracées, extraction vérifiée par un pair.

### WP2 — Exercice 4 : profiling (Q1–Q3)
- **Consigne / artefacts demandés**
  - **Q1** : tableau “% par classe d’instructions” pour **Dijkstra** et **BlowFish**.
  - **Q2** : 5 lignes max : quelle catégorie améliorer et pourquoi.
  - **Q3** : comparaison avec TP2 (SSCA2-BCS, SHA-1, produit de polynômes) : similitudes/divergences.
- **Inputs** : binaires RISC-V statiques de Dijkstra + BlowFish, gem5 stats “instruction classes”.
- **Outputs** : tableau profiling + 2 paragraphes (Q2/Q3) + `results/ex4_profiling.csv`.
- **DoD** : définition des classes d’instructions figée (mêmes catégories pour les 2 applis) + vérification croisée sur 1 run.
  - Classes conseillées (au minimum) : **ALU entier**, **mult/div entier**, **FP**, **load**, **store**, **branch**, **autres** (définition explicitée dans le rapport).

### WP3 — Exercice 4 : sweep performance Cortex **A7** (Q4)
- **Consigne / artefacts demandés**
  - **Q4** : figures de performances détaillées vs taille L1 (perf générale, IPC, hiérarchie mémoire, prédiction branchement, …) + analyse + meilleure config L1 pour Dijkstra et pour BlowFish.
  - Mention explicite des **paramètres d’exécution gem5**.
- **Paramètres clés (extraits)**
  - **L2 fixe = 512KB**, out-of-order, variation **simultanée IL1/DL1** : **1/2/4/8/16KB**.
  - Config “RISCV A7” (Tableau 12) : blocs **32B**, assoc **2** (L1), L2 bloc **32B** assoc **8**, BP **bimodal** (BTB=256), etc.
- **Inputs** : gem5 config “A7”, binaires Dijkstra + BlowFish.
- **Outputs** : 2 séries de courbes (Dijkstra, BlowFish) + dataset `results/ex4_a7_sweep.csv`.
- **DoD** : 10 runs (5 tailles × 2 applis) + figures reproductibles (scripts + source des stats).
  - Métriques minimum à extraire (et tracer au moins en partie) :
    - Perf : `simInsts`, `system.cpu.numCycles`, `system.cpu.ipc`, `system.cpu.cpi`
    - Mémoire : `icache.overallMissRate`, `dcache.overallMissRate`, `l2cache.overallMissRate`
    - Branchement : un taux de misprediction (ex. `condIncorrect/condPredicted` selon stats disponibles)

### WP4 — Exercice 4 : sweep performance Cortex **A15** (Q5)
- **Consigne / artefacts demandés**
  - **Q5** : mêmes attendus que Q4, mais pour Cortex A15 + meilleure config L1 pour chaque appli.
- **Paramètres clés (extraits)**
  - **L2 fixe = 512KB**, variation IL1/DL1 : **2/4/8/16/32KB**.
  - Config “RISCV A15” (Tableau 12) : blocs **64B**, assoc **2** (L1), L2 bloc **64B** assoc **16**, BP **2-level** (BTB=256), etc.
- **Inputs** : gem5 config “A15”, binaires Dijkstra + BlowFish.
- **Outputs** : figures + `results/ex4_a15_sweep.csv`.
- **DoD** : 10 runs (5 tailles × 2 applis) + scripts d’extraction/plot validés.
  - Métriques minimum à extraire : mêmes métriques que WP3, avec cohérence des colonnes CSV.

### WP5 — CACTI : surface & efficacité surfacique (Q6–Q9)
- **Consigne / artefacts demandés**
  - **Q6** : lire `cache.cfg` : paramètres par défaut (taille/bloc/assoc/techno).
  - **Q7** : surface L1 (Tableau 12) en mm² + % surface totale (A7=0.45mm², A15=2mm²) + taille cœurs hors L1 + analyse.
  - **Q8** : surfaces L1 pour toutes tailles possibles (A7 : 1→16KB, A15 : 2→32KB) + surface totale avec **L2=512KB** (graphes).
  - **Q9** : efficacité surfacique = `IPC / surface(mm²)` (perf + surface).
- **Inputs** : CACTI (28nm, sinon 32nm), paramètres caches (taille/bloc/assoc), IPC issus WP3/WP4.
- **Outputs** : `results/cacti_areas.csv`, graphes surface vs taille, graphes `IPC/surface`, texte d’analyse.
- **DoD** : tous les fichiers `cache_*.cfg` versionnés + sorties CACTI conservées + calculs traçables (CSV).

### WP6 — Énergie & choix big.LITTLE (Q10–Q14)
- **Consigne / artefacts demandés**
  - **Q10** : puissance à fréquence max (données : A7=0.10 mW/MHz @ 1.0GHz ; A15=0.20 mW/MHz @ 2.5GHz).
  - **Q11** : efficacité énergétique = `IPC / consommation(mW)` (à fmax) pour chaque config L1.
  - **Q12** : meilleure config L1 de big.LITTLE pour Dijkstra et BlowFish (basée sur Q10–Q11).
  - **Q13 (facultatif)** : compromis si non équivalent.
  - **Q14 (facultatif)** : méthode de spécification multi-applications.
- **Inputs** : IPC (WP3/WP4), surfaces (WP5), puissance (énoncé).
- **Outputs** : tableaux/graphes énergie, recommandation big.LITTLE argumentée, conclusion.
- **DoD** : recommandations cohérentes avec données (perf/surface/énergie) + hypothèses explicites.

### WP7 — Intégration & rédaction finale (rapport + QA)
- **Inputs** : tous résultats WPs 1–6.
- **Outputs** : PDF final (format : `TP4-nom1-nom2-nom3-nom4.pdf`), figures lisibles, annexes (commandes gem5, tableaux bruts).
- **DoD** :
  - Toutes questions répondues (Ex3 Q1–Q3, Ex4 Q1–Q12 + optionnels si choisis).
  - Tableaux/figures numérotés, légendés, unités claires, cohérence des notations (kB/KB, IPC, mm², mW).
  - Checklist de reproductibilité validée (cf. section C).

---

## B) Planning jour par jour (9 → 16 février 2026)

> Hypothèse : chaque membre peut lancer des runs gem5 en parallèle (un run par machine) et déposer les résultats dans une arborescence commune (Git/drive).  
> Point de synchro = réunion flash 15–20 min, obligatoire.

| Jour / objectif | Javier | Carlos | Maeva | Jair | Livrables du jour | Dépendances (minimiser) |
|---|---|---|---|---|---|---|
| **Lun 09/02** — Kick-off + jalon “binaires prêts” | Met en place l’arborescence `tp4/{runs,results,figures,report}` + gabarit `manifest.csv`. Compile **P1** (matmul) en RISC-V statique + 1 *smoke run* gem5 (C1) pour valider l’extraction des miss rates. | Patch/valide les Makefiles MiBench + compile **Dijkstra** en RISC-V statique + 1 *smoke run* gem5. Compile aussi **P2** (matmul) en RISC-V statique. | Compile **P3** (matmul) en RISC-V statique + *smoke run* gem5. Prépare le brouillon du Tableau 8 (mapping paramètres gem5 C1/C2). | Installe/valide CACTI (28nm sinon 32nm) + relève Q6 (paramètres par défaut). Compile **P4** (matmul) en RISC-V statique. | **Jalon M0 “binaires prêts”** : P1–P4 + Dijkstra (et idéalement BlowFish) + au moins 2 *smoke runs* gem5 + `results/manifest.csv` + conventions de nommage. | `riscv64-linux-gnu-gcc` opérationnel + sources accessibles. |
| **Mar 10/02** — Ex3 runs + Sync #1 (alignement extraction) | **Ex3** : lance **P1** sur **C1 & C2** (2 runs). Extrait miss rates il1/dl1/l2. (Si BlowFish manque : aide Carlos à le compiler.) | **Ex3** : lance **P2** sur **C1 & C2** (2 runs). Compile/valide **BlowFish** (MiBench) si pas terminé + partage binaires/commandes. | **Ex3** : lance **P3** sur **C1 & C2** (2 runs). Commence Q3 (localité code) + valide le format CSV. | **Ex3** : lance **P4** sur **C1 & C2** (2 runs). Prépare templates CACTI (cfg générables) pour L1 A7/A15 + L2. | Tableaux 9–11 complétés à 100% + Tableau 8 figé. **Sync #1** : conventions stats + chemins + format CSV. | Dépendances minimisées : chaque membre compile son P# ; MiBench validé au plus tard fin J2. |
| **Mer 11/02** — Profiling + début sweeps perf (50–60% runs) | **Profiling Dijkstra** (1 run) + **A15/Dijkstra** : tailles L1 **2/4/8KB** (3 runs). Dépose stats + CSV IPC/cycles. | **Profiling BlowFish** (1 run) + **A7/BlowFish** : tailles L1 **1/2/4KB** (3 runs). | **A7/Dijkstra** : tailles L1 **1/2/4KB** (3 runs). Début figures Q4 (gabarit plot). | **A15/BlowFish** : tailles L1 **2/4/8KB** (3 runs). Lance CACTI “baseline” (L1 32KB + L2 512KB) pour A7/A15. | `results/ex4_profiling.csv` (brouillon), `results/ex4_*_sweep.csv` partiels, scripts d’extraction (même colonnes). | Binaires Dijkstra/BlowFish **validés** (jalon M0/J2). |
| **Jeu 12/02** — Fin sweeps perf + extraction homogène | **A15/Dijkstra** : tailles **16/32KB** (2 runs). Début analyse Q5 (tendance + meilleur L1). | **A7/BlowFish** : tailles **8/16KB** (2 runs). Commence analyse Q4 (BlowFish). | **A7/Dijkstra** : tailles **8/16KB** (2 runs). Commence analyse Q4 (Dijkstra). | **A15/BlowFish** : tailles **16/32KB** (2 runs). CACTI : sweep complet L1 A7 (1→16KB) + L2 A7 (512KB). | Datasets Ex4 complets côté perf (20 runs) + 1ère version figures IPC vs L1 (A7/A15). | Aucun si binaires OK ; sinon replanifier compilation en priorité. |
| **Ven 13/02** — CACTI + efficacités + Sync #2 (revue résultats) | CACTI : sweep complet L1 A15 (2→32KB) + L2 A15 (512KB). Calcule surfaces totales (avec L2) + `IPC/surface` (A15/Dijkstra). | Calcule puissance (Q10) + efficacité énergétique (Q11) pour **A7/BlowFish** dès que surfaces A7 dispo. Revoit extraction miss rates Ex3 (cohérence). | Finalise tableau profiling (Q1) + texte Q2/Q3 (TP2 vs Ex4). Calcule `IPC/surface` & `IPC/power` pour **A7/Dijkstra**. | Consolidation CACTI (A7 + L2) + aide intégration datasets. Prépare trame décision big.LITTLE (Q12–Q14). | `results/cacti_areas.csv` complet, graphes surface vs taille, `results/derived_efficiency.csv` (IPC/surface + IPC/power), **Sync #2** : validation figures + “best L1” provisoire. | Dépend : surfaces CACTI + IPC extraits de tous. |
| **Sam 14/02** — Rédaction sections + figures finales | Rédige Ex4 Q5 (A15/Dijkstra) + partie CACTI A15 (Q7–Q9). Met en page figures A15. | Rédige Ex4 Q4 (A7/BlowFish) + énergie Q10–Q11 (partie A7). Relecture Ex3. | Rédige Ex4 Q4 (A7/Dijkstra) + Profiling Q1–Q3. Harmonise styles de figures (axes/units). | Rédige Ex4 Q5 (A15/BlowFish) + CACTI A7 (Q6–Q9) + prépare Q12–Q14. | Brouillon complet du rapport (toutes sections remplies, figures insérées), Tableaux 8–11 propres, légendes. | Dépend : données finalisées (sinon “TODO” explicite + plan de rattrapage). |
| **Dim 15/02** — Intégration + QA + Sync #3 (revue finale) | Intègre toutes figures/tableaux, vérifie cohérence notations, compile PDF “release candidate”. | Vérifie reproductibilité : 1 run gem5 d’un autre membre (replay rapide ou re-parse stats) + check extraction. | Relecture globale (orthographe, clarté) + vérifie que chaque question a une réponse explicite. | Finalise recommandation big.LITTLE (Q12) + optionnels Q13/Q14 si temps. | PDF RC + checklist QA remplie. **Sync #3** : décision “go/no-go” + liste corrections. | Dépend : convergence sur figures finales. |
| **Lun 16/02** — Tampon / corrections / gel du rendu | Applique corrections finales + génère PDF final et archive résultats. | Vérifie que toutes commandes gem5 sont documentées (commandes + paramètres). | Vérifie tableaux finaux et renumérotation (Tableaux/Figures). | Vérifie cohérence énergie/surface/perf dans la conclusion big.LITTLE. | PDF final + dossier `results/` complet + package de reproductibilité (manifest + scripts). | Aucun (jour tampon). |

---

## C) Standard de travail (très bref)

### Arborescence recommandée (dans `tp4/`)
- `tp4/runs/gem5/<ex>/<core>/<app>/<run_id>/` : `command.txt`, `config.ini`, `stats.txt`, `stdout.log`
- `tp4/runs/cacti/cfg/` et `tp4/runs/cacti/out/`
- `tp4/results/` : CSV consolidés (`ex3_missrates.csv`, `ex4_*_sweep.csv`, `cacti_areas.csv`, `derived_efficiency.csv`)
- `tp4/figures/` : figures exportées (PNG/PDF)
- `tp4/report/` : sources du rapport + PDF

### Convention de nommage des expériences
- Format conseillé : `ex{3|4}_{core}_{app}_L1i{X}_L1d{X}_L2{Y}_blk{B}_a{assoc}_bp{type}_{date}_{owner}`
- Exemple : `ex4_A7_dijkstra_L1i4kB_L1d4kB_L2512kB_blk32_a2_bpBimodal_2026-02-12_maeva`

### Gabarit CSV (colonnes minimales)
- `ex,core,app,config,l1i_kb,l1d_kb,l2_kb,blk_b,l1i_assoc,l1d_assoc,l2_assoc,bp,simInsts,numCycles,ipc,il1_miss,dl1_miss,l2_miss,notes,run_path`

### Checklist finale avant consolidation PDF
- Chaque figure = titre + axes + unités + légende + source (CSV).
- Chaque tableau = valeurs traçables (ligne → run_path), cohérence kB/KB et mm²/mW.
- Pour **chaque** run gem5 : `command.txt` présent + `config.ini` cohérent avec la taille L1/L2 demandée.
- Vérification croisée : 1 extraction de stats relue par un autre membre.
- Couverture : Ex3 Q1–Q3 ; Ex4 Q1–Q12 (et Q13–Q14 si choisis).
