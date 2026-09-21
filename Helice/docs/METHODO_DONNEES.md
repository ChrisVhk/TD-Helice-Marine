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
reprise — `case_kOmegaSST` en a 6, `case_laminar` en a 4, `case_kEpsilon` 2).
**Attention à `J` dans ce brut : c'est `URef/(nD)`, avec `URef` relevée à 0,17 D EN AVAL des pales, dans la zone d'induction. Ce n'est pas une avance** (voir le paragraphe suivant et `data/README.md`).
**Ce brut, sur les trois cas, porte `radius 0,1` (D=0,2 m)** — la géométrie mesurée le
14/09 est D=0,227378 m. **Décision enseignant (15/09, INV-19) : le brut ne se réécrit
jamais** — c'est l'enregistrement de ce que le solveur a réellement produit. La
correction vit dans le script suivant, jamais dans le fichier lui-même. Voir §5, défaut
n°3.

**→ `data/perf_<modele>.csv`** — produit par `Helice/scripts/extraire_kit_donnees.py
--csv`. Lit le brut (fonctions `find_performance_files`/`read_rows` de
`compare_turbulence.py`, fusion des segments repris), puis **rééchelonne** K_T et 10K_Q
par un facteur `D_hist/D_correct` (puissances 4 et 5 ; η₀ ne dépend pas de D) — `D_hist` est LU dans l'en-tête `# Radius` du brut lui-même,
`D_correct` est LU dans `Helice/docs/PARAMETRES_CAS.md` : **aucun facteur codé en
dur**, si l'un des deux change un jour le calcul s'ajuste seul. Le script ajoute aussi
les colonnes `tours`/`angle_deg` (voir §3) dans la même passe, **remplace `J` par l'avance
imposée** V_inlet/(nD) = 0,8743 (V_inlet est lue dans `0.orig/U`, la même dans les trois cas), recalcule
`eta0` avec ce J, et renomme la colonne `URef` du solveur en `U_aval` (vitesse relevée en aval,
conservée comme mesure). K_T et 10K_Q ne dépendent que de n et D : ils ne changent pas. Vérifié le 15/09 :
relancer ce script reproduit `data/perf_*.csv` **octet pour octet** (les trois
fichiers) par rapport à l'état actuellement suivi.

**→ `Results/bilan_helice.txt`** — produit par `Helice/scripts/bilan_helice.py`
(`average_last_revolution`, moyenne sur le DERNIER TOUR COMPLET, voir §4). **Lit
désormais `data/perf_*.csv`, plus le brut** (corrigé le 15/09 — lire le brut aurait
reproduit exactement l'erreur qui a produit des bilans périmés). Vérifié : relancer ce
script reproduit `bilan_helice.txt` à l'identique (**à 1,5 tour, PÉRIMÉ le 20/09, voir §6** : K_T 0,2170/0,2221/0,2261, η₀
0,5599/0,5901/0,6033).

**→ `Results/comparaison_performance.png` et `convergence_residus.png`** — même script,
fonctions `plot_performance()`/`plot_residuals()`. `plot_performance()` exclut le tout
début du transitoire (`T_TRANSIENT_SKIP = 0,001 s`) puis trace K_T/10K_Q/η₀ vs LE TEMPS
EN SECONDES (pas en tours) pour les trois modèles superposés, depuis les CSV corrigés ;
`plot_residuals()` trace les résidus de pression (`log.pimpleFoam`, échelle log, non
affecté par la question de D) un panneau par cas. Régénérées et regardées le 15/09 :
K_T/10K_Q/η₀ dans leurs plages physiques réelles (K_T ~0,21-0,23), plus le trou
kOmegaSST visible en segment interpolé (défaut n°1, §5).

## 2. Pourquoi 4874 lignes mais au plus 159 écritures de champs

