# Légendes — galerie d'introduction (pvbatch)

Générées par `_Setup/outils/rendre_vues_helice.py` (ParaView 5.11.2, hors écran).
PNG non versionnés (régénérables) ; ce fichier et le script, eux, sont suivis.

**Régime des images : introduction et exemples, pas comparaison ni preuve.** Chaque
image porte sa ligne de provenance incrustée en bas : `cas · modèle · instant · état
de validation`.

**Refonte du 14/09** — sept défauts constatés en regardant les images 1, 5, 6, 7, 8 le
13/09 au soir : pas d'interpolation (rendu en blocs), barres de couleurs illisibles,
cadrage trop large (objet ~5 % de l'image), corps solide en silhouette blanche sur fond
blanc, échelle linéaire sur un champ étalé sur des décades, aucun repère d'échelle/
d'écoulement, et l'image 6 qui montrait la surface triangulée de la pale au lieu d'une
vraie coupe volumique. Corrigés ci-dessous, image par image.

---

## 01_geometrie.png

- **Introduit** : l'objet, et un premier avertissement de méthode. Vue quasi axiale
  pour compter les 4 pales (erratum Z=4, 13/09).
- **Corps solide** : Surface With Edges, contour sombre — se lit comme un objet.
- **Échelle** : barre de 50 mm + valeur en toutes lettres dans la légende de l'image.
- **D mesuré ≈ 0,227 m, pas 0,2 m documenté** (LOT 1, consigne du 14/09) — écrit
  explicitement sur l'image, non arbitré.
- **Cas / modèle / instant** : `case_kEpsilon` · k-ε · t = 0,06 s.

## 02_geometrie_domaine.png

- **Introduit** : on calcule un volume de fluide (le cylindre), pas une hélice isolée.
  `inlet` (vert) / `outlet` (orange) marqués en couleurs franches.
- **Cadrage volontairement large** : le sujet de CETTE image est le contraste
  d'échelle objet/domaine — le zoomer serait contredire son propre message. Pas de
  repère d'écoulement/échelle ajouté ici (voir réserve du rapport).

## 03_maillage_coupe.png

- **Introduit** : discrétiser a un coût, concentré près de la pale. Coupe plan
  (0,0,0)/normale z, **recadrée sur l'hélice + sillage proche** (LOT 3.3) au lieu du
  domaine entier. Corps solide (pale+moyeu) ajouté dans la même vue (LOT 3.4).
  Flèche d'écoulement + barre d'échelle (20 mm) ajoutées (LOT 3.6).

## 04_interface_AMI.png

- **Introduit** : le maillage glissant (AMI1 rouge/rotor, AMI2 bleu/stator). Écart
  radial entre les deux exagéré pour la lisibilité (rendu, pas le maillage réel).
  **Cadrage large conservé** (même arbitrage que 02) : le contexte du domaine fait
  partie du message ici aussi.

## 05_pression_pales.png

- **Introduit** : la pression diffère nettement entre les deux faces de la pale —
  origine physique de la poussée.
- **Refonte du 14/09 (LOT 3.8)** : séparation par **orientation de la normale
  (2-means)**, PAS par point de vue — la version du 13/09 (caméras antipodales)
  mélangeait les deux signes de pression dans chaque vue, vérifié à l'œil. Les deux
  groupes de mailles obtenus ont des normales moyennes **antipodales à 180,0°** (log
  affiché par le script) : séparation nette, pas une approximation.
  Étiquetage **prudent** : la face à pression moyenne la plus haute est notée
  « probable intrados », l'autre « probable extrados » — indice de cohérence physique
  (un rotor qui pousse), pas une démonstration aérodynamique rigoureuse.
- **Interpolation POINTS** (LOT 3.1), échelle divergente symétrique sur 0 (Cool to
  Warm, percentiles 2-98 sur `propellerTip`), barre dans le cadre avec unité.
- **Moyeu atténué** (opacité 0,35) : le sujet est la pale.
- Pas de flèche d'écoulement ajoutée sur cette image (écart signalé, voir rapport).

## 06_couches_prismes.png

- **Introduit** : une couche limite se maille par une pile de prismes qui
  s'épaississent contre la paroi, avant un maillage de cœur bien plus grossier.
- **Refonte complète du 14/09 (LOT 3.7)** : l'ancienne coupe (normale à l'axe Y) était
  quasi TANGENTE à la paroi cylindrique du moyeu à l'endroit zoomé — les couches n'y
  apparaissaient que de biais, sur la tranche (pas un problème de zoom, une mauvaise
  orientation de plan). Nouvelle coupe **normale Z, perpendiculaire à la paroi** :
  contient à la fois la normale locale du moyeu (+X) et l'axe (Y), donc tranche
  perpendiculairement au mur.
  **Deux panneaux** : à gauche la pale entière avec un rectangle rouge marquant la
  zone agrandie ; à droite l'agrandissement, annoté (nombre de couches, épaisseur de
  la première, « maillage de cœur »).
