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
| U_Ref (vitesse mesurée, t=0,06 s) | 5,165668 | m/s | `Helice/data/perf_kEpsilon.csv`, dernière ligne (colonne `URef`) | 15/09 |
| J imposé (=V_inlet/(nD)) | 0,8743 | — | calculé depuis les trois lignes ci-dessus (`5/(25,15×0,227378)`) | 15/09 |
| J mesuré (=U_Ref/(nD), t=0,06 s) | 0,9033 | — | `Helice/data/perf_kEpsilon.csv`, dernière ligne (colonne `J`, déjà rééchelonnée) | 15/09 |
| K_T (moyenne dernier tour, kEpsilon) | 0,2170 | — | `Helice/Results/bilan_helice.txt`, ligne `case_kEpsilon` | 15/09 |
| K_T (kOmegaSST) | 0,2221 | — | `Helice/Results/bilan_helice.txt`, ligne `case_kOmegaSST` | 15/09 |
| K_T (laminar) | 0,2261 | — | `Helice/Results/bilan_helice.txt`, ligne `case_laminar` | 15/09 |
| 10K_Q (kEpsilon) | 0,5556 | — | `Helice/Results/bilan_helice.txt`, ligne `case_kEpsilon` | 15/09 |
| 10K_Q (kOmegaSST) | 0,5401 | — | `Helice/Results/bilan_helice.txt`, ligne `case_kOmegaSST` | 15/09 |
| 10K_Q (laminar) | 0,5371 | — | `Helice/Results/bilan_helice.txt`, ligne `case_laminar` | 15/09 |
| η₀ (kEpsilon) | 0,5599 | — | `Helice/Results/bilan_helice.txt`, ligne `case_kEpsilon` | 15/09 |
| η₀ (kOmegaSST) | 0,5901 | — | `Helice/Results/bilan_helice.txt`, ligne `case_kOmegaSST` | 15/09 |
| η₀ (laminar) | 0,6033 | — | `Helice/Results/bilan_helice.txt`, ligne `case_laminar` | 15/09 |
| y+ propellerTip, min | 27,9 | — | `Helice/docs/ETAT-DES-LIEUX.md:34` (calcul pvbatch du 14/09, sans couches, t=0,06 s, pondéré par l'aire — pas de log brut ré-exploitable, résultat consigné directement) | 15/09 |
| y+ propellerTip, médiane | 161 | — | `Helice/docs/ETAT-DES-LIEUX.md:34` | 15/09 |
| y+ propellerTip, max | 1043 | — | `Helice/docs/ETAT-DES-LIEUX.md:34` | 15/09 |
| y+ propellerTip, fraction dans [30;300] | 83,7 | % | `Helice/docs/ETAT-DES-LIEUX.md:34` | 15/09 |
| Couverture des couches, propellerTip (demandé/obtenu) | 6 / 3,71 | couches | `Helice/case_kEpsilon_layers/log.snappyHexMesh.tipedge:2940` | 15/09 |
| Couverture des couches, propellerTip (%) | 76,8 | % | `Helice/case_kEpsilon_layers/log.snappyHexMesh.tipedge:2940` | 15/09 |
| nCells (maillage à couches, `case_kEpsilon_layers`) | 608463 | cellules | `Helice/case_kEpsilon_layers/constant/polyMesh/owner:13` | 15/09 |
| Amplitude crête à crête K_T, fenêtre commune [0,022032;0,06] s (kEpsilon) | 0,0176 | — | `Helice/data/perf_kEpsilon.csv`, max−min sur la fenêtre (recalculé le 15/09 sur les données rééchelonnées le 14/09 — remplace la valeur pré-rééchelonnement 0,0294 citée au 13/09) | 15/09 |
| Amplitude crête à crête K_T, même fenêtre (kOmegaSST) | 0,0223 | — | `Helice/data/perf_kOmegaSST.csv`, même méthode (remplace 0,0373) | 15/09 |
| Amplitude crête à crête K_T, même fenêtre (laminar) | 0,0242 | — | `Helice/data/perf_laminar.csv`, même méthode (remplace 0,0404) | 15/09 |
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

**LOT 2a — écart de 19 % sur le pas/tour de référence, ÉCART OUVERT** : la formule de
coût `T_total(N) = N × (4464/S) × (3+2M)` (`_Methodo/JOURNAL.md`, 13/09) utilise une
référence « 4464 s/tour » qui, divisée par le coût mesuré 3,0546 s/pas (4 rangs, sans
couches), implique **1461 pas/tour** — alors que le pas/tour calculé directement depuis
le pas naturel mesuré (3,23e-5 s) et la période de rotation vérifiée (0,03977 s, depuis
n=25,15 tr/s) donne **1231 pas/tour**, un écart de 19 %. **1231 est la valeur JUSTE** :
ses deux termes (pas naturel, période) sont chacun indépendamment sourcés dans ce
tableau. **L'origine de 1461 (et donc de « 4464 s/tour ») reste OUVERTE** : elle est
citée comme « référence du matin » dans le JOURNAL du 13/09 sans que son calcul
intermédiaire n'y soit reproduit, et aucun log de ce dépôt ne permet de la reconstruire
avec certitude — hypothèse la plus probable, non vérifiée : un pas ou une période
antérieurs, jamais recorrigés après l'établissement de n=25,15 tr/s. **Conséquence
pratique** : tout `T_total(N)` calculé avec 4464 sous-estime probablement le coût réel
par tour d'environ 19 % si le régime de pas fixe de production utilise effectivement le
pas naturel comme référence de coût par pas.

**Valeurs explicitement PÉRIMÉES, à ne jamais recopier** (voir LOT 2 du rapport de
boucle pour le détail par document) : Z=3 (tripale) ; D=0,2 m / `radius 0.1` ; K_T=0,3625
et J=1,024 (valeurs pré-rééchelonnement du 14/09, D=0,2 m) ; y+ « 60 % » (jamais sourcé) ;
couverture des couches 4,42/6 et 82,7 % (`log.snappyHexMesh.v2`, run antérieur au retrait
des couches sur `propellerTipEdge`, ne correspond pas au maillage sur
`constant/polyMesh` aujourd'hui).
