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

## Diapo 1 — Progression : trois séances, un seul calcul
**Disposition** : Progression
**Segment / timing** : transition

**Contenu affiché** :
Trois séances, un seul calcul

**Progression** :
actif: 2
1 — Lire un résultat
K_T, la question des 3 pales, portance et traînée d'une pale
2 — Confronter
Trois fermetures, un classement impossible
3 — Voir, puis conclure
ParaView, restitution croisée
liaison: Le même calcul d'hélice tripale traverse les trois séances.

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
donne ses trois chiffres pour sa fermeture. Valeurs de référence (re-vérifiées par
exécution sur les CSV du dépôt, dernier tour) : K_T 0,363 / 0,378 / 0,371 ; η₀ 0,560 /
0,603 / 0,590 ; amplitude K_T (crête à crête) 0,0294 / 0,0404 / 0,0373 — à confronter aux
chiffres des groupes, jamais à leur substituer si un écart apparaît.

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
ΔK_T ≈ 0,015
B — Amplitude de l'oscillation
0,029 à 0,040 — 2 à 2,7 fois plus grande

**Notes d'orateur** :
La diapositive qui compte (désignée comme telle par le plan du 06/09). L'oscillation
qu'on doit moyenner pour lire K_T est 2 à 2,7 fois plus grande que l'écart qu'on cherche à
classer entre modèles. Origine de l'oscillation, à l'oral seulement (pas sur la
diapositive) : aucune raie à 3× la fréquence de rotation malgré l'hélice tripale — une
raie 1× accompagnée d'un 4× marqué désigne une origine numérique (maillage/interface AMI),
pas le passage des pales. Indice concordant : l'amplitude décroît quand la viscosité
turbulente augmente (laminaire > kOmegaSST > kEpsilon).

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

## Diapo 6 — Clôture
**Disposition** : Cloture
**Segment / timing** : Bilan (2 h)

**Contenu affiché** :
Fin de la séance 2 : un classement impossible, et pourquoi c'est la bonne conclusion.

**Notes d'orateur** :
Annoncer l'inter-séance B à l'oral : installation de ParaView (sur le modèle du pré-vol
S5 — script de vérification, page « ça n'a pas marché », un poste qui marche par binôme
suffit) et préparer UNE question à poser aux images en séance 3.
