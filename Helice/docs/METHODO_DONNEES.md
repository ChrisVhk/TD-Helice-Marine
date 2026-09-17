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
**Ce brut, sur les trois cas, porte `radius 0,1` (D=0,2 m)** — la géométrie mesurée le
14/09 est D=0,227378 m. **Décision enseignant (15/09, INV-19) : le brut ne se réécrit
jamais** — c'est l'enregistrement de ce que le solveur a réellement produit. La
correction vit dans le script suivant, jamais dans le fichier lui-même. Voir §5, défaut
n°3.

**→ `data/perf_<modele>.csv`** — produit par `Helice/scripts/extraire_kit_donnees.py
--csv`. Lit le brut (fonctions `find_performance_files`/`read_rows` de
`compare_turbulence.py`, fusion des segments repris), puis **rééchelonne** J/K_T/10K_Q
par un facteur `D_hist/D_correct` (puissances 1/4/5 ; η₀ inchangé, invariant par
construction) — `D_hist` est LU dans l'en-tête `# Radius` du brut lui-même,
`D_correct` est LU dans `Helice/docs/PARAMETRES_CAS.md` : **aucun facteur codé en
dur**, si l'un des deux change un jour le calcul s'ajuste seul. Le script ajoute aussi
les colonnes `tours`/`angle_deg` (voir §3) dans la même passe. Vérifié le 15/09 :
relancer ce script reproduit `data/perf_*.csv` **octet pour octet** (les trois
fichiers) par rapport à l'état actuellement suivi.

**→ `Results/bilan_helice.txt`** — produit par `Helice/scripts/bilan_helice.py`
(`average_last_revolution`, moyenne sur le DERNIER TOUR COMPLET, voir §4). **Lit
désormais `data/perf_*.csv`, plus le brut** (corrigé le 15/09 — lire le brut aurait
reproduit exactement l'erreur qui a produit des bilans périmés). Vérifié : relancer ce
script reproduit `bilan_helice.txt` à l'identique (K_T 0,2170/0,2221/0,2261, η₀
0,5599/0,5901/0,6033).

**→ `Results/comparaison_performance.png` et `convergence_residus.png`** — même script,
fonctions `plot_performance()`/`plot_residuals()`. `plot_performance()` exclut le tout
début du transitoire (`T_TRANSIENT_SKIP = 0,001 s`) puis trace K_T/10K_Q/η₀ vs LE TEMPS
EN SECONDES (pas en tours) pour les trois modèles superposés, depuis les CSV corrigés ;
`plot_residuals()` trace les résidus de pression (`log.pimpleFoam`, échelle log, non
affecté par la question de D) un panneau par cas. Régénérées et regardées le 15/09 :
K_T/10K_Q/η₀ dans leurs plages physiques réelles (K_T ~0,21-0,23), plus le trou
kOmegaSST visible en segment interpolé (défaut n°1, §5).

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

## 3. De la seconde au tour d'hélice — conversion temps → tours → angle

`constant/dynamicMeshDict:28` : `omega       158; // rad/s`. L'unité (rad/s) vit
**uniquement dans le commentaire** — `solidBodyMotionFunction rotatingMotion` lit
`omega` comme un scalaire nu, sans dimension attachée (contrairement à un champ
dimensionné) : **rien dans le solveur ne vérifie cette unité**. Se tromper ici (deg/s
au lieu de rad/s, par exemple) ne produirait aucune erreur OpenFOAM — juste une hélice
qui tourne à la mauvaise vitesse, à découvrir seulement en comparant le résultat aux
autres sources.

