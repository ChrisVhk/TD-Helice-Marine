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
  explicitement sur l'image. **Arbitrage rendu le 14/09** (boucle suivante) :
  D = 0,227378 m remplace 0,2 m dans `system/propellerInfo`, J/K_T/10K_Q rééchelonnés
  sur les données existantes.
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
- **Troisième tentative (15/09, LOT 5)** : les deux versions précédentes ne réglaient
  pas le vrai problème — une rupture d'échelle (l'empilement fait ≈1,8 mm pour un
  diamètre de 227 mm, moins de 1 %), pas un mauvais plan de coupe. Ajouté : le
  **facteur de grossissement écrit en toutes lettres** (« grossissement panneau de
  droite : ×N », calculé depuis les distances de caméra réelles, pas une estimation)
  et un **trait de rappel** entre le rectangle et le panneau agrandi (projection
  perspective approximative, post-traitement PIL sur le PNG composé — vérifiée à
  l'œil, pas garantie au pixel).
- **Quatrième tentative (15/09, retour enseignant « cette image ne me parle pas du
  tout »)** : le grossissement seul ne suffisait pas — cadré large (×6,5 l'épaisseur
  totale), la pile de 6 couches restait une mince bande écrasée par UNE cellule de
  cœur bien plus grosse qui dominait tout le panneau, les couches elles-mêmes
  jamais lisibles comme un empilement. Corrigé par deux changements ensemble :
  cadrage resserré sur la pile (peu de cœur visible), et **chaque couche colorée
  séparément** (alternance marine/teal, cœur en gris) au lieu d'un maillage gris
  uniforme — c'est la couleur qui rend l'empilement lisible, pas le zoom seul.
  Coloriage par scalaire (distance à la paroi, bandes à transition rapide) plutôt
  que par découpe géométrique bande par bande : un premier essai de découpe
  donnait des couches en « lentilles » pointues ou une fenêtre vide, sensible à la
  moindre ondulation locale de la paroi triangulée — le coloriage par scalaire
  garde la forme réelle de chaque cellule, robuste à cette ondulation.
- **Cas / modèle** : `case_kEpsilon_layers` · maillage seul, aucun champ.

## 06b_couches_epaisseurs.png

- **Introduit (15/09, LOT 5, variante quantitative de l'image 06)** : une image ne
  peut pas montrer à la fois la pale et l'épaisseur des couches (rupture d'échelle,
  voir ci-dessus) — ce graphe ne montre plus la géométrie du tout : épaisseur de
  chaque couche en fonction de son rang (progression géométrique DEMANDÉE à
  `snappyHexMesh`, 6 points, `firstLayerThickness × expansionRatio^rang`), plus la
  courbe cumulée et l'épaisseur totale visée.
- **Ce que l'image ne dit pas et que le graphe dit** : la couverture RÉELLEMENT
  obtenue (3,71/6 couches, 76,8 % sur `propellerTip`) est différente de la
  progression demandée tracée ici — annotée en légende, sourcée
  `Helice/docs/PARAMETRES_CAS.md`, jamais recalculée dans ce script.
- **Généré par** : `_Setup/outils/generer_figure_couches_epaisseurs.py` (matplotlib,
  aucun calcul CFD, aucun maillage — arithmétique pure sur les paramètres du dict).
- **Cas / modèle** : `case_kEpsilon_layers` · lecture de `system/snappyHexMeshDict`
  seulement.

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

## series_KT_tours.png / series_10KQ_tours.png / series_eta0_tours.png

- **Introduit (15/09, LOT A5, consigne « Ensemble »)** : K_T, 10·K_Q, η₀ en fonction des
  TOURS (pas des secondes), trois fermetures de turbulence superposées. Transitoire
  initial exclu (t<0,001 s, même filtre que `bilan_helice.py`), fenêtre commune et
  dernier tour marqués, trou de données `kOmegaSST` (13,8 ms) marqué visiblement, moyenne
  de chaque modèle sur la fenêtre commune en trait horizontal.
- **Réserve amplitude** : les valeurs annotées (0,0176/0,0223/0,0242) sont les valeurs
  COURANTES de `PARAMETRES_CAS.md` — PAS le rappel 0,0404/0,0373/0,0294 donné par la
  consigne de cette boucle, qui reprenait sans le savoir des chiffres pré-rééchelonnement
  déjà explicitement PÉRIMÉS depuis le 15/09 (voir JOURNAL).
- **Généré par** : `_Setup/outils/tracer_series_temporelles.py` (matplotlib, lit
  `Helice/data/perf_*.csv` déjà augmenté par `Helice/scripts/augmenter_tours_angle.py`
  — aucun calcul CFD, arithmétique et lecture de CSV existants).
- **Cas / modèle** : les trois cas (`case_kEpsilon`, `case_kOmegaSST`, `case_laminar`).

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
