# Kit de données — TD Hélice marine

**État au 20/09 : sept séries `perf_*.csv`, une par configuration de calcul.** Les trois séries instationnaires du départ
couvrent 4,00 tours (t = 0,159067 s) ; la fenêtre du dernier tour, [0,1193 ; 0,1591] s, est celle des moyennes de
`docs/PARAMETRES_CAS.md`. Les deux premiers tours sont un transitoire de mise en régime. Les champs pour ParaView (séance 3,
plus bas) sont, eux, à t = 0,056–0,06 s.

Le calcul OpenFOAM ne tourne **pas** en séance (un cas = ~2 h sur 4 cœurs et 12–14 Go). Les
résultats sont fournis ici. Tout est régénérable depuis les cas du dépôt via
`scripts/extraire_kit_donnees.py` (`--csv` pour les trois premiers, `--csv-supplementaires` pour les quatre autres).

## Les sept séries temporelles (versionnées, ~3,5 Mo au total)

| Fichier | Calcul | Nature de `time` | Lignes |
|---|---|---|---|
| `perf_kEpsilon.csv` | k-ε standard, maillage tournant (AMI), **instationnaire** `pimpleFoam` | secondes, pas adaptatif (~3,3e-5 s) | 4874 |
| `perf_kOmegaSST.csv` | k-ω SST, même calcul | secondes, pas adaptatif | 4453 |
| `perf_laminar.csv` | laminaire (aucun modèle de turbulence), même calcul | secondes, pas adaptatif | 4901 |
| `perf_kEpsilon_layers.csv` | k-ε, maillage **avec couches de prismes** sur la pale, instationnaire | secondes, pas FIXE 1e-5 s | 15907 |
| `perf_kEpsilon_MRF.csv` | k-ε, repère tournant **MRF**, **stationnaire** `simpleFoam` | **numéro d'itération** (1 à 1500) | 1500 |
| `perf_kOmegaSST_MRF.csv` | k-ω SST, MRF stationnaire | numéro d'itération | 1500 |
| `perf_laminar_MRF.csv` | laminaire, MRF stationnaire | numéro d'itération | 1500 |

**Les trois `perf_*_MRF.csv` existent : ce sont des calculs STATIONNAIRES en repère tournant (MRF), et chacun a son homologue instationnaire (`perf_kEpsilon.csv`, `perf_kOmegaSST.csv`, `perf_laminar.csv`) : la comparaison méthode par méthode est donc possible pour les trois modèles.**

Dans les quatre calculs instationnaires, la pale tourne réellement dans le maillage ; dans les MRF, la pale est **figée** et le
repère tourne : il n'y a ni tours ni angle, les colonnes `tours` et `angle_deg` sont **vides**, et K_T, K_Q se lisent en fin de
convergence (on moyenne les dernières itérations, pas « un tour »). Ordre de grandeur des 200 dernières itérations des trois MRF : K_T 0,214 / 0,217 / 0,221 (k-ε / k-ω SST / laminaire) ; les efforts
sont figés bien avant la fin, alors que les résidus de p et de U plafonnent vers 10⁻³. Même hélice, même domaine, même maillage de base dans les
sept fichiers ; les deux instationnaires k-ε (sans et avec couches) n'ont pas le même maillage de paroi ni le même pas de temps.

> ⚠️ **`perf_kOmegaSST.csv` — ne pas s'en servir pour une analyse fréquentielle sans lire ceci.** Sa série a un trou de
> 13,8 ms (de 0,0082 à 0,0220 s, reprise après un incident disque) : trop court pour qu'une FFT résolve la fréquence de
> rotation imposée (25,15 Hz) sur une fenêtre qui le contient ; la fréquence mesurée dérive alors vers ~26,2–26,3 Hz, un
> artefact de résolution spectrale et non un signal réel. **Les moyennes $K_T$/$K_Q$/$\eta_0$ du dernier tour ne sont pas
> affectées** (le trou est avant la fenêtre).

## Les colonnes — identiques dans les sept fichiers

`time, n, U_aval, J, KT, 10KQ, eta0, tours, angle_deg`

