# État des lieux — TD Hélice marine (version publique)

**Généré depuis la source enseignante par `_Setup/outils/extraire_etat_des_lieux_public.py`
-- ne jamais éditer ce fichier à la main.** Chaque affirmation d'`ÉTABLI` porte sa source
dans la version enseignante (non publiée ici, gitignorée) ; cette version publique reprend
`ÉTABLI` et `OÙ ON VA` intégralement, et d'`INCERTAIN` seulement l'énoncé et le test qui
trancherait -- pas le détail.

---

## ÉTABLI

- **Z = 4.** Histogramme azimutal des sommets du tiers extérieur de `propellerTip` — quatre
  amas distincts à 90° d'écart, r_max identiques à la 6ᵉ décimale sur les quatre.
  Source : `_Methodo/JOURNAL.md` (ENSM-Enseignement), entrée du 13/09 (erratum Z=4) et du
  14/09 (contre-vérification 360°) ; `Helice/docs/PLAN_SEANCE-3.md` §identité géométrique.

- **D = 0,227378 m.** Rayon max mesuré sur le patch maillé `propellerTip` : 0,113689 m ;
  sur le fichier géométrique brut (`.obj`) : 0,113720 m — écart 0,03 %, négligeable.
  Remplace 0,2 m codé en dur dans `system/propellerInfo` (corrigé le 14/09).
  Source : `Helice/docs/PLAN_SEANCE-3.md` §identité géométrique ; `_Methodo/JOURNAL.md`,
  entrées du 14/09 (mesure, puis rééchelonnement).

- **ρ (rhoInf) n'intervient pas dans K_T/K_Q.** Tracé dans le code source du
  `functionObject` : `sumForce` (numérateur de `kt`/`kq`) est déjà multiplié par
  `rho(patchi) = rhoRef_` en amont (`forces::forceEff()`), qui s'annule exactement avec le
  `rhoRef_` du dénominateur de `kt`/`kq`. Les deux valeurs contradictoires de `rhoInf`
  présentes dans ce cas (1,2 dans `propellerInfo`, 1 dans `forces`) n'ont donc aucune
  incidence sur les coefficients publiés.
  Source : lecture directe de `propellerInfo.C`/`forces.C` (bibliothèque OpenFOAM 2412,
  `forces`), tracée dans `Helice/docs/TUTORIEL_OpenFOAM-et-ParaView.md` partie 5, piège 5.

- **y+ (SANS couches de prismes), t = 0,06 s, pondéré par l'aire des faces.**
  `propellerTip` : 83,7 % dans [30 ; 300], médiane 161, min 27,9, max 1043.
  `propellerStem1` 95,0 %, `propellerStem2` 88,1 %, `propellerStem3` 95,6 % dans [30;300].
  Méthode : `pimpleFoam -postProcess -func yPlus -time 0.06` sur `case_kEpsilon`, puis
  ParaView `CellSize` (aire par face) et tri par aire cumulée.
  Source : `_Methodo/JOURNAL.md`, entrée du 14/09 (« 60 % » retiré, remplacé par cette
  mesure sourcée) ; ligne de provenance incrustée sur les images de
  `Helice/Images/galerie/`.

- **Amplitude crête à crête de K_T, dernier tour complet [0,119300 ; 0,159067] s (4,00 tours),
  fenêtre COMMUNE aux trois modèles :** kEpsilon 0,0039 < kOmegaSST 0,0048 ≈ laminaire 0,0048
  (5 chiffres : 0,00393 / 0,00478 / 0,00481 — les deux derniers ne se départagent pas).
  **Corrigé le 20/09** : ce bloc donnait « laminaire 0,0242 > kOmegaSST 0,0223 > kEpsilon 0,0176 »,
  mesuré à 1,5 tour sur [0,022 ; 0,06] s. Cette fenêtre recouvrait la mise en régime (K_T croît de
  +4 % entre les deux demi-tours de la fenêtre) : les amplitudes étaient gonflées d'un facteur 4 à 5,
  et l'ordre à trois niveaux n'est pas conservé (kOmegaSST et laminaire sont à égalité). On y croyait parce
  que la fenêtre était « commune » — elle l'était, mais commune ne veut pas dire en régime établi.
  Source : `Helice/docs/PARAMETRES_CAS.md`, `Helice/scripts/comparaison_modeles.py` (20/09).

