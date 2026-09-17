# Séance 3 — y+ et couches de prismes (TD Hélice marine)

Support dédié de 30 minutes (LOT 3, consigne du 17/09 « Supports-séance-3 »), distinct
de `S03_Arborescence-et-perspective_Slides.md` (autre sujet : arborescence du dépôt,
incertitude, perspective de la séance). Un fichier séparé plutôt qu'une intégration :
le sujet (y+, couches de prismes, lecture d'une courbe K_T) ne recoupe qu'une seule
diapositive de l'autre deck (sa Diapo 10) et la remplace en substance avec des données
plus récentes — les deux decks restent indépendants, chacun projetable seul.

**Écart signalé, non corrigé ici (hors périmètre de cette boucle)** : la Diapo 10 de
`S03_Arborescence-et-perspective_Slides.md` cite un tout premier relevé y+ avec couches
(`log.yPlus2`, t=0,0005 s — min 14,56/max 1845,09/moyenne 96,86) sans fraction pondérée
par l'aire. Un second relevé, huit fois plus loin dans le temps (t=0,004 s = 0,10 tour,
16/09) et AVEC fraction par l'aire, existe désormais et est celui utilisé ci-dessous
(voir Diapo 4). Les deux restent NON convergés — aucun des deux n'est faux, le second
est seulement plus loin et plus complet.

Format identique aux autres decks de ce dépôt — voir `_Setup/NOTE_GABARIT_PPTX.md`.

---

## Diapo 0 — Titre
**Disposition** : Couverture

**Contenu affiché** :
y+ et couches de prismes
Ce que nos données disent — et ne disent pas encore

**Notes d'orateur** :
30 minutes. Trois questions : qu'est-ce que y+, qu'est-ce que les couches de prismes
sont censées faire, et est-ce que NOTRE maillage à couches atteint ce qu'il visait —
réponse : pas encore, et pas de manière uniforme sur toute la pale.

---

## Diapo 1 — y+, une distance à la paroi mesurée dans l'unité de l'écoulement
**Disposition** : Corps

**Contenu affiché** :
y+, une distance à la paroi mesurée dans l'unité de l'écoulement
y+ = y·u_tau / nu, avec u_tau = racine(tau_w / rho).
y : distance du centre de la première cellule à la paroi. u_tau : vitesse de frottement, déduite de la contrainte de paroi tau_w. nu : viscosité cinématique.
Ce n'est PAS une longueur physique : la même distance en mètres correspond à un y+ différent selon l'intensité du frottement local à cet endroit de la pale.

**Notes d'orateur** :
Source : `Helice/docs/03_BASE_THEORIQUE.md` §4 (« y+, distance à la paroi
adimensionnée »). Le point à faire passer : deux points à la même distance physique de
la paroi peuvent avoir un y+ très différent — c'est pour ça qu'on ne peut pas se fier à
l'œil sur un maillage, il faut le calculer.

---

## Diapo 2 — Trois régions, deux stratégies incompatibles
**Disposition** : Tableau

**Contenu affiché** :
Trois régions de la couche limite turbulente
| Région | Plage en y+ | Ce qui domine |
|---|---|---|
| Sous-couche visqueuse | y+ <~ 5 | viscosité seule, profil linéaire |
| Zone tampon | 5 <~ y+ <~ 30 | ni l'un ni l'autre — aucune loi simple valide |
| Zone logarithmique | 30 <~ y+ <~ 300 | turbulence établie, profil en ln(y+) |

**Notes d'orateur** :
Source : `Helice/docs/03_BASE_THEORIQUE.md` §4 (tableau des trois régions + section
« Deux stratégies »). Loi de paroi (notre cas, k-epsilon/k-omega SST RAS) : IMPOSE le
profil log à la première cellule, valide seulement si 30 < y+ < 300 — sous 30 on impose
une loi log à une cellule qui est en réalité en zone tampon ou sous-couche visqueuse,
au-dessus la loi log elle-même cesse d'être valable. Résolution directe (low-y+,
wall-resolved) : exige y+ <~ 1, une cellule 30 à 300 fois plus proche de la paroi — un
maillage local bien plus fin, ce que les couches de prismes visent à fournir sans
raffiner tout le maillage de cœur.

---

## Diapo 3 — Ce que font les couches de prismes
**Disposition** : Corps

**Contenu affiché** :
Ce que font les couches de prismes
Un maillage de cœur non structuré (snappyHexMesh sans traitement particulier) ne place pas de cellule assez proche d'une paroi courbe pour l'une ou l'autre stratégie.
Les couches de prismes insèrent, entre la surface et le maillage de cœur, un empilement de cellules fines alignées sur la normale à la paroi, d'épaisseur croissante — pour viser un y+ donné à la première cellule.
Les viser ne garantit pas de les atteindre : encore faut-il le mesurer.

**Notes d'orateur** :
Source : `Helice/docs/03_BASE_THEORIQUE.md` §4 (« Les couches de prismes »),
`system/snappyHexMeshDict` → `addLayersControls`. La dernière ligne est la charnière
vers la diapo suivante — c'est exactement ce qui n'a jamais été fait à convergence sur
ce cas.