Une **ligne** de `propellerPerformance.dat` = un **PAS DE TEMPS** interne du solveur
(le functionObject s'exécute par défaut à chaque pas). Un **répertoire** `0.NNN/` =
une **ÉCRITURE** de champs complets (gouvernée par `writeInterval 0,001 s`,
`writeControl adjustable`, `system/controlDict:29-31`). Le pas de temps est ADAPTATIF
(`adjustTimeStep yes`, `maxCo 2`) : il grandit progressivement depuis ~1,2e-5 s en
début de calcul. Sur `case_kEpsilon` (deux segments, `0/` et `0.06/`) : **4874 lignes**
(`Helice/data/perf_kEpsilon.csv`, moins l'en-tête) pour 4,00 tours, contre **au plus 159 écritures**
de champs (`0.001`, … `0.159`, une toutes les 0,001 s ; ce qui reste sur disque dépend des purges et des
reprises) : un point d'écriture toutes les ~30 pas en moyenne. **C'est ce qui perd tout
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
facteur ~30 (4874 lignes pour au plus 159 écritures sur `case_kEpsilon`).

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
celui qui confond ligne et écriture de champs compte ~40 (159 écritures / 4,00 tours) — un
facteur ~30 d'écart, impossible à ne pas remarquer si on le cherche. C'est un contrôle
à reproduire soi-même, pas une valeur à recopier : le tableau ci-dessous existe pour
vérifier après coup, pas pour remplacer le calcul.

**Contrôle chiffré (lignes par tour, trois modèles)** — référence indépendante (mesure du 15/09 sur
1,5 tour : 1853 lignes / 1,509 tour = 1228 pas/tour ; refaite le 20/09 sur 4 tours, ci-dessous) :

| Modèle | Lignes | Temps réellement couvert | Tours | Lignes/tour | Écart vs 1228 |
|---|---|---|---|---|---|
| kEpsilon | 4874 | 0,159067 s | 4,0000 | 1218,5 | −0,78 % |
| kOmegaSST | 4453 | 0,145228 s (0,159067 s **moins le trou**, §5) | 3,6520 | 1219,3 | −0,71 % |
| laminar | 4901 | 0,159067 s | 4,0000 | 1225,2 | −0,23 % |

Les trois sont sous 5 % d'écart — **contrôle passé**. Pour kOmegaSST, le temps
« réellement couvert » exclut le trou du §5 : aucun pas n'a été calculé pendant ces
13,8 ms, les compter dans les tours sous-estimerait faussement sa densité de pas.

Cette conversion tours/angle est ce qui rend lisible la fenêtre du **dernier tour**
utilisée pour toutes les moyennes K_T/10K_Q/η₀ — voir §4 pour où elle commence
(0,119300 s à 4 tours) et pourquoi.

## 4. Le dernier tour : pourquoi on y moyenne

K_T/10K_Q/η₀ **oscillent** à la fréquence de passage de pale — une valeur instantanée
tombe sur un point arbitraire du cycle (`docs/STATUT.md`). `average_last_revolution()`
(`compare_turbulence.py`/`bilan_helice.py`) moyenne sur la fenêtre `[t_end − T ; t_end]`
= **[0,119300 ; 0,159067] s** (t_end=0,159067 s = 4,00 tours, T=0,039767 s ci-dessus) — le DERNIER
tour complet écoulé, jamais une moyenne sur tout le calcul (qui inclurait le transitoire de
démarrage) ni une valeur ponctuelle. **À 1,5 tour cette fenêtre, [0,020233 ; 0,06] s, recouvrait la mise
en régime** : les moyennes K_T étaient sous-estimées de 1,2 à 1,5 % (0,2170 au lieu de 0,2199 pour kEpsilon). À 4 tours le régime est établi (la moyenne
du 4ᵉ tour ne diffère plus de celle du 3ᵉ à plus de 0,05 %).

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
moyenne, l'historique est continu à partir de 0,022 s (à 4 tours, le trou couvre 0,35 tour, entre 0,0082 s et 0,0220 s).

**② `case_laminar` — trou dans les CHAMPS COMPLETS (répertoires de temps), pas dans
l'historique des efforts.** Les répertoires `0.048/` à `0.059/` (12, soit 0,012 s =
**0,30 tour**) n'existent pas sur disque — vérifié par listage direct le 20/09. **Les champs complets ne
vont d'ailleurs que jusqu'à 0,06 s** sur `case_kEpsilon` et `case_laminar` (les 4 tours ne sont
écrits en champs que sur `case_kOmegaSST`, jusqu'à 0,159 s) : à 1,5 tour, ce trou empiétait sur la fenêtre du
dernier tour [0,020233 ; 0,06] s ; à 4 tours il ne touche plus la fenêtre de moyenne [0,1193 ; 0,1591] s
(§4), mais **aucune image de champ n'existe sur cette fenêtre pour kEpsilon et laminar**.
**Interdit : toute analyse ou image de CHAMP (ParaView, coupe, iso-surface) du laminaire à un instant
dans 0,048–0,059 s ou au-delà de 0,06 s** — le champ n'existe pas, il ne peut pas être ouvert.
**N'interdit RIEN sur les séries scalaires** (`data/perf_laminar.csv`) : le journal `propellerInfo`
(défaut ①, absent ici) est continu sur tout `[0 ; 0,159]` — la moyenne K_T/10K_Q/η₀ du dernier tour n'est
PAS affectée, seule une exploration spatiale l'est.

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

À 4 tours, la fenêtre commune aux trois modèles est **le dernier tour complet, [0,119300 ; 0,159067] s** : les
trois séries y sont continues (le trou de kOmegaSST, §5, se situe avant 0,022 s). Une amplitude crête à crête
mesurée sur des fenêtres différentes n'est PAS une grandeur comparable : plus la fenêtre est longue, plus elle a de
chances de capter un maximum ET un minimum du cycle — et, pire, le transitoire de mise en régime. **C'est ce qui
gonflait les amplitudes du 15/09 (0,018 à 0,024, fenêtre [0,022 ; 0,06] s à 1,5 tour) d'un facteur 4 à 5 par
rapport à celles du dernier tour à 4 tours (0,0039 / 0,0048 / 0,0048).** Comparer les amplitudes de
kEpsilon/kOmegaSST/laminar (`PARAMETRES_CAS.md`) n'a de sens QUE sur cette même fenêtre — jamais sur
`[0 ; t_end]` de chaque cas séparément.

**Note du 20/09 — la phrase « relancer ce script reproduit `bilan_helice.txt` à l'identique (K_T
0,2170/0,2221/0,2261, η₀ 0,5599/0,5901/0,6033) » (§ plus haut) décrit le jeu de données à 1,5 tour.**
Depuis la régénération des CSV à 4,00 tours, le même script donne K_T 0,2198/0,2248/0,2294 et
η₀ 0,5457/0,5738/0,5873 (avec l'avance imposée J = 0,8743 ; moyenne sur les lignes du dernier tour ; 0,2199/0,2248/0,2295 en moyenne
pondérée par le temps, `Helice/scripts/comparaison_modeles.py`). Les anciennes valeurs sont conservées
dans `Helice/Results/bilan_helice_1p5tours.txt`. Le recollement des segments de reprise (fichiers
`propellerPerformance_<t>.dat` suffixés, recouvrements) est décrit dans le docstring de
`compare_turbulence.recoller`.

