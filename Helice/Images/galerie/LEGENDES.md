# Légendes — galerie d'introduction (pvbatch)

Générées par `_Setup/outils/rendre_vues_helice.py` (ParaView 5.11.2, hors écran).
PNG non versionnés (régénérables) ; ce fichier et le script, eux, sont suivis.

**Régime des images : introduction et exemples, pas comparaison ni preuve** (décision
enseignant, 13/09). Chaque image porte sa ligne de provenance incrustée en bas :
`cas · modèle · instant · état de validation`.

---

## 01_geometrie.png

- **Introduit** : l'objet. Vue quasi axiale choisie spécifiquement pour permettre de
  compter les pales — pièce justificative de l'erratum Z=4 (audit Cowork du 13/09).
- **Cas / modèle / instant** : `case_kEpsilon` · k-ε · t = 0,06 s.
- **Réserve de validation** : calcul de démonstration, non validé (Porte B non franchie).
- **Pales comptées à l'écran (LOT C)** : 4.

## 02_geometrie_domaine.png

- **Introduit** : on ne calcule pas « une hélice » mais un volume de fluide autour —
  `outerCylinder` en transparence, `inlet` (vert) et `outlet` (orange) marqués en
  couleurs franches pour rester visibles malgré la transparence de la paroi latérale.
- **Cas / modèle / instant** : `case_kEpsilon` · k-ε · t = 0,06 s.
- **Réserve de validation** : calcul de démonstration, non validé (Porte B non franchie).

## 03_maillage_coupe.png

- **Introduit** : discrétiser, et pourquoi c'est cher — coupe du maillage volumique
  par le plan (0,0,0)/normale z, cadrage large pour que le contraste entre la zone
  raffinée près de la pale et le maillage grossier au loin soit net.
- **Cas / modèle / instant** : `case_kEpsilon` · k-ε · t = 0,06 s.
- **Réserve de validation** : calcul de démonstration, non validé (Porte B non franchie).

## 04_interface_AMI.png

- **Introduit** : le maillage glissant — AMI1 (rouge, rotor) et AMI2 (bleu, stator)
  sont deux surfaces cylindriques quasi coïncidentes dans le calcul réel (rayons
  0,11985 vs 0,11999 m) ; **l'écart radial entre les deux est exagéré dans cette image
  (AMI1 réduite de 15 % en X/Z) uniquement pour la lisibilité** — sans quoi les deux
  patches se recouvrent et produisent du z-fighting à l'écran. Aucun maillage ni
  calcul n'est modifié par cet artifice de rendu. Hélice visible en gris par
  transparence à l'intérieur.
- **Cas / modèle / instant** : `case_kEpsilon` · k-ε · t = 0,06 s.
- **Réserve de validation** : calcul de démonstration, non validé (Porte B non franchie).

## 05_pression_pales.png

- **Introduit** : la poussée vient d'abord de la distribution de pression sur les
  pales (bonne réponse, Q8 du QCM). Deux vues côte à côte, échelle de couleurs `p`
  **commune** aux deux (une seule barre affichée, hors de la géométrie, avec
  unité et graduations chiffrées).
