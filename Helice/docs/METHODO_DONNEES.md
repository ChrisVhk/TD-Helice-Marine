# Méthode des données — du solveur à la figure

Pour les étudiants ET l'enseignant. Chaque nombre ci-dessous porte sa source exacte —
aucun ne doit être recopié ailleurs sans revenir ici. Valeurs canoniques du cas :
`Helice/docs/PARAMETRES_CAS.md`.

## 1. La chaîne, fichier par fichier

**`system/propellerInfo`** (functionObject OpenFOAM natif, `libs (forces)`) — clés qui
comptent : `patches ("propeller.*")`, `radius 0,113689` (D=2×radius), `n 25,15`,
`axis (0 1 0)`, `rotationMode specified`, `rhoInf 1,2`, `writePropellerPerformance yes`.
Exécuté par défaut à CHAQUE PAS DE TEMPS interne du solveur (comportement standard
d'un functionObject OpenFOAM sans `executeInterval` déclaré) — `writeControl writeTime`
ne gouverne QUE les sorties annexes (`writeWakeFields`, `sampleDisk`), pas le fichier de
performance lui-même.

**→ `postProcessing/propellerInfo1/<segment>/propellerPerformance.dat`** — texte,
colonnes `Time n URef J KT 10*KQ eta0`, **une ligne par PAS DE TEMPS** (voir §2).
`<segment>` = temps de démarrage de chaque tronçon calculé (`0/`, et un sous-dossier par
reprise — `case_kOmegaSST` en a 4, `case_laminar` en a 3, `case_kEpsilon` un seul).
**Constat majeur (15/09) : ce fichier brut, sur les TROIS cas, date d'AVANT la
correction de D du 14/09** (D=0,2 m au lieu de 0,227378 m) — jamais régénéré depuis
(regénérer exigerait de relancer le solveur, hors périmètre). Vérifié par calcul direct :
J/K_T/10K_Q du brut = J/K_T/10K_Q de `data/perf_*.csv` × (0,227378/0,2)^(1, 4, 5)
respectivement, sur les trois modèles.

**→ `data/perf_<modele>.csv`** — produit par `Helice/scripts/extraire_kit_donnees.py
--csv` (fonctions `find_performance_files`/`read_rows` de `compare_turbulence.py`) :
fusionne tous les segments d'un cas (un tronçon plus tardif écrase le temps commun s'il
y a reprise), écrit les colonnes du brut TELLES QUELLES. **Ce script ne rééchelonne
RIEN.** Les `data/perf_*.csv` actuellement sur ce disque SONT au bon D (vérifié :
`average_last_revolution()` appliquée à `perf_kEpsilon.csv` reproduit EXACTEMENT
`Results/bilan_helice.txt`, à 4 décimales) — mais ce rééchelonnement a été appliqué par
un moyen qui ne survit dans AUCUN script actuel de ce dépôt. **Ne jamais relancer
`extraire_kit_donnees.py --csv` sans d'abord vérifier que le brut `postProcessing/` est
lui-même à jour — sinon il écrase le CSV correct par le brut périmé.**

**→ `Results/bilan_helice.txt`** — produit par `Helice/scripts/bilan_helice.py`
(`average_last_revolution`, moyenne sur le DERNIER TOUR COMPLET, voir §4). **Ce script
lit directement le brut `postProcessing/propellerInfo1/*/propellerPerformance.dat`, PAS
`data/perf_*.csv`.** Conséquence directe du même problème : relancé aujourd'hui sur ce
disque, `bilan_helice.py` régénérerait un `bilan_helice.txt` PÉRIMÉ (vérifié : donne
K_T=0,3625/J=1,0270 pour kEpsilon au lieu de 0,2170/0,9007). **Ne pas le relancer sans
correction préalable** (le faire lire `data/perf_*.csv` plutôt que le brut).

**→ `Results/comparaison_performance.png` et `convergence_residus.png`** — même script,
fonctions `plot_performance()`/`plot_residuals()`. `plot_performance()` exclut le tout
début du transitoire (`T_TRANSIENT_SKIP = 0,001 s`) puis trace K_T/10K_Q/η₀ vs LE TEMPS
EN SECONDES (pas en tours) pour les trois modèles superposés ; `plot_residuals()` trace
les résidus de pression (`log.pimpleFoam`, échelle log) un panneau par cas. **Même
réserve que `bilan_helice.txt` : ces deux figures, datées du 06/09, ne sont PAS
reproductibles en relançant le script tel quel aujourd'hui** — le script est trouvé,
mais il lit une source devenue périmée. Statut tranché : **script trouvé
(`bilan_helice.py`), NON reproductible en l'état, à corriger avant toute relance.**

## 2. Pourquoi 1853 lignes mais 62 répertoires