- **Cas / modèle** : `case_kEpsilon_layers` · maillage seul, aucun champ.

## 07_vitesse.png

- **Introduit** : le champ de vitesse (norme), lisse (interpolation POINTS),
  accélération marquée aux bouts de pale, sillage plus lent en aval du moyeu.
- **Recadré** sur l'hélice + sillage proche, corps solide visible, barre dans le
  cadre avec unité (m/s), flèche d'écoulement + échelle (20 mm).
- **Défaut résiduel mineur, signalé, non corrigé** : deux courts segments blancs
  apparaissent au-dessus et en dessous de l'hélice — artefact de bord du `Clip` de
  cadrage, cosmétique, ne gêne pas la lecture du champ.

## 08_turbulence.png

- **Introduit** : la turbulence (k) est **produite** au bout de pale, à un niveau **un
  ordre de grandeur au-dessus** du niveau ambiant. **Correction du 14/09** : dire
  qu'elle est « quasi nulle ailleurs » est faux — k ne descend jamais sous 0,033 nulle
  part dans le domaine (niveau turbulent ambiant imposé à l'entrée, physique, pas une
  absence de turbulence). L'image affiche le **HAUT de la distribution** (>percentile
  85 mesuré dans la zone recadrée), **pas un seuil physique** de présence/absence.
- **Correctif appliqué, différent de la règle initialement demandée** : la consigne
  du 14/09 demandait un seuil bas à `k_max/1e4` (suppose un plancher quasi nul loin
  de la paroi). **Vérifié faux sur ce champ** : le k minimum réel sur tout le domaine
  est 0,033, pas ~0 — `k_max/1e4` tombe sous ce plancher, ne filtre RIEN (mesuré :
  896464/896464 mailles passent), et les deux représentations (fond gris + zone
  colorée) se superposent exactement → z-fighting (motif rouge/blanc en dents de
  scie, pas un défaut de donnée). **Repli adopté** : seuil bas = percentile 85 du
  champ dans la zone recadrée, qui filtre toujours réellement quel que soit le
  plancher. Échelle **log** conservée comme demandé.
  **Règle générale, à ré-appliquer** : un champ étalé sur des décades ne se montre
  jamais en échelle linéaire (vaut pour k, epsilon, nut, Q) — mais le seuil bas doit
  être calé sur les PERCENTILES du champ, pas sur une fraction fixe du maximum, sauf
  vérification préalable que le champ approche effectivement zéro.

---

## Écarts signalés, non comblés (LOT 3)

- **02 et 04** ne satisfont pas le repère « objet ≥ 50 % de la largeur » : cadrage
  large délibéré, le message de ces deux images est justement le contraste
  d'échelle objet/domaine. Ni flèche d'écoulement ni barre d'échelle ajoutées.
- **05** n'a pas de flèche d'écoulement (seule la barre de pression y figure).
- **07/08** portent un artefact de rendu mineur (fines lignes blanches au bord du
  Clip), cosmétique.
- **Bug VTK/ParaView découvert et contourné** (voir commentaires du script,
  fonction `_restore_builtins`) : exécuter un `ProgrammableFilter` dont le script
  importe `vtk.numpy_interface.dataset_adapter` — ou même un simple import local du
  même module en dehors de tout filtre — remplace `min`/`max`/`sum`/`abs` des
  BUILTINS Python de tout le processus pvbatch, et écrase aussi nos propres noms de
  fonctions qui collisionnent avec des symboles `numpy` (notre `save` face à
  `numpy.save`). Restauration explicite après chaque usage.
