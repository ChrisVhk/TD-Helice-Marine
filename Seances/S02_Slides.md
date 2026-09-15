# Séance 2 — TD Hélice marine (FON-S7) — source des diapositives

Une diapo = un bloc `## Diapo <N> — <titre>`, se termine à `---`. Champs : voir
`_Setup/NOTE_GABARIT_PPTX.md`. Matière reprise de
`/mnt/d/kdrive/ENSEIGNEMENT/01-cours/2026-09-06_TD-Helice_plan-seances-3x2h.md` §3 (plan
des 3 séances) et §2 (constats mesurés, re-vérifiés par exécution sur les CSV du dépôt —
voir le rapport de boucle, jamais recopiés du plan). 5 à 7 diapositives (consigne LOT I
§3) : le deck accompagne une confrontation orale, il ne la remplace pas.

---

## Diapo 0 — Couverture
**Disposition** : Couverture
**Segment / timing** : Ouverture

**Contenu affiché** :
TD Hélice marine
FON-S7 · Génie Maritime — 3 séances de 2 h
Séance 2 — Confronter

**Notes d'orateur** :
Chaque binôme arrive avec sa fermeture caractérisée (inter-séance A). Rien à recalculer
en séance : le calcul est un fait acquis depuis la séance 1.

---

<!-- RATTRAPAGE G1-G2 -->
**Bloc rattrapage — groupes 1 et 2 uniquement (décision enseignant, 15/09, équité).**
Fusionné depuis `Seances/S02bis_Rattrapage-groupes-1-2_Slides.md` (LOT 3, consigne du
15/09, source unique/deux sorties) — les groupes 1 et 2 ont passé leur séance 2 avant
la correction de D/y⁺ ; ce bloc leur donne, en ouverture, ce que le groupe 3 a reçu
directement dans la suite du deck. Numérotation volontairement hors séquence (90-93)
pour ne jamais entrer en conflit avec la numérotation 0-7 de la séance 2, citée ailleurs
dans le dépôt (`Helice/docs/ETAT-DES-LIEUX.md`, `_Methodo/JOURNAL.md`). Les deux
variantes (avec/sans ce bloc) sont produites par une seule commande
(`python3 Seances/generer_pptx_seance.py S02`, LOT 4-5 du 15/09) depuis cette source
unique — le marqueur ci-dessus suffit à déclencher la troisième sortie
`S02_groupes1-2.pptx`, rien à passer en argument.

## Diapo 90 — Titre (rattrapage)
**Disposition** : Couverture

**Contenu affiché** :
Rattrapage — ce que le groupe 3 a eu en séance 2
Trois points à mettre à jour avant de commencer la séance 3

**Notes d'orateur** :
À passer en 5 minutes en ouverture de séance 3, pour les groupes 1 et 2 uniquement.
Pas de nouvelle matière : une mise à jour de chiffres déjà vus, plus un point
théorique qui a été ajouté après leur passage.

---

## Diapo 91 — Les chiffres ont changé (rattrapage)
**Disposition** : Corps

**Contenu affiché** :
Les chiffres ont changé
- D était codé en dur à 0,2 m — mesuré et corrigé le 14/09 : D = 0,227378 m.
- K_T, 10K_Q ont été rééchelonnés en conséquence (facteur D⁴ et D⁵) : les valeurs que vous avez comparées en séance 2 ne sont plus les bonnes valeurs absolues.
- η₀ (le rendement) n'a PAS changé — c'est la seule grandeur mathématiquement invariante à cette correction, et c'est pour ça que rien ne vous a alertés en séance 2.
- Source unique désormais pour tout chiffre du cas : Helice/docs/PARAMETRES_CAS.md.

**Notes d'orateur** :
Ce n'est pas une remise en cause de votre travail de séance 2 : la LEÇON de la
diapositive « les deux nombres à mettre côte à côte » (l'oscillation domine l'écart
entre modèles) reste entièrement valable — elle est invariante au rééchelonnement,
comme η₀. Seuls les chiffres absolus de K_T et 10K_Q changent. Détail dans
`Helice/docs/PARAMETRES_CAS.md` et `_Methodo/JOURNAL.md` (entrée du 14/09).

---

## Diapo 92 — Ce que le maillage doit encore résoudre : y⁺ (rattrapage)
**Disposition** : Figure

**Contenu affiché** :
Ce que le maillage doit encore résoudre : y⁺

**Figure(s)** :
`Helice/Images/galerie/06b_couches_epaisseurs.png`

**Notes d'orateur** :
Point ajouté après votre séance 2 (théorie complète : `Helice/docs/
03_BASE_THEORIQUE.md` §4). Couches de prismes demandées contre couches réellement
obtenues (moyenne mesurée, 3,71/6 sur `propellerTip`, 76,8 %) — le maillage ne fait
pas ce qu'on lui demande partout. Détail en séance 3
(`Seances/S03_Arborescence-et-perspective_Slides.md`).

