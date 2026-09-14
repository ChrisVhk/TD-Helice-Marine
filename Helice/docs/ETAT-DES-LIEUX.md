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

- **Amplitude crête à crête de K_T, fenêtre COMMUNE aux trois modèles
  [0,022032 ; 0,06] s** (exclut le trou de données du 13/09) :
  laminaire 0,040407 > kOmegaSST 0,037294 > kEpsilon 0,029420 — ordre identique à celui
  déjà publié.
  Source : `_Methodo/JOURNAL.md`, entrée du 13/09 (LOT A, consigne « Correction-ensemble »),
  recalcul direct sur `data/perf_*.csv`.

- **η₀ = 0,5599 / 0,5901 / 0,6033** (kEpsilon / kOmegaSST / laminaire) — robuste à D et à ρ :
  invariant exact par construction (`η₀ = J·K_T/(K_Q·2π)`, les puissances de D et le
  facteur ρ s'annulent identiquement entre numérateur et dénominateur).
  Source : `Helice/Results/bilan_helice.txt` (rééchelonné le 14/09, valeurs recalculées
  identiques aux publiées à moins de 5.10⁻⁵) ; `_Methodo/JOURNAL.md`, entrée du 14/09.

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
convergence, n'a JAMAIS été mesuré.

**Trancherait** : relancer ce cas jusqu'à ~200 pas de temps supplémentaires (budget disque
et temps non arbitrés à ce jour, voir `_Methodo/DEFAUTS_ENVIRONNEMENT.md` §précondition
budget) puis répéter la mesure `pimpleFoam -postProcess -func yPlus` + pondération par
l'aire, comme fait le 14/09 sur le cas sans couches.

### Les couches de prismes améliorent-elles quoi que ce soit
**Énoncé** : non démontré — aucune comparaison chiffrée avec/sans couches n'existe sur ce
dépôt (K_T, K_Q, η₀, y+ à convergence).

**Trancherait** : même relance que l'item précédent, puis comparaison directe des K_T/K_Q/
η₀ des deux maillages (avec/sans couches) à J comparable.

### Convergence en maillage
**Énoncé** : jamais faite sur ce dépôt — aucun des chiffres absolus publiés (K_T, K_Q, η₀,
y+) ne porte de barre d'erreur liée au maillage.

**Trancherait** : au moins deux maillages supplémentaires (facteur ~0,7× et ~1,4× en
taille de cellule caractéristique), même cas, même modèle de turbulence, comparaison des
K_T/K_Q/η₀ obtenus.

### Pas de temps rendant `§4` faisable
**Énoncé** : le régime de pas de temps qui rendrait `§4` (les cinq cas prévus) faisable
dans le budget disque disponible n'a jamais été testé — seule une borne inférieure est
posée : dt ≥ 2,06.10⁻⁵ s.

**Trancherait** : lancer un cas au pas fixe candidat pendant une fraction du temps prévu et
mesurer le volume écrit réel, avant d'arbitrer `§4` en entier.

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

- **Séance 2** : l'argument amplitude contre écart tient et reste valable indépendamment
  de toutes les incertitudes ci-dessus — l'oscillation crête-à-crête de K_T (0,0294 à
  0,0404 selon le modèle, fenêtre commune) dépasse l'écart entre modèles qu'on cherche à
  classer : comparer trois fermetures dans ces conditions n'a pas de sens statistique.
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
