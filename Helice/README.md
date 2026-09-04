# TD Hélice marine en eau libre — 3 fermetures de turbulence

Cas de base : tutoriel officiel OpenFOAM `$FOAM_TUTORIALS/incompressible/pimpleFoam/RAS/propeller`
(hélice KP505-like en conduit, maillage `snappyHexMesh` + interface `AMI` rotor/stator, solveur
`pimpleFoam`, régime transitoire incompressible). Seule la fermeture de turbulence change d'un
cas à l'autre — même géométrie, même maillage, mêmes conditions aux limites U/p.

| Cas | `simulationType` | Modèle | Champs 0.orig |
|---|---|---|---|
| `case_kEpsilon` | RAS | k-epsilon | U, p, k, epsilon, nut |
| `case_kOmegaSST` | RAS | k-omega SST | U, p, k, omega, nut |
| `case_laminar` | laminar | — (aucun) | U, p |

`omega0` de `case_kOmegaSST` est dérivé de `epsilon0`/`k0` du cas k-epsilon via la relation
standard `epsilon = Cmu * k * omega` (Cmu = 0.09) : `omega0 = 0.0495 / (0.09 * 0.06) ≈ 9,1667 s⁻¹` —
même intensité turbulente en entrée pour les deux fermetures RAS, seule la fermeture diffère.

## Sortie exploitée : `propellerInfo`

Chaque cas embarque déjà le function object `propellerInfo` (`system/propellerInfo`) et `forces`
(`system/forces`) du tutoriel natif : ils écrivent en cours de calcul les performances hélice
(poussée, couple, coefficients KT/KQ, efficacité η0) dans `postProcessing/propellerInfo1/`.
C'est cette sortie que `scripts/compare_turbulence.py` lit pour comparer les 3 modèles — aucun
post-traitement de champ supplémentaire n'est nécessaire pour l'attendu référentiel.

## Étapes (par cas)

1. `Allrun.pre` — copie la géométrie hélice (`$FOAM_TUTORIALS/resources/geometry/propeller`),
   `blockMesh`, `surfaceFeatureExtract`, `snappyHexMesh`, `renumberMesh`, `topoSet`, `createPatch`.
2. `Allrun` — `restore0Dir` (copie `0.orig` → `0`), `decomposePar` (4 sous-domaines), `pimpleFoam`
   en parallèle, `reconstructPar`.

Utiliser `02_run.sh` à la racine de `Helice/` pour enchaîner les 3 cas, ou lancer un cas seul :

```bash
cd case_kOmegaSST && ./Allrun.pre && ./Allrun
```

## Docs

Voir [`docs/STATUT.md`](docs/STATUT.md) pour l'état de la suite pédagogique (ce qui est rédigé,
ce qui reste à faire).