- **η₀ = 0,5457 / 0,5738 / 0,5873** (kEpsilon / kOmegaSST / laminaire), dernier tour à 4,00 tours,
  calculé avec l'avance IMPOSÉE J = 0,8743 (à 1,5 tour : valeurs périmées, fenêtre non établie) — robuste à D et à ρ :
  invariant exact par construction (`η₀ = J·K_T/(K_Q·2π)`, les puissances de D et le
  facteur ρ s'annulent identiquement entre numérateur et dénominateur). **η₀ dépend en revanche de J** :
  le J écrit par le solveur (`URef/(nD)`, `URef` relevée à 0,17 D en aval des pales) n'est pas une avance et
  surestimait η₀ de 1,9 à 2,2 %.
  Source : `Helice/docs/PARAMETRES_CAS.md` ; `_Methodo/JOURNAL.md`, entrées du 14/09 et du 20/09.

- **La pale est un vrai volume dans le maillage, pas un baffle.** Correction du 20/09 : ce
  paragraphe affirmait le contraire (deux patches coïncidents) et s'appuyait sur deux éléments qui ne
  tiennent pas : la ligne « Converting baffles back into zoned faces » du log `snappyHexMesh` — la
  table FaceZone/nBaffles qui l'accompagne ne concerne que `innerCylinderSmall` (l'AMI), aucune
  occurrence ne concerne la pale — et l'analyse de l'écart angulaire du 15/09 (2,39°–4,09°), dont le
  script a disparu du dépôt et qui n'est pas rejouable. Mesure directe du 19/09 sur les patches de
  pale : la face de normale opposée la plus proche est à un décalage normal de 5,9 mm (0,3-0,5R) à
  2,6 mm (0,95-1,01R), soit environ 0,85 fois l'épaisseur mesurée (10,1 mm à 0,3R, 3,5 mm à 0,9R) ;
  un baffle donnerait 0. Même résultat sur cinq maillages d'essai ; en coupe, un vide d'environ 3 mm
  entre deux parois (`_Setup/outils/mesurer_vide_pale.py`). Ce qui reste incomplet : les couches de
  prismes sur `propellerTip` (3,71 sur 6, 76,8 % de l'épaisseur visée ; pile de couches sur 62,9 % de
  l'aire des flancs, 1,7 % dans la bande 0,804-0,925R). Huit variantes de maillage seul (raffinement local,
  3 couches, leur combinaison, troncature à 0,97R/0,99R, couches dégressives, et deux avec couches sur la
  bande `Edge`, 20/09) : la combinaison couvre 69 % des flancs (81 % de `propellerTip` seul contre 74 % en
  production) mais à 71 cellules à déterminant < 0,001 contre 11 et skewness 6,79 contre 4,32 ; la production
  avec 6 couches sur l'`Edge` couvre 81,6 % (bande : 77,3 %) avec 7 cellules et la même skewness ; la combinaison
  avec 3 couches sur l'`Edge` couvre 87,9 % (bande : 92,6 %) mais 43 cellules et skewness 6,79. Aucune ne réunit
  couverture ≥ 80 % sur la bande ET qualité de la production. *(Le « 93-98 % des flancs » que cette phrase
  portait était mesuré avec un proxy invalide, corrigé le 20/09.)* La bande 0,80R-0,925R reste sans couches
  dans le cas calculé, par décision du 13/09.
  Conséquence inchangée : séparer intrados et extrados PAR ORIENTATION DE LA NORMALE.
  Les tentatives de rendu « image 06 » écartées le 15/09 cherchaient un vide de la forme du profil :
  leur prémisse était juste, le vide existe (coupe de profil `rendre_couches_pale.py`).
  Source : `_Methodo/JOURNAL.md`, entrées du 19/09 et du 20/09 ; tableaux complets dans
  `Helice/docs/03_BASE_THEORIQUE.md`, section « La pale est un vrai volume dans le maillage ».

