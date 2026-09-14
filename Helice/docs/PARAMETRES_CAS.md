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

**Valeurs explicitement PÉRIMÉES, à ne jamais recopier** (voir LOT 2 du rapport de
boucle pour le détail par document) : Z=3 (tripale) ; D=0,2 m / `radius 0.1` ; K_T=0,3625
et J=1,024 (valeurs pré-rééchelonnement du 14/09, D=0,2 m) ; y+ « 60 % » (jamais sourcé) ;
couverture des couches 4,42/6 et 82,7 % (`log.snappyHexMesh.v2`, run antérieur au retrait
des couches sur `propellerTipEdge`, ne correspond pas au maillage sur
`constant/polyMesh` aujourd'hui).