---

## Diapo 93 — Origine de l'oscillation : l'état réel (rattrapage)
**Disposition** : Corps

**Contenu affiché** :
Origine de l'oscillation : l'état réel
- En séance 2, l'origine de l'oscillation à 4× la fréquence de rotation était laissée ouverte à l'oral.
- État réel (non résolu) : deux mécanismes distincts prédisent EXACTEMENT la même fréquence — le passage de pale (Z=4) et la symétrie d'ordre 4 du fond cartésien (interface AMI).
- Le test qui les distinguerait — tourner le fond de 45° et relancer — n'a PAS été fait.
- Ce n'est pas une case à cocher qui manque : c'est une incertitude assumée et documentée (Helice/docs/ETAT-DES-LIEUX.md).

**Notes d'orateur** :
Même contenu que celui donné au groupe 3 en séance 2 (diapo « les deux nombres à
mettre côte à côte »). Insister : documenter une incertitude n'est pas un échec du
TD, c'est l'objet même de la démarche scientifique qu'il enseigne.

---
<!-- FIN RATTRAPAGE -->

## Diapo 1 — Progression : trois séances, un seul calcul
**Disposition** : Progression
**Segment / timing** : transition

**Contenu affiché** :
Trois séances, un seul calcul

**Progression** :
actif: 2
1 — Lire un résultat
K_T, la question des 4 pales, portance et traînée d'une pale
2 — Confronter
Trois fermetures, un classement impossible
3 — Voir, puis conclure
ParaView, restitution croisée
liaison: Le même calcul d'hélice quadripale traverse les trois séances.

**Notes d'orateur** :
Le TD hélice n'a que 3 séances — le 4e emplacement de la disposition reste vide,
neutralisé par le générateur (prévu au LOT F).

---

## Diapo 2 — Tableau : les trois fermetures — vos chiffres
**Disposition** : Tableau
**Segment / timing** : Partie A (30 min)

**Contenu affiché** :
Chaque groupe pose ses chiffres au tableau
| | kEpsilon | laminaire | kOmegaSST |
|---|---|---|---|
| K_T | | | |
| η₀ | | | |
| amplitude K_T | | | |

**Notes d'orateur** :
Tableau volontairement VIDE — à remplir en direct pendant la partie A, chaque groupe
donne ses trois chiffres pour sa fermeture. Valeurs de référence (source unique :
`Helice/docs/PARAMETRES_CAS.md`, fichier+ligne pour chacune) : K_T 0,2170 / 0,2261 /
0,2221 ; η₀ 0,5599 / 0,6033 / 0,5901 ; amplitude K_T (crête à crête, fenêtre commune)
0,0176 / 0,0242 / 0,0223 — à confronter aux chiffres des groupes, jamais à leur
substituer si un écart apparaît. **Corrigé le 15/09** : ces trois séries de chiffres
avaient encore les valeurs d'avant le rééchelonnement de D du 14/09 (0,363/0,378/0,371
pour K_T, 0,0294/0,0404/0,0373 pour l'amplitude) — remplacées ; η₀ inchangé (invariant
par construction) ; l'ORDRE entre les trois fermetures ne change jamais par un
rééchelonnement uniforme.

---

## Diapo 3 — Accroche : le classement impossible
**Disposition** : Accroche
**Segment / timing** : Partie B (1 h 30)

**Contenu affiché** :
Trois fermetures, trois jeux de chiffres.
Peut-on les classer ?

**Notes d'orateur** :
Laisser la salle essayer de classer avant la diapositive suivante — c'est le réflexe
naturel (« kOmegaSST est le plus fiable », etc.), et c'est exactement le réflexe que la
suite doit interroger.

---

## Diapo 4 — Comparaison : les deux nombres à mettre côte à côte
**Disposition** : Comparaison
**Segment / timing** : Partie B (1 h 30)

**Contenu affiché** :
Les deux nombres à mettre côte à côte

**Comparaison** :
A — Écart entre les 3 fermetures
ΔK_T ≈ 0,0091
B — Amplitude de l'oscillation
0,0176 à 0,0242 — 2 à 2,7 fois plus grande