- **Trois défauts de données connus, à ne jamais confondre entre eux** (détail complet
  et sources exactes : `Helice/docs/METHODO_DONNEES.md` §5) :
  ① `perf_kOmegaSST.csv` a un trou de 13,8 ms (0,008194 à 0,022032 s) dans l'historique
  des efforts — interdit toute FFT couvrant cette fenêtre, n'affecte pas la moyenne
  dernier tour (le trou est avant elle).
  ② `case_laminar` a un trou de champs complets de 0,012 s = 0,30 tour (`0,048` à
  `0,059` s, 12 répertoires absents) qui empiète sur la fenêtre du dernier tour —
  interdit toute image/analyse de champ du laminaire dans cette plage, n'affecte pas les
  séries scalaires (le journal `propellerInfo`, lui, est continu).
  ③ Le brut `propellerPerformance.dat` des trois cas porte `radius 0,1` (D=0,2 m, décision
  enseignant du 15/09 : jamais réécrit, INV-19) — la correction D vit dans
  `Helice/scripts/extraire_kit_donnees.py`, jamais régénérée depuis le solveur (perte de
  résolution ~30× si tenté par post-traitement, mesuré le 15/09).

---

## INCERTAIN — et ce qui le trancherait

### Origine de la raie à 4×
**Énoncé** : l'origine de la raie spectrale à 4× la fréquence de rotation n'est pas
établie — passage de pale (Z=4) et symétrie d'ordre 4 du fond cartésien (interface AMI
sur un maillage de fond lui-même d'ordre 4) prédisent EXACTEMENT la même fréquence,
indiscernables par la seule analyse spectrale actuelle.

**Trancherait** : tourner le fond cartésien de 45° et relancer — si la raie à 4× persiste
identique, elle est physique (passage de pale) ; si elle se déplace ou disparaît, elle
venait de la symétrie du fond.

### y+ du maillage À COUCHES, à convergence
**Énoncé** : le y+ réel du maillage AVEC couches de prismes (`case_kEpsilon_layers`), à
convergence, n'a JAMAIS été mesuré. **Une seconde mesure existe désormais (16/09),
huit fois plus loin que la première — TOUJOURS PAS À CONVERGENCE, à étiqueter comme
telle systématiquement.**

**Trancherait** : relancer au-delà de 200 pas (plusieurs tours complets, budget disque
et temps à arbitrer, voir `_Methodo/DEFAUTS_ENVIRONNEMENT.md` §précondition budget) et
répéter la même mesure jusqu'à ce que la fraction se stabilise d'un relevé à l'autre —
ce qui n'a pas été tenté ici (hors périmètre du 16/09, borné à 200 pas).

### Les couches de prismes améliorent-elles quoi que ce soit
**Énoncé** : non démontré — aucune comparaison chiffrée avec/sans couches n'existe sur ce
dépôt (K_T, K_Q, η₀, y+ à convergence).

**Trancherait** : même relance que l'item précédent, puis comparaison directe des K_T/K_Q/
η₀ des deux maillages (avec/sans couches) à J comparable.

### Convergence en maillage
**Énoncé** : jamais faite sur ce dépôt — aucun des chiffres absolus publiés (K_T, K_Q, η₀,
y+) ne porte de barre d'erreur liée au maillage. **C'est la lacune la plus lourde du TD,
désormais CHIFFRÉE (16/09, LOT D3) sans être lancée.**

**Trancherait** : purger ou déplacer une partie du disque hôte, ou revoir la durée visée
(moins de 1,509 tour réduirait le volume proportionnellement), puis reprendre ce
dimensionnement avant toute construction réelle.