- **LOT D du 13/09 — 5 correctifs appliqués** :
  1. Échelle bornée aux **percentiles 2-98** de `p` sur `propellerTip` (pas min/max brut).
  2. Palette **divergente ET symétrique autour de zéro** (Cool to Warm ; L =
     max(|p2|,|p98|), rescale [-L,+L]) — rouge = surpression, bleu = dépression,
     signe lisible d'un coup d'œil. Le passage précédent à Viridis (12/09) réglait
     le mauvais problème : un divergent ne blanchit pas « la médiane », il
     blanchit SON POINT CENTRAL — le défaut était que ce centre restait au milieu
     de la plage brute au lieu d'être forcé à zéro.
  3. Barre de couleurs **hors de la géométrie**, titrée avec l'unité (`p [m²/s²],
     pression cinématique`) et le mode d'écrêtage, graduée en valeurs numériques.
  4. `propellerStem1/2/3` (arbre/moyeu) **atténué** (gris uni, opacité 0,35) : le
     sujet de l'image est la pale, pas l'arbre.
  5. Vue **axiale de chaque face** (même famille de caméra que `01_geometrie.png`,
     miroir en Y), **pas un angle 3/4** — remplace l'ancienne méthode par caméras
     antipodales à 3/4.
- **Constat honnête (LOT D, question posée par la consigne)** : on voit une
  variation de pression réelle sur la surface des pales, mais **concentrée aux
  bords/bouts de pale** — la majeure partie de chaque face reste proche de 0
  (teinte pâle), avec des liserés rouges ET bleus mélangés sur les MÊMES bords
  d'une même vue (cohérent avec bord d'attaque en surpression / bord de fuite en
  dépression sur une même face). **Les deux vues axiales ne se distinguent PAS
  proprement par un signe dominant unique** (l'une n'est pas franchement rouge,
  l'autre franchement bleue) : la pale est vrillée, une vue purement axiale
  traverse donc, selon le rayon, des zones de torsion différente — la même
  limite de principe qui interdisait déjà une coupe planaire. **Signalé tel
  quel, pas maquillé** : cette image montre honnêtement qu'une pression varie
  sur la pale et où (les bords), pas une séparation propre intrados/extrados.
- **Cas / modèle / instant** : `case_kEpsilon` · k-ε · t = 0,06 s.
- **Réserve de validation** : calcul de démonstration, non validé (Porte B non franchie).
  Le champ de pression affiché n'a subi aucune vérification physique — seule sa
  représentation graphique a été rendue lisible ici, pas sa validité.

## 07_vitesse.png

- **Introduit** : le champ de vitesse (norme `|U|`), coupe par le plan
  (0,0,0)/normale z (même coupe que `03_maillage_coupe.png`), palette séquentielle
  (Viridis), échelle bornée aux percentiles 2-98 (même raison qu'en 05). On y lit
  une accélération marquée de part et d'autre du bout de pale (jaune) et une zone
  de sillage plus lente juste en aval du moyeu — cohérent avec un disque tournant,
  sans qu'aucune validation n'ait été faite sur ce champ.
- **Cas / modèle / instant** : `case_kEpsilon` · k-ε · t = 0,06 s.
- **Réserve de validation** : calcul de démonstration, non validé (Porte B non franchie).
  L'aspect « mosaïque » visible loin de l'hélice reflète la taille réelle des
  cellules du maillage grossier à cet endroit (voir image 3) — ce n'est pas un
  artefact de rendu.

## 08_turbulence.png

- **Introduit** : l'énergie cinétique turbulente `k`, même coupe et même échelle
  robuste que 07 (percentiles 2-98, Inferno). La turbulence apparaît concentrée
  quasi exclusivement dans une fine bande au niveau du bout de pale — le reste du
  domaine est proche de zéro sur cette coupe à cet instant. Utile pour montrer que
  la turbulence est PRODUITE localement (bout de pale, couche de cisaillement), pas
  répartie partout dans l'écoulement.
- **Cas / modèle / instant** : `case_kEpsilon` · k-ε · t = 0,06 s.
- **Réserve de validation** : calcul de démonstration, non validé (Porte B non franchie).

## 06_couches_prismes.png (bonus)

- **Introduit** : la couche limite et le y⁺ — zoom sur la pile de couches de prismes
  (6 couches, patch `propeller.*`), maillage seul (ce cas n'a aucun champ calculé).
  Zoom calculé depuis l'épaisseur réelle de la pile lue dans le
  `snappyHexMeshDict` du cas (`firstLayerThickness` 0,00018 m, `expansionRatio` 1,2,
  6 couches → pile ≈ 1,79 mm), pas une valeur devinée.
  **Zoomé sur le CORPS de la pale** (`propellerStem2`, mi-envergure), délibérément
  PAS sur le bout de pale : ce cas retire les couches à `propellerTipEdge`
  (`nSurfaceLayers 0`, décision enseignant du 13/09, LOT N) — zoomer sur le bout
  aurait montré 0 couche et donné une image trompeuse.
- **Cas / modèle / instant** : `case_kEpsilon_layers` · k-ε (maillage à couches) · t = 0 s.
- **Réserve de validation** : maillage seul, aucun champ associé ; ce maillage n'a
  jamais tourné 200 pas stables au-delà du test du 13/09 à pas fixe (voir
  `_Methodo/JOURNAL.md`, entrée « Pas fixe assumé ») — la validité du maillage en
  tant que TEL n'est pas en cause ici (checkMesh non audité dans cette boucle),
  seule la stabilité du calcul qui s'appuie dessus reste ouverte.