**Notes d'orateur** :
La diapositive qui compte (désignée comme telle par le plan du 06/09). L'oscillation
qu'on doit moyenner pour lire K_T est 2 à 2,7 fois plus grande que l'écart qu'on cherche à
classer entre modèles — ce RAPPORT ne change pas avec le rééchelonnement de D du 14/09
(les deux grandeurs sont multipliées par le même facteur), seuls les chiffres absolus
ont changé (source : `Helice/docs/PARAMETRES_CAS.md`). Origine de l'oscillation, à
l'oral seulement (pas sur la diapositive) — **erratum du 13/09, voir
`Helice/docs/ERRATUM.md`** : l'hélice est quadripale (Z=4, pas 3), donc le passage de
pale attendu (4n = 100,6 Hz) tombe exactement sur la même case de résolution que la
raie à 4× déjà repérée. **État réel (15/09, voir `Helice/docs/ETAT-DES-LIEUX.md`,
item INCERTAIN « origine de la raie à 4× ») : deux mécanismes distincts prédisent
EXACTEMENT la même fréquence — passage de pale (Z=4) et symétrie d'ordre 4 du fond
cartésien (interface AMI) — et le test qui les discriminerait (tourner le fond de 45°
et relancer) n'a PAS été fait.** Le spectre seul ne peut donc pas trancher lequel des
deux domine. Seul indice qui reste concordant : l'amplitude décroît quand la viscosité
turbulente augmente (laminaire > kOmegaSST > kEpsilon) — cohérent avec au moins une
composante numérique, mais n'exclut pas une contribution physique réelle.

---

## Diapo 5 — Corps : la leçon
**Disposition** : Corps
**Segment / timing** : Partie B (1 h 30)

**Contenu affiché** :
La leçon
On ne compare pas trois modèles de turbulence quand l'incertitude numérique dépasse leur écart.
C'est vrai, et ce sont vos propres mesures qui le démontrent.

**Notes d'orateur** :
La compétence visée n'est pas de classer les modèles — c'est de savoir quand une
différence n'en est pas une. C'est ainsi que la capacité « se familiariser à la différence
des résultats selon le modèle de turbulence » du référentiel est réellement traitée.

---

## Diapo 6 — Ce que le maillage doit encore résoudre : y⁺
**Disposition** : Figure
**Segment / timing** : Bilan (2 h)

**Contenu affiché** :
Ce que le maillage doit encore résoudre : y⁺

**Figure(s)** :
`Helice/Images/galerie/06b_couches_epaisseurs.png`

**Notes d'orateur** :
Une seule diapositive — la séance 2 n'est pas un cours de maillage, ce point est
adossé à `Helice/docs/03_BASE_THEORIQUE.md` §4 (théorie complète : ce qu'est y⁺, les
trois régions de la couche limite, pourquoi une loi de paroi exige 30<y⁺<300).
Le graphe : épaisseur DEMANDÉE de chaque couche de prismes contre épaisseur
OBTENUE (moyenne mesurée, 3,71/6 couches sur `propellerTip`, 76,8 %) — le maillage
ne fait pas ce qu'on lui demande partout, et ça se voit, pas seulement en légende.
Renvoyer les questions détaillées à la séance 3 (`Seances/S03_Arborescence-et-
perspective_Slides.md`), qui couvre l'arborescence et la perspective couches en
entier.

---

## Diapo 7 — La pale est un baffle, pas un volume
**Disposition** : Corps
**Segment / timing** : Bilan (2 h)

**Contenu affiché** :
La pale est un baffle, pas un volume
- `log.snappyHexMesh` le dit explicitement : « Converting baffles back into zoned faces ».
- Un baffle est une surface d'épaisseur nulle, dupliquée en deux patches coïncidents (intrados, extrados) — pas un solide creusé dans le maillage fluide.
- Conséquence : « la pression sur la pale » désigne deux faces coïncidentes de normales opposées, jamais une seule surface.
- C'est pour ça que séparer intrados/extrados PAR ORIENTATION DE LA NORMALE est la méthode correcte — et la seule possible ici.

**Notes d'orateur** :
Trouvé le 15/09 en tentant un rendu (5e essai) d'une coupe cylindrique du maillage : la
coupe ne pouvait montrer aucun trou en forme de pale, à aucun rayon testé — l'écart
angulaire entre cellules fluides voisines (2,39°-4,09°) est celui d'une cellule de
cœur normale, pas d'un vide de la taille de la pale. Quatre tentatives d'image
antérieures avaient corrigé des symptômes de rendu sans jamais vérifier cette
prémisse. Détail théorique complet : `Helice/docs/03_BASE_THEORIQUE.md`, section
« La pale est un baffle, pas un volume » (juste après le §4 y⁺).

---

## Diapo 8 — Clôture
**Disposition** : Cloture
**Segment / timing** : Bilan (2 h)

**Contenu affiché** :
Fin de la séance 2 : un classement impossible, et pourquoi c'est la bonne conclusion.

**Notes d'orateur** :
Annoncer l'inter-séance B à l'oral : installation de ParaView (sur le modèle du pré-vol
S5 — script de vérification, page « ça n'a pas marché », un poste qui marche par binôme
suffit) et préparer UNE question à poser aux images en séance 3.