| Colonne | Définition | Unité |
|---|---|---|
| `time` | temps de calcul (instationnaire) ou numéro d'itération (MRF) | s ; 1 |
| `n` | fréquence de rotation utilisée par le solveur pour normaliser, 25,15 (`system/propellerInfo`) | tr/s |
| `U_aval` | vitesse moyenne **relevée en aval** du disque (plan y = −0,1 m, à 0,17 D derrière le bord aval des pales) ; ex-colonne `URef` du solveur. **Négative** (axe −y). Une mesure de l'écoulement induit, **pas une avance** | m/s |
| `J` | **avance IMPOSÉE** : J = V_inlet/(n D) = 5,000/(25,15 × 0,227378) = **0,8743**, constante, identique dans tous les fichiers ; V_inlet est lue dans `0.orig/U` (patch `inlet`, `uniform (0 -5 0)`) | — |
| `KT` | coefficient de poussée K_T = T/(ρ n² D⁴) | — |
| `10KQ` | **dix fois** le coefficient de couple : 10 K_Q = 10 Q/(ρ n² D⁵). Diviser par 10 pour K_Q | — |
| `eta0` | rendement en eau libre η₀ = J · K_T / (2π · K_Q), **calculé avec le `J` ci-dessus** | — |
| `tours` | time × ω/2π (n = 25,146 tr/s, `constant/dynamicMeshDict:29`) ; vide en MRF | — |
| `angle_deg` | (360 · tours) mod 360 ; vide en MRF | ° |

**η₀ se recalcule depuis les colonnes** : `eta0 = J*KT/(2*pi*(10KQ/10))` (à 10⁻⁶ près ; c'est le test à faire avant de se fier
à la colonne). Ne divisez pas par `10KQ` tel quel : c'est 10 K_Q. Un étudiant qui recalcule η₀ avec `U_aval/(nD)` à la place de
`J` trouve un autre nombre, plus grand de 2 % : `U_aval` n'est pas une avance.

Le `J` que le solveur écrit lui-même dans `postProcessing/propellerInfo1/*/propellerPerformance.dat` vaut `URef/(n D)`, avec la
vitesse relevée en aval : ce n'est pas une avance, il est plus grand que le `J` de ces fichiers (≈ 0,89 contre 0,8743) et
surestimait η₀ de 1,9 à 2,2 %. K_T et K_Q ne dépendent que de n et D : ils sont ceux du solveur, inchangés.

> **Rééchelonnement D (15/09, décision enseignant, INV-19)** : le brut solveur des trois premiers cas
> (`postProcessing/propellerInfo1/`) porte encore `radius 0,1` (D = 0,2 m, jamais réécrit — ce
> serait réécrire une mesure) ; `K_T` et `10KQ` sont corrigés par `scripts/extraire_kit_donnees.py` (facteur calculé depuis le
> brut et `docs/PARAMETRES_CAS.md`, jamais codé en dur — voir `docs/METHODO_DONNEES.md`). Les quatre autres cas portent
> déjà le bon rayon (rapport 1).

> **Les toutes premières lignes sont un transitoire de démarrage** ($K_T$ de plusieurs centaines
> quand `U_aval` ≈ 0) : c'est normal, ça s'établit en quelques millisecondes. Fait partie de ce que
> les étudiants doivent repérer eux-mêmes.
>
> `U_aval` diffère un peu d'un cas à l'autre (en valeur absolue, dernier tour : 5,110 / 5,110 / 5,097 m/s pour
> k-ε / k-ω SST / laminaire) parce que l'induction de l'hélice en diffère ; `J`, lui, est le même partout.

Régénérer : `python3 scripts/extraire_kit_donnees.py --csv` (les trois premiers), `--csv-supplementaires` (couches et MRF).

## Séance 3 — champs pour ParaView (NON versionné, ~1 Go)

`data/paraview_kit/` : 5 pas du dernier tour sur `case_kOmegaSST` + le pas final ($t = 0{,}06$) sur
`case_kEpsilon` et `case_laminar`, avec maillage. Un fichier `<case>.foam` par cas pour l'ouverture
ParaView.

> ⚠️ **Piège de régénération (constaté le 20/09).** Les champs complets n'existent que jusqu'à t = 0,06 s
> sur `case_kEpsilon` et `case_laminar`, alors que `case_kOmegaSST` en a jusqu'à 0,159 s. Relancer
> `--champs` tel quel prendrait donc les 5 derniers pas de kOmegaSST à t ≈ 0,155–0,159 s et le pas
> t = 0,06 s des deux autres : trois cas à des instants différents, non comparables. Le kit actuellement sur
> disque (t = 0,056–0,06 s pour les trois) est cohérent ; ne le régénérer qu'après avoir aligné les instants.

À produire **avant la séance 3** (pas dans le dépôt — trop lourd, régénérable) :

```
python3 scripts/extraire_kit_donnees.py --champs
```

Distribution : archiver `data/paraview_kit/` et le diffuser hors dépôt (kDrive, clé USB, partage
réseau école).