Une **ligne** de `propellerPerformance.dat` = un **PAS DE TEMPS** interne du solveur
(le functionObject s'exécute par défaut à chaque pas). Un **répertoire** `0.NNN/` =
une **ÉCRITURE** de champs complets (gouvernée par `writeInterval 0,001 s`,
`writeControl adjustable`, `system/controlDict:29-31`). Le pas de temps est ADAPTATIF
(`adjustTimeStep yes`, `maxCo 2`) : il grandit progressivement depuis ~1,2e-5 s en
début de calcul. Sur `case_kEpsilon` (un seul segment, jamais repris) : **1853 lignes**
(`Helice/data/perf_kEpsilon.csv`, moins l'en-tête) pour **62 répertoires** `0`, `0.001`,
… `0.06` (un point d'écriture toutes les ~30 pas en moyenne). **C'est ce qui perd tout
le monde** : compter les répertoires pour estimer le nombre de pas de calcul sous-estime
d'un facteur ~30.

## 3. Conversion temps → tours → angle

n = 25,146 tr/s (calculé : ω=158 rad/s / 2π, `constant/dynamicMeshDict:29` — plus
précis que le n=25,15 arrondi de `propellerInfo:34`, même rotation, deux sources
cohérentes). Période T = 1/n = **0,039767 s**. Colonnes ajoutées à `data/perf_*.csv`
(`Helice/scripts/augmenter_tours_angle.py`, SUIVI) :
```
tours     = time * n
angle_deg = (360 * time * n) mod 360
```
Fichiers d'origine (sans ces deux colonnes) conservés sous `data/perf_<modele>_
sans_tours.csv` — aucune donnée détruite, seulement réétiquetée.

**Contrôle (lignes par tour, trois modèles)** — référence indépendante :
1853 lignes / 1,509 tour (kEpsilon) = **1228 pas/tour**, soit 0,293°/pas en moyenne :

| Modèle | Lignes | Temps réellement couvert | Tours | Lignes/tour | Écart vs 1228 |
|---|---|---|---|---|---|
| kEpsilon | 1853 | 0,060000 s | 1,5088 | 1228,1 | +0,01 % |
| kOmegaSST | 1433 | 0,046161 s (0,06 s **moins le trou**, §5) | 1,1608 | 1234,5 | +0,53 % |
| laminar | 1886 | 0,060000 s | 1,5088 | 1250,0 | +1,79 % |

Les trois sont sous 5 % d'écart — **contrôle passé**. Pour kOmegaSST, le temps
« réellement couvert » exclut le trou du §5 : aucun pas n'a été calculé pendant ces
13,8 ms, les compter dans les tours sous-estimerait faussement sa densité de pas.

## 4. Le dernier tour : pourquoi on y moyenne

K_T/10K_Q/η₀ **oscillent** à la fréquence de passage de pale — une valeur instantanée
tombe sur un point arbitraire du cycle (`docs/STATUT.md`). `average_last_revolution()`
(`compare_turbulence.py`/`bilan_helice.py`) moyenne sur la fenêtre `[t_end − T ; t_end]`
= **[0,020233 ; 0,06] s** (t_end=0,06 s, T=0,039767 s ci-dessus) — le DERNIER tour
complet écoulé, jamais une moyenne sur tout le calcul (qui inclurait le transitoire de
démarrage) ni une valeur ponctuelle.

## 5. Le trou de `perf_kOmegaSST.csv`

**Écart de 0,0138388 s entre 0,00819355 s et 0,0220323 s** (`data/perf_kOmegaSST_
sans_tours.csv` — le segment `postProcessing/propellerInfo1/0/` s'arrête, `0.022/`
reprend, sans tronçon intermédiaire). Ni `case_kEpsilon` ni `case_laminar` n'ont de
trou comparable (contrôlé, §3). **Ce que ça interdit : toute analyse fréquentielle
(FFT, autocorrélation) dont la fenêtre couvrirait cette période** — un trou de données
introduit une discontinuité artificielle qui pollue tout spectre calculé dessus. Une
FFT sur kOmegaSST doit se restreindre à un segment SANS le trou (ex. la fenêtre commune
du §6, qui commence après).

## 6. La fenêtre commune

`[0,022032 ; 0,06] s` — choisie parce qu'elle **exclut le trou de kOmegaSST** tout en
restant DANS le dernier tour des trois modèles. Une amplitude crête à crête mesurée sur
des fenêtres différentes n'est PAS une grandeur comparable : plus la fenêtre est longue,
plus elle a de chances de capter un maximum ET un minimum du cycle, gonflant
artificiellement l'amplitude par rapport à une fenêtre courte. Comparer 0,0176/0,0223/
0,0242 (kEpsilon/kOmegaSST/laminar, `PARAMETRES_CAS.md`) n'a de sens QUE parce que les
trois sont mesurées sur cette même fenêtre commune — jamais sur `[0 ; t_end]` de chaque
cas séparément.
