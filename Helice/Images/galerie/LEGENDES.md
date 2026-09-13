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
  **commune** aux deux (une seule barre affichée, partagée par construction — même
  LUT ParaView pour les deux représentations).
- **Méthode intrados/extrados** : **pas de coupe planaire** (la géométrie est vrillée,
  une coupe avait déjà échoué le 13/09) — deux points de vue caméra antipodaux
  (symétriques par rapport au centre de l'hélice), qui montrent naturellement les
  deux faces via l'orientation, sans toucher à la géométrie. Approximation
  d'introduction : l'antipodie montre une paire de pales opposées (symétrie
  d'ordre 4), pas rigoureusement les deux faces d'UNE seule pale.
- **Cas / modèle / instant** : `case_kEpsilon` · k-ε · t = 0,06 s.
- **Réserve de validation** : calcul de démonstration, non validé (Porte B non franchie).
  Le champ de pression affiché n'a subi aucune vérification (Porte B non franchie) —
  la plage de couleur elle-même peut être dominée par des valeurs extrêmes locales
  sans que cela ait été qualifié.

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