### Pas de temps rendant `§4` faisable
**Énoncé** : le régime de pas de temps qui rendrait `§4` (les cinq cas prévus) faisable
dans le budget disque disponible n'a jamais été testé — seule une borne inférieure était
posée : dt ≥ 2,06.10⁻⁵ s. **PARTIELLEMENT TRANCHÉ le 16/09 (LOT D1)** : dt=2e-5 s
mesuré stable (200 pas, `case_kEpsilon_layers`, 4 rangs) — au-dessus de la borne, mais
dt=2,5e-5 s diverge (FPE), donc la marge au-dessus de 2e-5 s reste étroite et non
cartographiée finement (rien entre 2e-5 et 2,5e-5 n'a été testé).
(Correction du 20/09 : « le pas fixe retenu (2e-5 s) » ne décrit PAS le calcul qui a été fait. Le cas complet
`case_kEpsilon_layers` (4 tours) a tourné à `deltaT 1e-5`, `adjustTimeStep no` (`system/controlDict`), soit
15 907 pas jusqu'à t = 0,15907 s (`propellerPerformance_0.dat`) ; le 2e-5 s n'a servi qu'aux essais de 200 pas du
16/09. Le pas 2e-5 « retenu » l'a été comme hypothèse de plan, jamais comme réglage du calcul de production.)

**Trancherait** : mesurer le volume RÉEL écrit par un cas complet au pas de production (1e-5 s fixe, voir la correction du 20/09 ci-dessus)
(pas seulement 200 pas exploratoires) avant d'arbitrer `§4` en entier — non fait ici,
hors périmètre du 16/09 (borné à 200 pas/essai, aucune production).

### P/D et rapport de surface (EAR)
**Énoncé** : P/D = 1,21 ± 4 % (dispersion inter-rayons mesurée, pas une incertitude
statistique) ; le rapport de surface (EAR) n'est PAS mesurable proprement avec les outils
de cette boucle — tenté par comptage de points sur grille 2D, aucun plateau de
convergence trouvé (0,77 à grille grossière jusqu'à 0,05 à grille fine, sans jamais se
stabiliser).

**Trancherait** : pour l'EAR, reprendre par union géométrique des polygones du maillage de
surface (pas un comptage de points), ou appliquer la définition normée (contour développé,
pas projeté) — ni l'une ni l'autre tentée à ce jour.

---

## OÙ ON VA

- **Séance 2** : **le sens de l'argument s'est inversé le 20/09.** À 1,5 tour l'oscillation crête à
  crête de K_T (0,018 à 0,024) dépassait l'écart entre modèles (ΔK_T ≈ 0,0096 à 4 tours) ; à 4 tours,
  dernier tour établi, l'oscillation vaut 0,0039 à 0,0048 et c'est **l'écart entre modèles qui la dépasse de
  2 à 2,5 fois**. Le message de séance devient : un écart entre modèles ne se lit qu'en régime établi et une fois
  les autres incertitudes bornées. Sur le COUPLE, le maillage de paroi (couches sur 63 % de l'aire des flancs, aucune sur la bande 0,804-0,925R) déplace 10K_Q de +4,2 % contre 3,1 %
  pour l'écart entre modèles ; sur K_T il ne se mesure pas (effet 6,6× plus petit que la borne du pas de temps).
  Résultat encore à défendre : la zone 0,80–0,925R sans couches reste ouverte
  (`_Reserve/comparaison-3-modeles/RAPPORT_comparaison_4tours_2026-09-20.md` §3.4 et §6).
  Voir le deck de la séance 2.
- **Séance 3** : Acte 1 — chaque binôme apporte un point de J (mesuré, pas nominal) →
  diagramme en eau libre collectif. Acte 2 — la courbe entrante dans un calcul
  d'auto-propulsion classique, SANS CFD (le calcul d'hélice reste en amont, jamais recalculé
  en séance 3). Piste avancée mais non engagée : construire le maillage à couches jusqu'à
  un état mesurable et y mesurer le y+ — c'est la mesure qui manque le plus (voir item
  « y+ du maillage à couches » ci-dessus).
- **Ensuite** : arbitrer le régime de pas fixe pour `§4` (voir item « pas de temps » ci-
  dessus) ; envisager une V2 du tutoriel comme test de reproductibilité — si un tiers
  suit `TUTORIEL_OpenFOAM-et-ParaView.md` sans aide, retrouve-t-il les mêmes défauts et
  les mêmes chiffres ?
