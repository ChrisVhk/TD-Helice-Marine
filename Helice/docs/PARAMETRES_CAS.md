# Paramètres du cas — source unique de vérité

**RÈGLE DE FER (consigne du 15/09) : aucune valeur n'entre dans ce tableau sans son
fichier ET sa ligne. Une valeur sans source ne s'écrit pas.** Tout autre document du
dépôt qui cite un de ces chiffres doit renvoyer ICI plutôt que le recopier — c'est la
recopie, répétée dans onze documents, qui a fait vivre des valeurs périmées (D=0,2 m,
Z=3, couverture des couches 4,42/82,7 %) longtemps après leur correction.

Cas de référence : `case_kEpsilon`, sauf mention contraire (patch/log différents pour
la géométrie et le maillage à couches, précisé colonne « Fichier · ligne »).

| Symbole | Valeur | Unité | Fichier · ligne | Vérifié le |
|---|---|---|---|---|
| Z (nombre de pales) | 4 | — | `_Methodo/JOURNAL.md` (ENSM-Enseignement), entrée du 13/09 (erratum) et du 14/09 (contre-vérification 360°) ; `Helice/docs/ETAT-DES-LIEUX.md:13-16` | 15/09 |
| D (diamètre) | 0,227378 | m | `Helice/case_kEpsilon/system/propellerInfo:28` (`radius 0.113689`, D=2×radius) | 15/09 |
| R (rayon) | 0,113689 | m | `Helice/case_kEpsilon/system/propellerInfo:28` | 15/09 |
| n (fréquence de rotation) | 25,15 | tr/s | `Helice/case_kEpsilon/system/propellerInfo:34` | 15/09 |
| ω (vitesse de rotation) | 158 | rad/s | `Helice/case_kEpsilon/constant/dynamicMeshDict:29` | 15/09 |
| ν (viscosité cinématique) | 1e-6 | m²/s | `Helice/case_kEpsilon/constant/transportProperties:19` | 15/09 |
| V_inlet (vitesse imposée) | 5,000 | m/s | `Helice/case_kEpsilon/0.orig/U:28` (`uniform (0 -5 0)`) | 15/09 |
| U_aval (vitesse moyenne RELEVÉE en aval du disque, à 0,17 D derrière les pales ; ex-`URef` du solveur ; n'est pas une avance) | 5,1102 | m/s | `Helice/data/perf_kEpsilon.csv`, colonne `U_aval` en valeur absolue, moyenne pondérée du dernier tour complet (kOmegaSST 5,1099 ; laminar 5,0966) | 20/09 |
| J imposé (=V_inlet/(nD)) | 0,8743 | — | calculé depuis les trois lignes ci-dessus (`5/(25,15×0,227378)`) | 15/09 |
| J du solveur (=U_aval/(nD) ; PAS une avance, non utilisé) | ≈ 0,89 | — | calculé : `\|U_aval\|/(nD)` ; c'est ce que `propellerPerformance.dat` écrit dans sa colonne `J`. La colonne `J` de `data/perf_*.csv` est, elle, l'avance imposée (ligne ci-dessus) | 20/09 |
| K_T (moyenne dernier tour, kEpsilon) | 0,2199 | — | `Helice/scripts/comparaison_modeles.py`, dernier tour complet [0,1193 ; 0,1591] s, moyenne pondérée par le temps, D corrigé | 20/09 |
| K_T (kOmegaSST) | 0,2248 | — | `Helice/scripts/comparaison_modeles.py`, dernier tour complet [0,1193 ; 0,1591] s, moyenne pondérée par le temps, D corrigé | 20/09 |
| K_T (laminar) | 0,2295 | — | `Helice/scripts/comparaison_modeles.py`, dernier tour complet [0,1193 ; 0,1591] s, moyenne pondérée par le temps, D corrigé | 20/09 |
| 10K_Q (kEpsilon) | 0,5606 | — | `Helice/scripts/comparaison_modeles.py`, dernier tour complet [0,1193 ; 0,1591] s, moyenne pondérée par le temps, D corrigé | 20/09 |
| 10K_Q (kOmegaSST) | 0,5452 | — | `Helice/scripts/comparaison_modeles.py`, dernier tour complet [0,1193 ; 0,1591] s, moyenne pondérée par le temps, D corrigé | 20/09 |
| 10K_Q (laminar) | 0,5437 | — | `Helice/scripts/comparaison_modeles.py`, dernier tour complet [0,1193 ; 0,1591] s, moyenne pondérée par le temps, D corrigé | 20/09 |
| η₀ (kEpsilon) | 0,5457 | — | `Helice/scripts/comparaison_modeles.py`, dernier tour complet [0,1193 ; 0,1591] s, moyenne pondérée par le temps, D corrigé, avec l'avance imposée J = 0,8743 | 20/09 |
| η₀ (kOmegaSST) | 0,5738 | — | `Helice/scripts/comparaison_modeles.py`, dernier tour complet [0,1193 ; 0,1591] s, moyenne pondérée par le temps, D corrigé, avec l'avance imposée J = 0,8743 | 20/09 |
| η₀ (laminar) | 0,5873 | — | `Helice/scripts/comparaison_modeles.py`, dernier tour complet [0,1193 ; 0,1591] s, moyenne pondérée par le temps, D corrigé, avec l'avance imposée J = 0,8743 | 20/09 |
| y+ propellerTip, min | 27,9 | — | `Helice/docs/ETAT-DES-LIEUX.md:34`. **Provenance retrouvée et REPRODUITE le 18/09** (consigne "Cloture-et-passation" LOT 1) : `case_kEpsilon` (sans couches), champ `0.06/yPlus` écrit le 14/09 par `pimpleFoam -postProcess -func yPlus -time 0.06`, encore présent sur disque -- rejoué directement (sans ParaView) par `_Setup/outils/verifier_yplus_pondere_aire.py --cas Helice/case_kEpsilon --time 0.06 --patch propellerTip`, résultat identique à 4 décimales (27,8951) | 15/09 |
| y+ propellerTip, médiane | 161 | — | idem -- reproduit à 161,11 (pondérée par l'aire) | 15/09 |
| y+ propellerTip, max | 1043 | — | idem -- reproduit à 1043,0622 | 15/09 |
| y+ propellerTip, fraction dans [30;300] | 83,7 | % | idem -- reproduit à 83,7073 % (fraction de l'AIRE ; fraction du nombre de faces, pour contexte : 76,05 %) | 15/09 |
| Couverture des couches, propellerTip (demandé/obtenu) | 6 / 3,71 | couches | `Helice/case_kEpsilon_layers/log.snappyHexMesh.tipedge:2940` | 15/09 |
| Couverture des couches, propellerTip (%) | 76,8 | % | `Helice/case_kEpsilon_layers/log.snappyHexMesh.tipedge:2940` | 15/09 |
| nCells (maillage à couches, `case_kEpsilon_layers`) | 608463 | cellules | `Helice/case_kEpsilon_layers/constant/polyMesh/owner:13` | 15/09 |
| Amplitude crête à crête K_T, dernier tour complet [0,1193;0,1591] s (kEpsilon) | 0,0039 | — | `Helice/data/perf_kEpsilon.csv`, max−min sur la fenêtre (`comparaison_modeles.py`) ; la valeur à 1,5 tour était gonflée par la mise en régime (voir l'historique en fin de fichier) | 20/09 |
| Amplitude crête à crête K_T, même fenêtre (kOmegaSST) | 0,0048 | — | `Helice/data/perf_kOmegaSST.csv`, même méthode | 20/09 |
| Amplitude crête à crête K_T, même fenêtre (laminar) | 0,0048 | — | `Helice/data/perf_laminar.csv`, même méthode (0,00393 / 0,00478 / 0,00481 à 5 chiffres : kOmegaSST et laminar ne se distinguent pas) | 20/09 |
| Pas de temps naturel (sans couches) | 3,23e-5 | s | `case_kEpsilon` (`adjustTimeStep`, pas observé en régime établi) — voir `_Methodo/JOURNAL.md`, 13/09 « Pas fixe assumé » | 15/09 |
| Période de rotation (=1/n) | 0,03977 | s | calculé depuis n=25,15 tr/s ci-dessus | 15/09 |
| Pas par tour, pas naturel (=période/pas naturel) | 1231 | pas/tour | calculé (0,03977/3,23e-5) — **JUSTE**, les deux termes sont indépendamment sourcés dans ce tableau | 15/09 |
| Pas par tour, pas fixe production (1e-5 s) | 3977 | pas/tour | calculé (0,03977/1e-5) — régime `§4` envisagé, jamais arbitré | 15/09 |
| Coût par pas, 4 rangs, sans couches (référence banc S) | 150,67 / 50 = 3,013 | s/pas | `case_kEpsilon_layers/_bench_logs/S_log.pimpleFoam.bench4` (Case=`case_kEpsilon_bench`), dernière `ExecutionTime`, 50 pas | 15/09 |
| Débit, 4 rangs, sans couches | 19,9 | pas/min | idem, 50 pas/150,67 s × 60 | 15/09 |
| Débit, 8 rangs, sans couches | 34,5 | pas/min | `.../_bench_logs/S_log.pimpleFoam.bench8`, 50 pas/87,06 s × 60 | 15/09 |
| Débit, 16 rangs, sans couches | 39,6 | pas/min | `.../_bench_logs/S_log.pimpleFoam.bench16`, 50 pas/75,69 s × 60 | 15/09 |
| S, accélération 4→16 rangs, sans couches | 1,97 | — | `_Methodo/JOURNAL.md`, 13/09 « LOT N (reprise) » : 152,73/77,35 s pour 50 pas — **rang de référence : 4→16, PAS 4→8** | 15/09 |
| Débit, 4/8/16 rangs, AVEC couches | 17,2 / 27,8 / 32,8 | pas/min | `case_kEpsilon_layers/log.pimpleFoam.bench{4,8,16}`, dernière `ExecutionTime` (174,68 / 107,87 / 91,55 s), 50 pas chacun | 15/09 |
| n, précision oméga/2π (pour tours/angle, LOT A3) | 25,146 | tr/s | calculé (`constant/dynamicMeshDict:29`, ω=158 rad/s, n=ω/2π) — plus précis que le n=25,15 arrondi ci-dessus, utilisé pour convertir temps→tours dans `data/perf_*.csv` | 15/09 |
| Lignes de données, `perf_kEpsilon.csv` (deux segments, `0/` et `0.06/`) | 4874 | lignes | `Helice/data/perf_kEpsilon.csv` (`wc -l` moins l'en-tête) | 15/09 |
| Tours couverts à t=0,159067 s (=0,159067×25,146) | 4,000 | tours | calculé depuis n=25,146 ci-dessus | 20/09 |
| Pas par tour, mesuré directement sur le CSV (=4874/4,000) | 1218 | pas/tour | calculé, `Helice/data/perf_kEpsilon.csv` — **confirme à 1 % près** la ligne « pas naturel » ci-dessous (1231 ; le pas est adaptatif, il grandit un peu) | 15/09 |
| Trou de données, `perf_kOmegaSST.csv` (segment repris) | 0,0138388 | s | `Helice/data/perf_kOmegaSST.csv`, saut entre 0,00819355 s et 0,0220323 s (`postProcessing/propellerInfo1/0/` s'arrête, `/0.022/` reprend) | 15/09 |
| R mesuré sur `propellerTip.obj.gz` (rayon max des sommets) | 0,11372 | m | `Helice/case_kEpsilon/constant/triSurface/propellerTip.obj.gz`, mesuré par `_Setup/outils/mesurer_pas_pale.py` — écart à D/2=0,113689 ci-dessus : 0,000031 m (0,027 %). **Première confirmation de D INDÉPENDANTE de `system/propellerInfo`** : cette mesure lit la géométrie triangulée brute, jamais le radius déclaré dans le dict — les deux sources concordent | 17/09 |
| P/D à r/R=0,5 (formule corrigée le 18/09, P/D=π·(r/R)·tanφ) | 1,2144 | — | `_Setup/outils/mesurer_pas_pale.py`, φ=-37,71°, dispersion 0,00° sur 4 pales (seuil 5°). **Correction du 18/09** : la valeur publiée le 17/09 (2,4287) était FAUSSE, formule erronée d'un facteur 2 (2π·(r/R)·tanφ au lieu de π·(r/R)·tanφ, confusion r/R et r/D à la dérivation) — voir JOURNAL 18/09 | 18/09 |
| P/D à r/R=0,7 (formule corrigée le 18/09) | 1,1483 | — | `_Setup/outils/mesurer_pas_pale.py`, φ=-27,57°, dispersion 0,00° sur 4 pales. Remplace la valeur erronée du 17/09 (2,2967), même correction de facteur 2 | 18/09 |
| P/D à r/R=0,9 (formule corrigée le 18/09) | 1,1156 | — | `_Setup/outils/mesurer_pas_pale.py`, φ=-21,53°, dispersion 0,00° sur 4 pales. Remplace la valeur erronée du 17/09 (2,2312), même correction de facteur 2 | 18/09 |
| Pas de l'hélice : variable ou constant (0,5R→0,9R) | VARIABLE, décroissant | — | `_Setup/outils/mesurer_pas_pale.py` — φ décroît de 37,71° à 21,53° de 0,5R à 0,9R, P/D décroît de 1,214 à 1,116 (formule corrigée) — soit -8,1 % sur cette plage | 18/09 |

**`FIG-fon-s7-reference-wageningen.png` (générée par `_Setup/outils/reference_wageningen.py`,
suivie en git) — non-usage justifié (LOT 3, consigne du 18/09 « Cloture-et-passation »)** :
compare K_T/10K_Q/η₀ de nos trois cas à la série B de Wageningen au P/D corrigé ci-dessus. La
figure porte elle-même sa conclusion en légende : « Notre pale n'est pas une série B. Cette
comparaison teste la vraisemblance, elle ne valide rien. » Le panneau η₀ affiche une divergence
numérique brutale (jusqu'à ~60) près de J≈1,28 où l'extrapolation de la série B change de signe
au dénominateur — un artefact de l'ajustement polynomial, pas une lecture pédagogique propre.
Diagnostic enseignant (a motivé le gel de la piste série B, voir JOURNAL et
`ENSM-Enseignement/_Reserve/pale-B4/`), pas une figure conçue pour un deck étudiant — non
intégrée à un support pour cette raison, pas par oubli.

**LOT A1 — chaîne solveur→figure, maillon cassé identifié (15/09)** : `system/
propellerInfo` (functionObject natif, colonnes `Time n URef J KT 10*KQ eta0`, UNE
LIGNE PAR PAS DE TEMPS — confirmé : 1853 lignes pour seulement 62 répertoires
d'écriture) écrit `postProcessing/propellerInfo1/<segment>/propellerPerformance.dat`.
**Ce fichier brut, sur les trois cas, est resté au stade PRÉ-correction de D** (D=0,2 m,
`radius 0.1` — vérifié : J/K_T/10K_Q du fichier brut valent respectivement le J/K_T/10K_Q
de `data/perf_*.csv` divisés exactement par (0,2/0,227378)¹ᐟ⁴ᐟ⁵, aux trois modèles). Le
script `Helice/scripts/extraire_kit_donnees.py --csv` (via `compare_turbulence.
find_performance_files`/`read_rows`) **copie ces colonnes SANS AUCUN rééchelonnement** —
relancé aujourd'hui tel quel, il écraserait `data/perf_*.csv` avec les valeurs PÉRIMÉES
(vérifié par exécution arithmétique directe des deux fonctions, aucun fichier modifié).
`data/perf_*.csv`, TELS QU'ILS SONT SUR CE DISQUE, portent bien le rééchelonnement
correct — mais AUCUN script actuellement dans ce dépôt ne documente ni ne reproduit ce
rééchelonnement : c'est une correction arithmétique déjà appliquée hors dépôt, jamais
capturée en code. **Même maillon cassé pour `Results/bilan_helice.txt` et les deux
.png** : `Helice/scripts/bilan_helice.py` lit directement `postProcessing/propellerInfo1/
*/propellerPerformance.dat` (le brut périmé), PAS `data/perf_*.csv` — vérifié par
exécution arithmétique de `average_last_revolution()` sur le brut (donne K_T=0,3625,
J=1,0270 pour kEpsilon, les valeurs PÉRIMÉES) contre la même fonction appliquée à
`data/perf_kEpsilon.csv` (donne K_T=0,2170, J=0,9007 à 1,5 tour — reproduisait EXACTEMENT
`Results/bilan_helice.txt` du 15/09, conservé sous `bilan_helice_1p5tours.txt`). **Conclusion : `bilan_helice.py`, SI RELANCÉ
AUJOURD'HUI, régénérerait un `bilan_helice.txt` et deux .png PÉRIMÉS** — le script est
trouvé, mais il n'est PAS reproductible en l'état contre les valeurs établies dans ce
tableau. Ne jamais le relancer sans d'abord le corriger pour lire `data/perf_*.csv` au
lieu du brut `postProcessing/`.

**LOT 2a — pas/tour du modèle de coût, 1228-1231 CONFIRMÉ par deux méthodes
indépendantes, 1461/4464 CONTREDIT PAR LES DONNÉES** : la formule de coût
`T_total(N) = N × (4464/S) × (3+2M)` (`_Methodo/JOURNAL.md`, 13/09) utilise une
référence « 4464 s/tour » qui, divisée par le coût mesuré 3,0546 s/pas (4 rangs, sans
couches), implique **1461 pas/tour**. Deux méthodes indépendantes contredisent ce
chiffre : (1) pas naturel mesuré (3,23e-5 s) ÷ période de rotation (0,03977 s, depuis
n=25,15 tr/s) = **1231 pas/tour** ; (2) lecture directe du CSV — 1853 lignes de données
pour 1,509 tour couverts à l'époque (t=0,06 s × n=25,146) = **1228 pas/tour**, une mesure PRIMAIRE,
pas un calcul dérivé. Les deux méthodes s'accordent à moins de 0,3 % l'une de l'autre et
CONTREDISENT 1461 de 19 %. **1228-1231 est désormais positivement établi, pas seulement
probable.** Le terme `3,0546 s/pas` lui-même est vérifié légitime : il mesure un coût de
calcul PAR PAS ÉLÉMENTAIRE (4 rangs, sans couches) à PAS FIXE (banc `S_4 du matin`,
152,73 s/50 pas) — une mesure de coût de calcul pur, indépendante du régime de pas
(adaptatif ou fixe) réellement utilisé en production ; ce n'est ni un coût par pas
naturel ni un coût par pas de production 1e-5 s, et rien n'indique qu'il soit lui-même
faux. **L'erreur est en aval** : `4464 = 1461 × 3,0546` utilise un pas/tour de 1461 que
plus aucune donnée primaire ne soutient. **L'origine exacte du calcul ayant produit
1461/4464 reste NON RETRACÉE** dans le JOURNAL accessible — mais son inexactitude n'est
plus une simple suspicion. **Conséquence pratique inchangée** : tout `T_total(N)` calculé
avec 4464 s'appuie sur un pas/tour non soutenu par les données ; utiliser 1228-1231.

**LOT D1 (16/09) — pas fixe retenu pour `case_kEpsilon_layers` : 2e-5 s, M et N
recalculés, 1,031/6 CADUCS.** **[CORRECTION 20/09 : le pas « retenu » ci-dessous, 2e-5 s, est celui des
essais de 200 pas du 16/09. Le calcul complet de `case_kEpsilon_layers` a tourné à `deltaT 1e-5`,
`adjustTimeStep no` (`system/controlDict`), 15 907 pas jusqu'à t = 0,15907 s (`propellerPerformance_0.dat`).
Toute lecture « couches = pas fixe 2e-5 s » est fausse pour ce calcul ; `Helice/scripts/borne_pas_de_temps.py`
chiffre l'effet de ce choix de pas.]** Trois essais bornés (200 pas, 4 rangs, maillage
`case_kEpsilon_layers` déjà construit, rampe 5 ms conservée), `controlDict` sauvegardé
et restauré (vérifié par `diff`/`md5sum` après chaque essai) :

| Essai | deltaT | Pas franchis | Courant max | Coût mesuré | Motif d'arrêt |
|---|---|---|---|---|---|
| 1 | 2e-5 s | 200/200 | 2,004 (croissance régulière, stable) | 932,48 s → **4,6624 s/pas** | Aucun — fin propre (`End`) |
| 2 | 2,5e-5 s | 55/200 | 5,04e70 (explosion géométrique) | 477,26 s avant arrêt (non exploitable) | **FPE, solveur de pression (GAMG/DIC)**, écart amorcé à t=0,0012 s (pas ~48, Courant passe de 1,09 à 2,93), emballement jusqu'à t=0,001375 s (pas 55) |
| 3 | 1,5e-5 s | — non lancé — | — | — | Essai 1 stable → branche « sinon essai 3 » non déclenchée (arbre de décision de la consigne du 16/09) |

**Pas retenu : 2e-5 s** (le plus grand des deux valeurs testées au-dessus de 1e-5 qui
tienne). Source logs : `case_kEpsilon_layers/log.pimpleFoam.essai1_2e-5` (et sa reprise
`essai1_rerun_pour_yplus`, identique, relancée pour D2), `log.pimpleFoam.essai2_2.5e-5`.

**M — PROVISOIRE, EN COURS DE VÉRIFICATION (17/09).** Le recalcul du 16/09 (ci-dessous,
barré) donnait M≈0,763 — **erreur de méthode repérée le 17/09**, pas seulement une
valeur douteuse : M<1 signifierait que les couches coûtent MOINS que leur absence, alors
que le coût PAR PAS augmente (4,66 contre 3,05 s/pas, mesuré) et qu'à 2e-5 s il faut
1988 pas/tour contre 1231 au pas naturel. La cause : le calcul comparait couches-à-2e-5s
contre sans-couches-à-1e-5s — **deux pas de temps différents sur les deux côtés**, alors
que `§4` impose LE MÊME RÉGIME TEMPOREL aux cinq cas. Trois bases de comparaison
donnent trois résultats très différents, et aucune n'est validée à ce jour :
```
(a) couches à 2e-5s / sans-couches à 1e-5s (calcul du 16/09, ERRONÉ, bases différentes)
    = 9269 / 12147 = 0,763
(b) couches à 2e-5s / sans-couches à SA PROPRE dt naturelle (3,23e-5s), coût/pas non
    réajusté au changement de dt (méthode Cowork, 17/09)
    = 9269 / (1231 × 3,0546) = 9269 / 3760 = 2,46 ≈ 2,5
(c) couches à 2e-5s / sans-couches à 2e-5s EXTRAPOLÉ (même facteur d'augmentation du
    coût/pas avec dt que celui mesuré sur les couches, ×1,48 — JAMAIS MESURÉ sur le cas
    sans couches, une hypothèse, pas une donnée)
    = 9269 / (1988,35 × 3,0546 × 1,48) = 9269 / 8991 ≈ 1,03
```
**Aucune des trois n'est tranchée.** (a) est écarté (bases non comparables). (b) et (c)
restent tous deux plausibles selon ce que `§4` décide RÉELLEMENT pour le régime des trois
cas sans couches — et c'est un ARBITRAGE ENSEIGNANT, pas un calcul : si les cas sans
couches tournent à leur pas naturel (aucune contrainte de stabilité ne les y oblige),
(b) s'applique ; si `§4` les force au même pas fixe que les couches pour rester
strictement comparable, (c) s'applique. **Tant que cet arbitrage n'est pas rendu, M
reste PROVISOIRE — ne pas le publier comme un fait établi, dans aucun document.**

**N — PLAFONNÉ À 6, par construction, pas par calcul.** `N∈[4;6]` est une borne EXTERNE
imposée par la consigne du 13/09 (nombre de configurations retenu pour l'étude, jamais
une sortie du modèle de coût) : *« le plus grand N∈[4;6] sous le budget »*
(`_Methodo/JOURNAL.md`, 13/09). Le calcul du 16/09 avait donné N=7 en ignorant cette
borne — **erreur, corrigée le 17/09** : quel que soit M, N ne peut jamais dépasser 6.
Reste à vérifier, une fois M tranché, si N=6 tient réellement sous 20h (avec M≈2,5, même
N=6 dépasserait 20h — `6×(4464/1,97)×(3+2×2,5)=108792 s=30,2 h` — et le N affordable
serait alors plus proche de 4). **Conclusion honnête : N=6 est le PLAFOND, pas
nécessairement la valeur atteignable — dépend de M, provisoire.**

**Valeurs explicitement PÉRIMÉES, à ne jamais recopier** (voir LOT 2 du rapport de
boucle pour le détail par document) : Z=3 (tripale) ; D=0,2 m / `radius 0.1` ; K_T=0,3625
et J=1,024 (valeurs pré-rééchelonnement du 14/09, D=0,2 m) ; y+ « 60 % » (jamais sourcé) ;
couverture des couches 4,42/6 et 82,7 % (`log.snappyHexMesh.v2`, run antérieur au retrait
des couches sur `propellerTipEdge`, ne correspond pas au maillage sur
`constant/polyMesh` aujourd'hui) ; **M=1,031 et N=6 (établis le 13/09 au pas fixe
1e-5 s) NE SONT PLUS LA RÉFÉRENCE depuis le 16/09, mais leur remplaçant n'est PAS
établi — M reste PROVISOIRE (0,763/2,5/1,03 selon la base de comparaison, aucune
tranchée) et N reste PLAFONNÉ À 6 par construction, jamais 7 (voir LOT D1/17-09
ci-dessus).**

## Historique — valeurs à 1,5 tour (jusqu'au 19/09), remplacées le 20/09 par celles à 4,00 tours ci-dessus

Les trois cas atteignent t = 0,159067 s (4,00 tours) depuis le 20/09 (`case_kOmegaSST` repris de 0,143 à
0,159068 ; CSV régénérés, `Helice/scripts/extraire_kit_donnees.py`). Les valeurs du tableau principal sont les
moyennes du **dernier tour complet** [0,1193 ; 0,1591] s (`Helice/scripts/comparaison_modeles.py`). La dérive
d'un tour au suivant est ≤ 0,02 % sur K_T et K_Q, ≤ 0,05 % sur η₀. **Les valeurs à 1,5 tour, ci-dessous, étaient
sous-estimées de 1,2 à 1,5 % (K_T) par la mise en régime** (leur fenêtre recouvrait le transitoire) et leurs amplitudes
gonflées d'un facteur 4 à 5 ; elles sont tracées dans `Helice/Results/bilan_helice_1p5tours.txt` (local).

| Grandeur (fenêtre à 1,5 tour, PÉRIMÉES) | kEpsilon | kOmegaSST | laminar |
|---|---|---|---|
| K_T | 0,2170 | 0,2221 | 0,2261 |
| 10 K_Q | 0,5556 | 0,5401 | 0,5371 |
| η₀ | 0,5599 | 0,5901 | 0,6033 |
| Amplitude crête à crête de K_T, fenêtre commune [0,022032 ; 0,06] s | 0,0176 | 0,0223 | 0,0242 |
| J (dernière ligne, t = 0,06 s) | 0,9033 | — | — |
