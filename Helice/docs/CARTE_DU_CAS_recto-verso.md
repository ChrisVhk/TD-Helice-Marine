# Carte du cas — recto-verso

**Deux pages A4 max.** Ne recopie rien de ce que `PerfNav` couvre déjà (structure d'un cas
OpenFOAM, déplacement, lancement, décomposition, ParaView, les cinq opérations, CL/maillage
— voir tableau de couverture, LOT 1 du rapport du 15/09). Ici : uniquement ce qui est
spécifique à CE cas (`Helice/case_kEpsilon`, `case_kEpsilon_layers`).

**Renvois PerfNav** : structure `0`/`constant`/`system`, lancement séq./parallèle,
`decomposePar`/`runParallel`/`reconstructPar` → `~/Work_ENSM/PerfNav/Propulseur/
Tp_propulseur_eau_libre.md` ; ParaView (ouverture, 5 opérations) →
`~/Work_ENSM/PerfNav/Docs/PostTraitement_ParaView.md`.

---

## Recto — les quatre états du cas

Référence : `case_kEpsilon` (4 rangs). Arbres RÉDUITS, méthode indiquée pour chacun.

**① Avant maillage** — *reconstruit* (`Allrun.pre`, aucun état « avant » sur ce disque) :
```
case_kEpsilon/
├── 0.orig/       (U, p, k, epsilon, nut)
├── constant/     dynamicMeshDict, transportProperties, turbulenceProperties (pas triSurface/ : copié par Allrun.pre)
└── system/       blockMeshDict, snappyHexMeshDict, decomposeParDict, ...
```

**② Après snappyHexMesh** (blockMesh→surfaceFeatureExtract→snappyHexMesh -overwrite→
renumberMesh→`rm -rf 0`→topoSet→createPatch) — *reconstruit* depuis `log.snappyHexMesh`
et suivants (disque déjà à l'état ④) :
```
case_kEpsilon/
├── 0.orig/                (inchangé)
├── constant/polyMesh/     (NOUVEAU)
├── constant/triSurface/   propeller*.obj.gz + *.eMesh
# pas de 0/ : rm -rf explicite avant restore0Dir
```

**③ Après decomposePar** (`numberOfSubdomains 4`, `hierarchical`, `n (1 4 1)` —
`decomposeParDict:14-18`) — *reconstruit* depuis `log.decomposePar` (`processor*/` détruits
par `reconstructPar`) :
```
case_kEpsilon/
├── processor0/ .. processor3/   (chacun : 0/, constant/, system/)
├── constant/, system/            (inchangés, hors processor*)
```

**④ Après calcul + reconstructPar** — *lu en direct*, état actuel du disque :
```
case_kEpsilon/
├── 0, 0.001, ... 0.06            (61 pas, writeInterval 0,001 s)
├── constant/polyMesh/, triSurface/
├── postProcessing/forces/, propellerInfo1/ (source PARAMETRES_CAS.md), yPlus/, AMIWeights1/, surfaces/, checkMesh/
├── log.blockMesh, log.snappyHexMesh, log.decomposePar, log.pimpleFoam, log.reconstructPar, ...
# pas de processor*/ : supprimés par reconstructPar
```

---

## Verso — index inverse et intouchables

### Je veux changer X → fichier + clé (valeurs : `PARAMETRES_CAS.md`)

| Changer… | Fichier · clé | Valeur |
|---|---|---|
| Rotation | `dynamicMeshDict:29 omega`, axe `:28` | 158 rad/s, (0 1 0) |
| Vitesse entrée | `0.orig/U:28 value` | 5,000 m/s |
| Durée | `system/controlDict:25 endTime` | 0,06 s |
| Fréq. écriture | `controlDict:31 writeInterval` | 0,001 s |
| Sous-domaines | `decomposeParDict:14 numberOfSubdomains`, `:18 coeffs.n` | 4, (1 4 1) |
| Turbulence | `turbulenceProperties:16 RASModel` | kEpsilon |
| Viscosité | `transportProperties:19 nu` | 1e-6 m²/s |
| Raffinement | `snappyHexMeshDict:230-238 refinementSurfaces.propellerTip.level` | (4 5) |
| Couches prismes | `case_..._layers/system/snappyHexMeshDict:359 nSurfaceLayers` (`propellerTipEdge:367`=0, voulu) | 6 visées, 3,71 obtenues |
| Diamètre réf. | `system/propellerInfo:28 radius` (D=2×radius) | 0,113689 m (D=0,227378) |

### Jamais touché

`constant/polyMesh/` (sortie maillage, on édite `snappyHexMeshDict` + relance) ·
`processor*/` (recréés/détruits par decompose/reconstruct) · `postProcessing/` (sortie,
lecture seule) · `log.*` (trace, jamais réécrit) · `0/` (écrasé par `restore0Dir` à chaque
`Allrun` — éditer `0.orig/`) · `postProcessing/propellerInfo1/*/propellerPerformance.dat`
en particulier (décision enseignant 15/09, INV-19 : c'est une mesure, radius=0,1 y
compris — la correction D vit dans `Helice/scripts/extraire_kit_donnees.py`, jamais dans
ce fichier, voir `METHODO_DONNEES.md`).

### Informatique S5 (Bloc 2 — Shell & Git), dans les deux sens

Dix commandes de l'aide-mémoire (`Informatique-Appliquee-S5/docs/03_BLOC2_Shell-Git.md`)
appliquées ici :

| Commande | Usage sur ce cas |
|---|---|
| `pwd` | quel `case_kEpsilon*` avant un `runApplication` |
| `ls -l` | `constant/polyMesh/` existe-t-il déjà ? |
| `cd X`/`cd ..` | naviguer `case_kEpsilon` ↔ `case_kEpsilon_layers` |
| `cat`/`less` | lire `system/controlDict` avant de l'éditer |
| `head`/`tail` | en-tête ou `ExecutionTime` d'un `log.*` |
| `wc -l` | compter les pas de `data/perf_kEpsilon.csv` |
| `tail -n +2 f\|wc -l` | idem sans l'en-tête CSV |
| `grep "^texte," f` | `grep ExecutionTime log.pimpleFoam.bench4` (LOT 2) |
| `sort -t, -k1,1n f` | trier `data/perf_*.csv` par temps |
| `awk -F, '$2>N' f` | filtrer les pas où K_T dépasse un seuil |

Réciproque : Bloc 2 suffit déjà pour naviguer ce cas — aucune commande nouvelle, juste un
terrain d'application réel.