---

## Diapo 4 — Notre cas : gain sur la pale, PAS un gain net
**Disposition** : Comparaison

**Contenu affiché** :
Notre cas : gain sur la pale, PAS un gain net

**Comparaison** :
A — Sans couches (propellerTip)
83,7 % de la surface dans [30;300], médiane 161, min 27,9, max 1043.
Les trois propellerStem : 95,0 % / 88,1 % / 95,6 % dans [30;300].
B — Avec couches — mesuré à t=0,004 s = 0,10 tour, PAS à convergence
propellerTip : 90,0 % dans [30;300] (aire), médiane 62,8 — mieux que sans couches.
Les trois propellerStem : 0 % dans [30;300] — TOUS sous 30 (15,6 à 27,6).

**Notes d'orateur** :
Sources : sans couches, `Helice/docs/PARAMETRES_CAS.md:33-36` et
`ETAT-DES-LIEUX_Enseignant.md:44-45`. Avec couches, `Helice/docs/PLAN_SEANCE-3.md:54-58`
(public, cite lui-même `ETAT-DES-LIEUX_Enseignant.md`, gitignoré, et
`PARAMETRES_CAS.md` LOT D1-D2 du 16/09). Le message : ajouter des couches a amélioré
le patch qui EN A (propellerTip, 83,7%→90,0%) mais les trois patches SANS couches
volontaires (propellerStem, `propellerTipEdge` a aussi 0 couche) sont tombés sous 30 —
cohérent avec des couches qui poussent y+ vers le bas comme visé (cible y+~50), mais pas
encore stabilisées à ce point du transitoire. Net : PAS un gain global, un gain localisé
qui déplace le problème plutôt que de le résoudre partout. Insister : à 0,10 tour, cette
comparaison elle-même reste provisoire (voir `PLAN_SEANCE-3.md`, la piste avancée qui
consiste à la reproduire à un tour comparable).

---

## Diapo 5 — Ce que le maillage a vraiment posé (couverture des couches)
**Disposition** : Figure

**Contenu affiché** :
Ce que le maillage a vraiment posé
6 couches demandées, 3,71 obtenues en moyenne sur propellerTip (76,8 % de couverture).

**Figure(s)** :
`Helice/Images/galerie/06b_couches_epaisseurs.png`

**Notes d'orateur** :
Généré par `_Setup/outils/generer_figure_couches_epaisseurs.py` (lecture de
`system/snappyHexMeshDict`, aucun calcul CFD). Sources des chiffres :
`Helice/docs/PARAMETRES_CAS.md:37-38` (couverture demandé/obtenu),
`Helice/case_kEpsilon_layers/log.snappyHexMesh.tipedge:2940`. Le point : la PROGRESSION
demandée (ce que trace le graphe) n'est pas ce que le maillage a réellement posé — une
couverture incomplète (3,71/6) explique en partie pourquoi le y+ obtenu (diapo
précédente) n'est pas uniformément dans la cible, même là où des couches existent.

---

## Diapo 6 — Lire une courbe de K_T
**Disposition** : FigureCommentee

**Contenu affiché** :
Lire une courbe de K_T

**Figure commentée** :
Abscisse en TOURS, pas en secondes — sinon les portions de cycle comparées diffèrent selon le modèle.
Dernier tour marqué (fond bleu) : fenêtre de moyenne (trait en tirets), jamais tout le calcul ni un point isolé.
Trou kOmegaSST (fond rouge) : absence de calcul, ligne franchement coupée — jamais reliée par un trait.
Piège des deux échelles : une amplitude mesurée sur une fenêtre plus longue grossit artificiellement — comparer QUE sur la même fenêtre.

**Figure(s)** :
`Helice/Images/FIG-fon-s7-KT-series-tours.png`

**Crédit** : `_Setup/outils/tracer_series_temporelles.py` — lit `Helice/data/perf_*.csv`.

**Notes d'orateur** :
Sources : `Helice/docs/METHODO_DONNEES.md` §3 (tours/angle), §4 (dernier tour), §6
(fenêtre commune), §5 défaut ① (trou kOmegaSST). Question de contrôle à poser à la
classe, jamais à répondre soi-même : combien de lignes du CSV couvrent un seul tour
d'hélice ? (Un répertoire de temps écrit n'est PAS un pas de temps calculé — voir
`METHODO_DONNEES.md` §2-§3 si la question bloque.)

---

## Diapo 7 — Ce qui reste à faire
**Disposition** : Cloture

**Contenu affiché** :
Ce qui reste à faire
Mesurer le y+ avec couches à convergence — jamais fait à ce jour.

**Notes d'orateur** :
Renvoi : `Helice/docs/PLAN_SEANCE-3.md`, piste avancée bornée (200 pas, pas de calcul en
production — 35-41 h sur 16 cœurs, INTERDIT en séance). Et `Helice/docs/
17_AUTO-EVALUATION_avant-seance-3.md` pour se tester avant lundi.