n = ω/2π = 158/(2π) = **25,146 tr/s** (plus précis que le n=25,15 arrondi de
`propellerInfo:34` — même rotation, deux sources cohérentes, l'écart n'est qu'un
arrondi d'affichage). Période T = 1/n = **0,039767 s**.

**Le piège du facteur ~30** (voir §2) : une **ligne** de `propellerPerformance.dat` est
un **pas de temps** interne du solveur ; un **répertoire** `0.NNN/` est une **écriture**
de champs complets. Les confondre — par exemple compter les répertoires (`ls` sur le
cas) pour estimer combien de pas couvrent un tour — sous-estime la densité réelle d'un
facteur ~30 (1853 lignes pour 62 répertoires sur `case_kEpsilon`).

Colonnes ajoutées par `Helice/scripts/extraire_kit_donnees.py` (même passe que le
rééchelonnement D, §1) :
```
tours     = time * n
angle_deg = (360 * time * n) mod 360
```
Le brut (jamais modifié, §1) reste la trace « sans tours » -- pas besoin d'une copie
CSV supplémentaire pour ça.

**Le contrôle, le cœur de cette conversion** : ~1228 lignes par tour, soit 0,293° par
pas en moyenne. Celui qui convertit correctement (une division par n, pas par le nombre
de répertoires) retrouve ce chiffre à quelques pourcents près sur les trois modèles ;
celui qui confond ligne et répertoire compte ~41 (62 répertoires / 1,509 tour) — un
facteur ~30 d'écart, impossible à ne pas remarquer si on le cherche. C'est un contrôle
à reproduire soi-même, pas une valeur à recopier : le tableau ci-dessous existe pour
vérifier après coup, pas pour remplacer le calcul.

**Contrôle chiffré (lignes par tour, trois modèles)** — référence indépendante :
1853 lignes / 1,509 tour (kEpsilon) = **1228 pas/tour**, soit 0,293°/pas en moyenne :

| Modèle | Lignes | Temps réellement couvert | Tours | Lignes/tour | Écart vs 1228 |
|---|---|---|---|---|---|
| kEpsilon | 1853 | 0,060000 s | 1,5088 | 1228,1 | +0,01 % |
| kOmegaSST | 1433 | 0,046161 s (0,06 s **moins le trou**, §5) | 1,1608 | 1234,5 | +0,53 % |
| laminar | 1886 | 0,060000 s | 1,5088 | 1250,0 | +1,79 % |

Les trois sont sous 5 % d'écart — **contrôle passé**. Pour kOmegaSST, le temps
« réellement couvert » exclut le trou du §5 : aucun pas n'a été calculé pendant ces
13,8 ms, les compter dans les tours sous-estimerait faussement sa densité de pas.

Cette conversion tours/angle est ce qui rend lisible la fenêtre du **dernier tour**
utilisée pour toutes les moyennes K_T/10K_Q/η₀ — voir §4 pour où elle commence
(0,020233 s) et pourquoi.

## 4. Le dernier tour : pourquoi on y moyenne

K_T/10K_Q/η₀ **oscillent** à la fréquence de passage de pale — une valeur instantanée
tombe sur un point arbitraire du cycle (`docs/STATUT.md`). `average_last_revolution()`
(`compare_turbulence.py`/`bilan_helice.py`) moyenne sur la fenêtre `[t_end − T ; t_end]`
= **[0,020233 ; 0,06] s** (t_end=0,06 s, T=0,039767 s ci-dessus) — le DERNIER tour
complet écoulé, jamais une moyenne sur tout le calcul (qui inclurait le transitoire de
démarrage) ni une valeur ponctuelle.

## 5. Les trois défauts de données, ensemble

Regroupés ici (et dans `ETAT-DES-LIEUX_Enseignant.md` §ÉTABLI) pour qu'ils se voient
côte à côte — chacun affecte une chose différente, se confondre entre eux fait dire le
mauvais interdit à la mauvaise donnée.

**① `perf_kOmegaSST.csv` — trou dans l'HISTORIQUE DES EFFORTS (le journal
`propellerInfo`).** Écart de 0,0138388 s entre 0,00819355 s et 0,0220323 s (le segment
`postProcessing/propellerInfo1/0/` s'arrête, `0.022/` reprend, sans tronçon
intermédiaire — vérifié : aucun trou comparable sur `case_kEpsilon` ni `case_laminar`).
**Interdit : toute analyse fréquentielle (FFT, autocorrélation) dont la fenêtre
couvrirait cette période** — un trou introduit une discontinuité artificielle qui
pollue tout spectre calculé dessus. Une FFT sur kOmegaSST doit se restreindre à un
segment sans le trou (ex. la fenêtre commune du §6, qui commence après). **N'affecte
PAS** la moyenne K_T/10K_Q/η₀ du dernier tour (§4) : le trou est avant la fenêtre de
moyenne, l'historique est continu à partir de 0,022 s.

**② `case_laminar` — trou dans les CHAMPS COMPLETS (répertoires de temps), pas dans
l'historique des efforts.** Les répertoires `0.048/` à `0.059/` (12, soit 0,012 s =
**0,30 tour**) n'existent pas sur disque — vérifié par listage direct, contre 62
répertoires complets pour `case_kEpsilon` et `case_kOmegaSST`. **Ce trou EMPIÈTE sur la
fenêtre du dernier tour [0,020233 ; 0,06 s]** (§4) : environ 30 % de cette fenêtre n'a
aucun champ complet sur `case_laminar`. **Interdit : toute analyse ou image de CHAMP
(ParaView, coupe, iso-surface) du laminaire à un instant dans cette plage** — le champ
n'existe pas, il ne peut pas être ouvert. **N'interdit RIEN sur les séries scalaires**
(`data/perf_laminar.csv`) : le journal `propellerInfo` (défaut ①, absent ici) est
continu sur tout `[0 ; 0,06]` — la moyenne K_T/10K_Q/η₀ du dernier tour n'est PAS
affectée, seule une exploration spatiale l'est.

**③ Le brut `propellerPerformance.dat` — antérieur à la correction de D, jamais
régénéré, et non régénérable sans perte.** Voir §1 : `radius 0,1` (D=0,2 m) au lieu de
0,227378 m, décision enseignant de ne jamais le réécrire (INV-19). Une régénération par
post-traitement (`pimpleFoam -postProcess`, testée le 15/09, LOT B0 du bloc précédent)
donne le bon D mais seulement aux ~62 répertoires ÉCRITS, contre ~1200-1900 pas
internes dans le brut vivant — **perte de résolution d'un facteur ~30**, écart mesuré
de 0,06 à 0,62 % sur la moyenne dernier tour selon le cas. **Interdit : toute
régénération du brut par post-traitement comme substitut au rééchelonnement en code**
(§1) — la correction vit dans `extraire_kit_donnees.py`, jamais dans une nouvelle
lecture du solveur.

## 6. La fenêtre commune

`[0,022032 ; 0,06] s` — choisie parce qu'elle **exclut le trou de kOmegaSST** tout en
restant DANS le dernier tour des trois modèles. Une amplitude crête à crête mesurée sur
des fenêtres différentes n'est PAS une grandeur comparable : plus la fenêtre est longue,
plus elle a de chances de capter un maximum ET un minimum du cycle, gonflant
artificiellement l'amplitude par rapport à une fenêtre courte. Comparer 0,0176/0,0223/
0,0242 (kEpsilon/kOmegaSST/laminar, `PARAMETRES_CAS.md`) n'a de sens QUE parce que les
trois sont mesurées sur cette même fenêtre commune — jamais sur `[0 ; t_end]` de chaque
cas séparément.
