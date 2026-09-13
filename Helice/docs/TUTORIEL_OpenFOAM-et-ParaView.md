# Tutoriel — OpenFOAM et ParaView, sans rien supposer acquis

Document unique pour deux publics (INV-01 : le master est une réserve, la concision
est le travail des synthèses aval — ne pas dupliquer ce fichier par filière).
Registre : celui de `PostTraitement_ParaView.md` (PerfNav) retravaillé par
l'enseignant — chaque commande Unix et chaque clic ParaView sont explicités, rien
n'est supposé acquis.

## Deux itinéraires

**I3 / Informatique S5** (découverte de l'outil, pas le TD hélice) — 10 lignes :
1. Partie 1 (arborescence) — comprendre `0/`, `constant/`, `system/` avant d'ouvrir quoi que ce soit.
2. Partie 3 (faire tourner) — exécuter la chaîne maillage → calcul → reconstruction sur un cas fourni.
3. Partie 4 (ParaView) — les cinq opérations, dans l'ordre, sur les résultats obtenus.
4. Partie 2 : lecture seule, pour repérer où vivent les paramètres, pas pour les modifier.
5. Partie 5 et la fiche d'identité : **optionnelles**, en bonus si le temps le permet.
6. Objectif de séance : produire une image ParaView et savoir dire ce qu'elle montre.
7. Pas de calcul de coefficient propulsif attendu — ce n'est pas l'objet du module.
8. Le cas support peut être n'importe quel tutoriel OpenFOAM simple, pas forcément l'hélice.
9. Niveau : premier contact, aucune notion de mécanique des fluides supposée.
10. Support : ce document, parties 1/3/4 en priorité.

**FON-S7 / Hélice** (TD hélice marine en eau libre) — 10 lignes :
1. Séance 1 : Partie 1 en autonomie avant de lire les CSV (`data/perf_*.csv`).
2. Séance 1 : Partie 2, colonnes du tableau §2 uniquement, sans encore aller voir la géométrie.
3. Inter-séances : Partie 5 en lecture, pour armer la lecture critique des chiffres publiés.
4. Séance 3 : Partie 3 lue avant la session ParaView guidée (comprendre ce qui a déjà tourné).
5. Séance 3 : Partie 4, les cinq opérations, appliquées aux champs du cas hélice.
6. **La fiche d'identité (ci-dessous) est OBLIGATOIRE avant d'utiliser un chiffre du cas.**
7. Elle se remplit en DEUX temps : lecture des fichiers, PUIS vérification sur la géométrie.
8. C'est l'exercice qui aurait attrapé les quatre erreurs trouvées les 13-14/09 sur ce cas.
9. Niveau : notions de coefficients propulsifs déjà vues en cours (K_T, K_Q, η₀, J).
10. Support : ce document en entier, plus `ERRATUM.md` et `PLAN_SEANCE-3.md`.

---

## 1. L'arborescence — ce qui évolue, ce qui décrit, ce qui pilote

Un cas OpenFOAM est un dossier avec exactement trois sous-dossiers obligatoires, et la
règle qui les sépare est **le rythme de changement**, pas le sujet :

| Dossier | Rôle | Rythme |
|---|---|---|
| `0/` (et `0.orig/`) | Les CHAMPS au premier instant : `U`, `p`, `k`, `epsilon`, `nut` — une valeur (ou une condition aux limites) par cellule/patch. | **Évolue** à chaque pas de temps calculé — c'est le RÉSULTAT qui change. `0.orig/` est la copie de sûreté, jamais écrasée par le solveur ; `restoreDir` la recopie en `0/` avant de lancer. |
| `constant/` | La géométrie (`polyMesh/`, `triSurface/`) et les PROPRIÉTÉS physiques qui ne varient pas dans le temps : `transportProperties` (viscosité), `turbulenceProperties` (quel modèle), `dynamicMeshDict` (rotation de l'hélice). | **Décrit** l'objet et le fluide — ne change jamais pendant un calcul donné. Changer ce dossier, c'est changer de cas. |
| `system/` | Les RÉGLAGES de la simulation elle-même : `controlDict` (durée, pas de temps), `fvSchemes`/`fvSolution` (comment on résout), `decomposeParDict` (parallélisme), et les *functionObjects* (`propellerInfo`, `forces`) qui mesurent des grandeurs pendant le calcul. | **Pilote** — décide COMMENT le calcul tourne, pas ce qu'il calcule. |

Piège immédiat, déjà rencontré sur ce cas : un dossier `postProcessing/` apparaît
PENDANT le calcul (sorties des *functionObjects*) — ce n'est ni `0/`, ni `constant/`,
ni `system/`, c'est un QUATRIÈME type, un résultat dérivé, à ne jamais confondre avec
les champs de `0/`.

---

## 2. Les valeurs clés et où elles vivent

| Grandeur | Fichier · clé | Valeur sur ce cas | Ce qu'elle change dans le résultat |
|---|---|---|---|
| Vitesse de rotation ω | `constant/dynamicMeshDict`, ligne `omega` | 158 rad/s | Pilote la fréquence de rotation n = ω/2π (25,15 tr/s) — donc J, et toutes les fréquences du volet spectral (passage de pale = 4n). |
| Diamètre de référence D | `system/propellerInfo`, ligne `radius` (D = 2×radius) | `radius 0.1` → **D = 0,2 m codé en dur** — **vérifié FAUX sur la géométrie réelle (D = 0,227 m, voir Partie 5 et la fiche d'identité)** | Dénominateur de J (×D), de K_T (×D⁴), de K_Q (×D⁵) — une petite erreur sur D s'amplifie violemment (voir Partie 5, piège 4). |
| Masse volumique ρ | `system/propellerInfo` (`rhoInf 1.2`) **et** `system/forces` (`rhoInf 1`) — **deux valeurs différentes dans le même cas** | 1,2 (air) et 1 | **N'affecte PAS K_T/10K_Q/η₀** publiés (rhoRef s'annule dans leur formule, vérifié sur le code source du functionObject — voir Partie 5, piège 5) ; affecterait une poussée reconstruite en newtons si on mélangeait les deux sans y prendre garde. |
| Pas de temps | `system/controlDict`, ligne `deltaT` (+ `adjustTimeStep`, `maxCo`) | `deltaT 1e-5`, `adjustTimeStep yes`, `maxCo 2` | Pas de temps ajusté pour ne jamais dépasser un Courant de 2 — trop grand, le calcul diverge ; trop petit, le calcul coûte cher sans gagner en précision utile. |
| Nombre de Courant | `system/controlDict`, ligne `maxCo` | 2 | Condition de stabilité du schéma explicite en temps — au-delà, la solution peut diverger à chaque pas. |
| Schéma temporel | `system/fvSchemes`, bloc `ddtSchemes` | `Euler` | Ordre 1 en temps — simple et robuste, mais diffusif ; un schéma d'ordre 2 (`backward`) serait plus précis à pas égal, mais moins stable ici. |
| Nombre de sous-domaines | `system/decomposeParDict`, ligne `numberOfSubdomains` | 4 (méthode `hierarchical`) | Nombre de cœurs utilisés pour `pimpleFoam` en parallèle — change le temps de calcul, jamais le résultat physique (à convergence égale). |

---

## 3. Faire tourner — ce que chaque commande produit, et comment savoir qu'elle a réussi

Chaîne exacte de ce cas (`Allrun.pre` puis `Allrun`) :

1. **`blockMesh`** — construit le maillage de fond (grossier, cartésien).
   *Réussite* : `constant/polyMesh/` rempli (points, faces, owner, neighbour) ; le log
   se termine par `End` sans `FOAM FATAL ERROR`.
2. **`surfaceFeatureExtract`** — repère les arêtes vives de la géométrie STL/OBJ
   (`constant/triSurface/`), pour que `snappyHexMesh` les respecte en découpant.
   *Réussite* : un fichier `.eMesh` par surface apparaît dans `constant/triSurface/`.
3. **`snappyHexMesh -overwrite`** — la vraie fabrication du maillage : castellation
   (découpe grossière autour de la géométrie), snap (colle le maillage à la surface),
   couches de prismes si demandées. `-overwrite` remplace le maillage de fond par le
   résultat final, sans garder les étapes intermédiaires.
   *Réussite* : log se terminant par un résumé de qualité de maille sans `FATAL` ;
   `checkMesh` (pas lancé automatiquement ici) confirmerait `Mesh OK`.
4. **`renumberMesh -overwrite`** — renumérote les cellules pour réduire la largeur de
   bande de la matrice à résoudre (calcul plus rapide, résultat physique inchangé).
5. **`rm -rf 0`** puis **`restoreDir`** (dans `Allrun`) — `snappyHexMesh` produit un
   dossier `0/` mangé par le remaillage ; on le jette et on repart de `0.orig/`, la
   copie de sûreté jamais touchée par le solveur.
6. **`topoSet`** (`system/createInletOutletSets.topoSetDict`) — construit des
   ensembles de faces/cellules nommés, préparation à l'étape suivante.
7. **`createPatch -overwrite`** — matérialise les patches `inlet`, `outlet`, `AMI1`,
   `AMI2` à partir des ensembles ci-dessus. *Réussite* : `constant/polyMesh/boundary`
   liste ces patches avec un nombre de faces non nul.
8. **`decomposePar`** — découpe le cas en `numberOfSubdomains` dossiers
   `processorN/`, un par cœur.
9. **`pimpleFoam` en parallèle** (`mpirun -np 4 pimpleFoam -parallel`) — le calcul
   lui-même. *Réussite* : le log progresse par pas de temps croissants sans
   `FOAM FATAL ERROR`, et surtout — **un `Time = ...` qui avance n'est pas une preuve
   de résultat exploitable** (voir Partie 5) : vérifier que `postProcessing/` contient
   bien un fichier de sortie pour chaque instant écrit, pas seulement les logs.
10. **`reconstructPar`** — recolle les `processorN/` en des dossiers de temps uniques
    (`0.001/`, `0.002/`, …) au niveau du cas. *Réussite* : ces dossiers existent au
    niveau racine du cas ET les `processorN/` peuvent alors être supprimés sans perte.

**Incident réel rencontré sur ce cas (05-06/09)** : une écriture qui produit des
fichiers de 0 octet SIMULTANÉMENT sur tous les rangs parallèles est un défaut de
DISQUE (plein), jamais un OOM (l'OOM tue un rang, pas quatre à la même seconde) — ne
jamais relancer sans avoir vérifié `df -h` sur l'HÔTE, pas seulement dans la distribution.

---

## 4. ParaView — cinq opérations, ce qu'elles montrent, ce qu'elles peuvent faire croire à tort

### 4.1 Ouvrir le `.foam` et choisir les régions/champs
**Montre** : dans le panneau *Properties*, une case à cocher par patch (`Mesh Regions`)
et par champ (`Cell Arrays`) — rien n'est chargé tant que la case n'est pas cochée et
`Apply` cliqué.
**Peut faire croire à tort** : que tout est chargé par défaut (faux — un patch ou un
champ oublié est juste absent, sans message d'erreur), et que les données affichées
sont lisses. **Elles ne le sont pas** : OpenFOAM écrit en CELL DATA (une valeur par
maille), ParaView les affiche telles quelles — en blocs plats — tant qu'on n'a pas
appliqué un filtre `Cell Data to Point Data`.

### 4.2 Slice (coupe par un plan)
**Montre** : l'intersection d'un plan (origine + normale) avec le maillage ou une
surface — pratique pour voir l'intérieur d'un volume.
**Peut faire croire à tort** : qu'une coupe planaire sépare proprement deux zones
d'intérêt d'une géométrie complexe. **Constaté faux le 13/09** sur la pale de ce
cas : une pale vrillée n'a pas ses deux faces (intrados/extrados) de part et d'autre
d'un même plan — un `Slice` mélange les deux. Ce qui sépare correctement, c'est
l'ORIENTATION LOCALE DE LA NORMALE à la surface, pas une position dans l'espace.

### 4.3 Threshold (seuil)
**Montre** : uniquement les cellules dont un champ tombe dans un intervalle
`[LowerThreshold, UpperThreshold]` donné.
**Peut faire croire à tort** : qu'un seuil « raisonnable » (par exemple un dix-millième
du maximum) filtre forcément quelque chose. **Constaté faux le 14/09** sur le champ de
turbulence `k` de ce cas : `k` ne descend nulle part sous ~0,033 (niveau ambiant
physique imposé à l'entrée) — un seuil à `k_max/10000` reste sous ce plancher, et
**TOUTES les cellules passent le seuil, silencieusement, sans erreur.** Toujours
vérifier le PLANCHER réel du champ (un `min` mesuré, pas supposé) avant de choisir un
seuil relatif à son maximum.

### 4.4 Color By + Rescale to Data Range
**Montre** : le champ colorié sur l'intervalle `[min, max]` mesuré.
**Peut faire croire à tort** : que cet intervalle est la bonne échelle à utiliser.
**Constaté le 13/09** sur le champ de pression de ce cas : le min/max réel est
`[-105,3 ; 97,7]`, mais 90 % des valeurs vivent dans `[-25,6 ; 11,3]` — quelques
cellules extrêmes (souvent au bord d'un maillage ou d'un calcul pas encore stabilisé)
écrasent tout le reste en une seule teinte plate. Rescaler sur des PERCENTILES
(2-98 par exemple), pas sur le min/max brut.

### 4.5 Calculator / Programmable Filter
**Montre** : un nouveau champ dérivé, calculé à partir des champs existants — utile
pour une norme, un critère, une transformation.
**Peut faire croire à tort** : que c'est une opération isolée et sans risque pour le
reste de la session. **Bug VTK/ParaView découvert le 14/09** sur ce cas : un
`Programmable Filter` dont le script Python importe
`vtk.numpy_interface.dataset_adapter` (même indirectement) REMPLACE les fonctions
`min`, `max`, `sum`, `abs` **du langage Python lui-même**, pour le reste de la session
ParaView — sans lever la moindre erreur au moment où ça se produit. Un `min()` ou un
`max()` utilisé PLUS TARD, n'importe où dans un autre script, peut alors planter avec
un message qui n'a aucun rapport apparent (`'float' object cannot be interpreted as
an integer`). Après tout usage d'un Programmable Filter, se méfier des fonctions
Python de base dans la suite de la session.

---

## 5. Lire un résultat sans se faire avoir

Six pièges **réellement rencontrés sur ce cas les 13-14/09** — aucun n'est inventé
pour l'exercice.

1. **Une échelle de couleur calée sur le min/max brut, qu'écrasent quelques cellules
   extrêmes.** Incident : image de pression du 13/09 (voir §4.4) — rescaler sur des
   percentiles, jamais sur le min/max sans avoir regardé leur écart au reste des
   valeurs.
2. **Un champ étalé sur des décades, montré en échelle linéaire.** Incident : image
   de turbulence (k) du 13/09, qui apparaissait comme un rectangle noir avec deux
   points brillants — passer en échelle LOGARITHMIQUE dès qu'un champ a un rapport
   max/min de plus de ~2 ordres de grandeur.
3. **Des données `cell data` rendues en blocs faute d'interpolation.** Incident :
   images de vitesse et de pression du 13-14/09, rendues en damier de rectangles
   plats — toujours passer par `Cell Data to Point Data` avant de colorier un champ
   destiné à être *lu visuellement* comme continu (voir §4.1).
4. **Un adimensionnement par une longueur de référence FAUSSE.** Incident : ce cas
   précis — `D = 0,2 m` codé en dur dans `system/propellerInfo`, contre `D = 0,227 m`
   mesuré et confirmé sur la géométrie (§2, et la fiche d'identité ci-dessous). Une
   erreur de 14 % sur D, élevée à la puissance 4 (K_T) et 5 (K_Q), donne une erreur
   de **~67 % sur K_T et ~90 % sur K_Q** — une petite erreur géométrique amplifiée
   par un exposant élevé n'a plus rien de petit.
5. **Une grandeur insensible à l'erreur qu'on croit valider.** Le rendement η₀ =
   K_T·J / (K_Q·2π) **annule D et ρ dans son calcul** — il « semblait bon » pendant
   que K_T et K_Q, eux, étaient faux d'un facteur 1,67 et 1,90. **Une vérification qui
   ne peut pas échouer ne vérifie rien** : ne jamais choisir, pour contrôler un
   résultat, la seule grandeur qui ne PEUT PAS révéler l'erreur cherchée.
6. **Un bug d'environnement qui casse du code sans lever d'erreur au bon endroit.**
   Le bug `min`/`max`/`sum`/`abs` du Programmable Filter (§4.5) — un symptôme loin de
   sa cause est le signe qu'il faut chercher un effet de bord dans l'environnement,
   pas seulement une faute de logique locale.

---

## Fiche d'identité du cas — à remplir par l'étudiant

**Méthode obligatoire : D'ABORD lire les fichiers (colonne 2), PUIS vérifier CHAQUE
valeur sur la géométrie ou les données brutes (colonne 3) — jamais l'inverse.** C'est
l'exercice qui aurait attrapé les quatre erreurs trouvées sur ce cas les 13-14/09
(Z=3 au lieu de 4, D=0,2 au lieu de 0,227, deux `rhoInf` incohérents, un bug
d'environnement invisible).

| Grandeur | Où la lire (fichier · clé) | Comment la VÉRIFIER sur la géométrie/les données | Ta valeur lue | Ta valeur vérifiée | Concordance ? |
|---|---|---|---|---|---|
| Nombre de pales Z | Nom du cas, docs, ou en comptant sur une image 3D | Histogramme azimutal des sommets du bout de pale (`propellerTip.obj.gz` ou le patch calculé) — chercher la PÉRIODE angulaire du motif, pas la deviner à l'œil | | | |
| Diamètre D | `system/propellerInfo`, ligne `radius` (D = 2×radius) | Rayon max $\sqrt{x^2+z^2}$ sur TOUS les points du patch de bout de pale, sur les 360° — vérifier que les Z pales donnent le MÊME rayon max (sinon, une pale diffère des autres, c'est un défaut à part). **Piège : ne jamais utiliser la boîte englobante (bounding box) — le point de rayon max n'est pas forcément aligné avec un axe.** | | | **D = 0,227 m, ÉTABLI** (voir réserve ci-dessous) |
| Vitesse de rotation n | `system/propellerInfo` (`n`) ou `constant/dynamicMeshDict` (`omega`, avec n = ω/2π) | Les deux fichiers doivent donner la MÊME valeur (à la conversion près) — sinon, lequel pilote réellement la rotation ? | | | |
| Masse volumique ρ | `grep -rn rhoInf` sur tout le cas — **ne pas s'arrêter au premier résultat** | Identifier lequel des `functionObjects` alimente RÉELLEMENT le résultat qu'on regarde (tracer le fichier de sortie jusqu'à sa source), pas supposer qu'un seul existe | | | |
| Coefficient d'avance J | Dernière colonne utile de `postProcessing/propellerInfo1/*/propellerPerformance.dat` | Recalculer J = V_a/(nD) à la main avec le D **vérifié** (pas celui du fichier) et comparer | | | |

**Réserve sur D (établie le 14/09, boucle « Identité-galerie-tutoriel »)** : mesuré
deux fois indépendamment sur ce cas (r_max = 0,113689 m sur le patch calculé,
0,113720 m sur le fichier géométrique brut, écart 0,03 % — négligeable). Vérifié sur
un histogramme azimutal complet (360°) : **quatre amas de points distincts, à
49,5°/139,5°/229,5°/319,5°, chacun avec exactement le même r_max** — les quatre
pales sont identiques à la précision du maillage, ce n'est pas une pale isolée qui
fausserait la mesure. **D = 0,227 m est établi**, contre 0,2 m codé en dur dans
`system/propellerInfo`. **Ce qui reste ouvert** : l'arbitrage de ce qu'on fait de cet
écart dans les supports déjà publiés (K_T/K_Q n'ont pas été recalculés avec cette
valeur) — décision de l'enseignant, pas de ce tutoriel.
