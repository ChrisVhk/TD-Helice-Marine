# Deck — Séance 1 (TD Hélice marine, FON-S7)

> Source de diapositives pour `fabricant-supports` (skill `produire-supports`). Format calqué sur
> `~/ENSM-Enseignement/_Setup/TEMPLATE_SEANCE_structure.md` (lu en référence, jamais modifié).
> Dispositions utilisées : celles du gabarit `_Setup/TEMPLATE_ENSM_cours.pptx` (13 dispositions
> confirmées par le générateur). Sortie attendue : `Helice/docs/DECK-SEANCE1.pptx` (ce dépôt).
>
> Contenu écrit par Claude Code (relecteur/rédacteur), à partir de la consigne
> `2026-09-06_PROMPT_ClaudeCode_soiree.md` LOT 3. La fabrication (remplissage des dispositions,
> charte, vérification visuelle diapo par diapo) revient à l'agent `fabricant-supports` — ce
> fichier ne fabrique rien par lui-même.

---

## Diapo 0 — Couverture
**Disposition** : Couverture
**Segment / timing** : Ouverture, avant le segment 1

**Contenu affiché** :
TD Hélice marine en eau libre
Séance 1 — Lire un résultat
FON-S7 · I4 · 07/09/2026

**Notes d'orateur** :
Contrôle d'ouverture déjà passé en tout début de séance (30 min sur les 120). Ce deck démarre
juste après. Public : I4, parcours DMO + EGN, binômes déjà formés pour le TD.

---

## Diapo 1 — La marche
**Disposition** : Rappel
**Segment / timing** : Segment 1, ouverture (~5 min)

**Contenu affiché** :
Au semestre dernier : Poiseuille, une solution analytique exacte — vous compariez.
Aujourd'hui : personne n'a la réponse. Ni essai, ni géométrie publiée.

**Repère de module** : FON-S6 → FON-S7

**Notes d'orateur** :
« Au semestre dernier, on vous a appris à faire tourner un calcul. Aujourd'hui, on vous demande
de décider si on peut le croire. » Dire cette phrase, la laisser porter — ne pas l'expliquer
davantage à ce stade, elle se déplie dans les diapos suivantes.
⚠️ Ne jamais dire ni laisser entendre « l'an dernier vous étiez passifs » : la comparaison porte
sur le PROBLÈME (une solution connue vs. aucune solution connue), pas sur le groupe. Un étudiant
à qui on dit qu'il a été passif se défend ; ce n'est pas l'effet recherché.
Rappel factuel si besoin à l'oral : Poiseuille a été fait en S6, ce n'est pas « l'an dernier » au
sens calendaire — le mot exact compte, cf. sujet du contrôle de ce matin.

---

## Diapo 2 — Où se situe ce problème
**Disposition** : Figure
**Segment / timing** : Segment 1, ouverture (~5 min)

**Contenu affiché** :
Les profils portants et la propulsion : ni surface libre, ni houle — la question ici est la
fermeture de turbulence, pas la surface libre.

**Figure(s)** : `FIG:fon-s7-CLASSIF-helice` — `Images/FIG-fon-s7-CLASSIF-helice.png` — carte de
classification à deux axes (complexité de l'écoulement × échelles temps/espace), zone « profils
portants, propulsion » mise en évidence, hélice en eau libre situé dedans.

**Crédit** : Schéma ENSM, réalisé pour ce TD (06/09/2026) — pas d'attribution tierce.

**Notes d'orateur** :
Schéma refait à la charte ENSM, PAS la figure `fon-s7-001` du collègue (DMN 1998 / IFP DeepFlow) :
son accord n'était pas acquis au moment de préparer cette séance, le deck ne pouvait pas en
dépendre pour exister. Si l'accord arrive, cette diapo peut être remplacée par la figure créditée
— décision et remplacement à faire plus tard, hors de cette séance.
Expliquer brièvement les deux axes : la résistance de vague et la tenue à la mer sont des cas à
surface libre déjà vus ou à venir en FON-S7 ; l'hélice en eau libre n'a pas de surface libre —
c'est pour ça qu'elle est ailleurs sur la carte, et que la question qui se pose est différente
(modèle de turbulence, pas modélisation de houle).

---

## Diapo 3 — L'objet du TD
**Disposition** : Figure
**Segment / timing** : Segment 1, ouverture (~2 min)

**Contenu affiché** :
Une hélice tripale en eau libre — c'est ce dont vos trois séries de données parlent.

**Figure(s)** : `FIG:fon-s7-helice-3D` — `Images/FIG-fon-s7-helice-3D.png` — rendu 3D de la
géométrie de pale (patch `propellerTip`), cas kEpsilon reconstruit à t=0,06.

**Crédit** : Rendu ENSM, pvpython headless sur le cas de ce TD (07/09/2026).

**Notes d'orateur** :
Correctif A2 (deck V2, 07/09, après retour du groupe 1) : « il manque des images parlantes » —
l'objet du TD n'apparaissait nulle part dans le deck jusqu'ici. C'est la géométrie réelle du cas,
pas une image d'illustration : D = 0,2 m, 3 pales, tourne à 25,15 tr/s (1 509 tr/min) autour de
l'axe vertical visible sur le rendu. Point d'échelle à donner ici ou en séance 2 : c'est une
maquette (D = 0,2 m à 1 509 tr/min) ; une hélice réelle fait 5 à 9 m pour 100-120 tr/min — le
passage modèle → réel (ITTC-78, essais en eau libre) est une discipline qu'ils rencontreront en
EGN-S9, pas ici.
Note technique pour qui régénère cette figure : le patch `propellerTip` porte les 3 pales et
`propellerStem1/2/3` porte l'arbre cylindrique — l'inverse de ce que les noms suggèrent,
vérifié en rendant chaque patch séparément (`_Setup/outils/generer_figure_helice_3D.py`).

---

## Diapo 4 — Trois métiers, une même question
**Disposition** : Tableau
**Segment / timing** : Segment 1, ouverture (~5 min)

**Contenu affiché** :

| Métier | La question |
|---|---|
| Superintendant | Un rapport de performance en service : encrassement, météo, ou mesure ? |
| Bureau d'études | Une prédiction de puissance : quelle marge son incertitude impose-t-elle ? |
| Ingénieur performance | Le chiffre lui-même : que doit-il au maillage ? |

**Notes d'orateur** :
« Ce chiffre, tu le crois ? » — la question qui revient dans les trois métiers. Ce n'est PAS une
diapo « débouchés » : c'est l'énoncé de la compétence visée par toute la séquence.
Un ingénieur ENSM ne produira presque jamais un calcul. Il en recevra — d'un chantier, d'un
bureau d'études, d'un fournisseur — et devra dire si le chiffre tient. C'est exactement ce que la
séance 1 met en pratique : on vous donne un chiffre (K_T), à vous de dire s'il tient.
Référence interne : `_Methodo/PORTE2_EGN-S9.md` §6 (tags marin/superint/be).

---

## Diapo 5 — Le contrat de travail
**Disposition** : Corps
**Segment / timing** : Segment 1→2, transition (~5 min)

**Contenu affiché** :
**Aujourd'hui et à la séance 2 : un tableur suffit.**
Les données sont trois fichiers CSV de moins de 500 Ko au total — pas d'OpenFOAM, pas de
ParaView, pas de ligne de commande.

- Le calcul est une donnée fournie — vous ne lancez aucun cas.
- Tout le monde en binôme ; chaque binôme reçoit les TROIS cas.
- La séance 2 se tient avec vos chiffres : mêmes données pour tous.
- ParaView ne sert qu'à la séance 3 — son installation est le travail de l'inter-séance B.
- C009 / C011 : la salle de secours si une machine ne suit pas — accès en autonomie **à venir**.
- Deux travaux à rendre avant la séance 2 (doc 12). Le dépôt versionné : diapo suivante.

**Notes d'orateur** :
**Correctif du 07/09, après retour du groupe 1 : ils ont galéré sur un environnement dont ils
n'avaient pas l'usage aujourd'hui.** Insister sur le bandeau : aucun besoin d'OpenFOAM ni de
ParaView avant la séance 3. « Vos machines d'abord » (renversement validé le 06/09) reste le
message pour la suite — vous avez déjà ce qu'il faut, un cas de quelques minutes et quelques
mégaoctets (inter-séance A, puis MRF plus tard) tourne sur un portable étudiant — mais ce n'est
PAS pour aujourd'hui. C009/C011 est le repli pour une machine qui ne suit pas, une install qui a
échoué, ou la session ParaView de la séance 3 — pas un passage obligé.

**Trois cas, pas un** : sans les trois fermetures, l'analyse comparative de la séance 2 est
impossible. Si deux binômes ne trouvent pas les mêmes moyennes sur les mêmes données, la question
qui se pose en séance 2 n'est pas la physique mais la méthode (quelle fenêtre, quel instant) —
venir sans chiffres, c'est n'avoir rien à confronter.

**Salles C009/C011 — reprendre les termes exacts, ne pas paraphraser** (note de service
N° 05/D/2026-2027 du 09/09/2026, P. Leblond, directeur de site, « Utilisation en autonomie des
salles C009, C011 et C012 », diffusion Élèves M1) :
- du lundi au vendredi, 8h00–18h30 (horaires de présence de l'administration) ;
- hors des heures de cours ;
- être au moins deux — l'organisation en binôme le satisfait d'office ;
- se déclarer à l'administration (BEF ou directeur) ;
- en partant : ranger, verrouiller la porte, rendre le badge.
⚠️ **La note prend effet le 09/09 ; cette séance est le 07/09.** L'annoncer comme **à venir**, pas
comme déjà en vigueur aujourd'hui. Ne pas recopier les consignes de sécurité de la note (paillasses,
découpeuse laser, fer à souder) : sans rapport avec ce TD, y renvoyer plutôt que d'en paraphraser
une partie. L'accès et le créneau se règlent avec le bureau des élèves, pas avec l'enseignant ;
l'installation logicielle des postes, en revanche, lui revient.

Le dépôt versionné : dire où vivent les données et les documents, et pourquoi c'est versionné —
une clause du contrat, pas une décoration.

---

## Diapo 6 — Le dépôt, concrètement
**Disposition** : Corps
**Segment / timing** : Segment 1→2, transition (~3 min)

**Contenu affiché** :
**Où** : dépôt GitHub public ChrisVhk/TD-Helice-Marine.

**Comment on l'obtient — une seule commande :**
git clone https://github.com/ChrisVhk/TD-Helice-Marine

- Dedans, pour l'instant : le dossier docs (les consignes) et le dossier data (les trois CSV) —
  le reste ne vous concerne pas encore.
- Aujourd'hui : ouvrir les trois CSV du dossier data dans un tableur. C'est tout.
- Vous rapportez : le livrable de l'inter-séance A (doc 12), en binôme.
- La matière : votre cours de mécanique des fluides du semestre dernier (Moodle), partie
  turbulence — utile dès la séance 2. Le doc 03 du dépôt en fait la synthèse courte.

**Notes d'orateur** :
⚠️ **Cette diapositive suppose le dépôt public et déjà poussé sur GitHub — ce n'est pas encore
fait au moment de préparer ce correctif** (aucun push cette nuit, c'est le geste de
l'enseignant). Vérifier avant de projeter que `git clone` fonctionne réellement depuis un poste
hors de ce compte. Si le dépôt n'est pas encore en ligne au moment de la séance : distribuer les
trois CSV autrement pour cette fois (pièce jointe, clé USB, dépôt Moodle) et corriger cette
diapositive dès que le dépôt est poussé — ne pas projeter une commande qui échouera devant la
salle.
Insister sur ce qui compte AUJOURD'HUI : la commande à taper, et seulement deux dossiers
(`docs/`, `data/`) — pas les quinze qu'ils verront s'ils explorent tout le dépôt. Le renvoi au
cours du semestre dernier répond à la question « je veux réviser, où je vais ? », restée
implicite jusqu'ici.

---

## Diapo 7 — Comment c'est noté
**Disposition** : Tableau
**Segment / timing** : Segment 2 (~3 min)

**Contenu affiché** :

| Objet | Ce que c'est |
|---|---|
| Ce TD | pas de contrôle |
| Le travail à rendre | formuler · mesurer · critiquer · rendre |
| L'attitude — 20 % | grille (diapo suivante) |
| Évaluation de formation continue | distincte — chaque groupe évalué une fois, à une phase et sur un objet différents |

**Notes d'orateur** :
Annoncer le PRINCIPE de l'évaluation continue, jamais le calendrier — préciser qu'aucun groupe ne
sait à l'avance quand ni sur quoi il sera évalué retire l'effet de piège et la comparaison entre
groupes. Ne pas répondre si la question du calendrier est posée par un étudiant : « ça viendra en
temps voulu » suffit.

---

## Diapo 8 — La grille d'attitude
**Disposition** : Tableau
**Segment / timing** : Segment 2 (~2 min)

**Contenu affiché** :

| Item | ++ (moteur) | + (actif) | − (passif) | −− (décroché) |
|---|---|---|---|---|
| Participation | Propose, alimente | Répond, pertinent | Suit sans contribuer | Décroché |
| Tableau / oral | Volontaire, argumente | Y va si désigné | Subit | Se défile |
| **Autonomie** | **Cherche avant** | **Essaie puis demande** | **Demande sans essayer** | **Redemande sans fin** |
| Rigueur | Vérifie, réutilise | Suit le fil | Oublie l'acquis | Tout à refaire |
| Initiative | Va au-delà | Fait proprement | Fait le minimum | Rien sans pousser |

**Notes d'orateur** :
Reprise **telle quelle** de la grille EGN-S9 (`Presentation_Intro.pptx`, diapo 18 — vérifié
verbatim le 06/09), qu'ils rencontreront en I5. Dire explicitement qu'elle vient d'EGN-S9 : ce
standard n'est pas inventé pour ce TD, c'est celui de l'école, appliqué un an plus tôt.
**Faire ressortir la ligne Autonomie** (mise en gras dans le tableau) : elle donne son sens à la
diapo 5 — « vos machines d'abord » n'a de sens que si l'autonomie est ce qui est valorisé.
Phrase de la grille source, à garder en tête sans nécessairement l'afficher : « La grille fait
référence. L'initiative et l'autonomie sont récompensées ; la négligence ou le désengagement
répétés sont pénalisés (item −− = malus). »

---

## Diapo 9 — Vos données
**Disposition** : Figure
**Segment / timing** : Segment 3, avant la question (~2 min)

**Contenu affiché** :
Ce sont vos données : trois séries, un même calcul, trois fermetures de turbulence.

**Figure(s)** : `FIG:fon-s7-KT-series-tours` — `Images/FIG-fon-s7-KT-series-tours.png` — série
temporelle de K_T, les 3 cas superposés, axe des temps en tours d'hélice.

**Crédit** : Vos données — perf_kEpsilon.csv, perf_kOmegaSST.csv, perf_laminar.csv.

**Notes d'orateur** :
Correctif A1 (deck V2, 07/09, après retour du groupe 1) — le correctif jugé le plus rentable du
lot : montrer la donnée avant de poser la question, plutôt que poser la question dans l'abstrait.
Ne RIEN dire du moment où il faut moyenner ni de la valeur finale — c'est tout l'objet du travail
qui suit. Faire remarquer, sans l'expliquer :
(a) le régime transitoire du tout début (jusqu'à ~0,3-0,5 tour) n'est pas le régime établi ;
(b) l'oscillation persiste même en régime établi ;
(c) le trou visible sur la courbe k-ω SST (~0,2 à 0,55 tour) est un vrai trou de données
(incident de calcul du 05/09, documenté dans STATUT.md), pas un artefact du tracé — bon exemple
si l'occasion se présente d'illustrer « lire un graphe honnêtement ».

---

## Diapo 10 — La question
**Disposition** : Accroche
**Segment / timing** : Segment 3, lancement du travail (~1 min)

**Contenu affiché** :
Quelle est la valeur de K_T ?

**Notes d'orateur** :
Pas de nouvelle donnée à l'écran par rapport à la diapo précédente — pas de piste
supplémentaire. Les données (les CSV du kit, séance 1 : `perf_kEpsilon.csv` et
`perf_laminar.csv` seulement, voir `data/README.md`) sont distribuées à ce moment, pas avant.
Laisser les binômes découvrir seuls qu'il faut moyenner et sur quelle fenêtre — c'est l'objet de
la séance, ne rien présenter en cours magistral avant.

---

## Diapo 11 — Les trois pales
**Disposition** : Tableau
**Segment / timing** : Segment 3 (~10 min, en fin de créneau K_T)

**Contenu affiché** :

| | |
|---|---|
| a) | L'hélice a 3 pales et tourne à 25,15 tr/s. À quelle fréquence la poussée devrait-elle osciller ? |
| b) | Cette fenêtre de données vous permet-elle de le vérifier ? Justifiez par un calcul de résolution. |
| c) | Que faudrait-il pour trancher, et qu'est-ce que ça coûterait ? |

**Notes d'orateur** :
**Formulation tranchée par le LOT 0A du 06/09 — ne pas dire « mesurez, elle n'y est pas ».** Sur
une fenêtre d'un tour, la résolution FFT vaut 25,15 Hz : les raies mesurées à 25,1 · 50,1 ·
100,3 Hz sont les cases 1, 2 et 4 de cette grille de résolution, et la fréquence de passage de
pale (75,44 Hz) tombe exactement sur la case 3. Il y a un **creux, pas une absence** — vérifié
(magnitude non nulle, très au-dessus du bruit). Affirmer « la raie n'y est pas » n'est pas soutenu
par la donnée, et pénaliserait à tort un binôme qui mesure honnêtement un petit pic à 75 Hz.
La question devient l'adéquation de la donnée à la question posée — même leçon que la séance 2,
une séance plus tôt : quelle fenêtre, quelle résolution, qu'est-ce que ça permet de conclure.
b) attend un calcul explicite : résolution = 1/(durée de la fenêtre) ; comparer à 75,44 Hz.
c) attend une réponse en coût (durée de calcul plus longue, donc en temps machine) autant qu'en
méthode (plus de tours, ou une méthode d'estimation robuste à un signal court).

---

## Diapo 12 — Ce que dit le spectre
**Disposition** : Figure
**Segment / timing** : Segment 3, reveal (~3 min) — **APRÈS que les binômes ont répondu**

**Contenu affiché** :
Le spectre confirme le calcul : la case de résolution a exactement la largeur de l'écart entre
deux harmoniques.

**Figure(s)** : `FIG:fon-s7-spectre-KT` — `Images/FIG-fon-s7-spectre-KT.png` — spectre de K_T
(dernier tour, kEpsilon et laminaire), harmoniques n/2n/3n/4n repérées, case de résolution
matérialisée en bande grisée.

**Crédit** : Vos données — perf_kEpsilon.csv, perf_laminar.csv.

**Notes d'orateur** :
Correctif A3 (deck V2, 07/09) — **diapo de reveal, à ne montrer qu'après que les binômes ont
proposé leur propre calcul de résolution** pour la question (b) de la diapo précédente. La
montrer avant viderait l'exercice de son objet : la question n'est plus « quel est le résultat »
mais « votre fenêtre de données vous permet-elle seulement de le sortir ».
Lecture : les seules fréquences que la fenêtre peut distinguer sont des multiples de la
résolution (~25,2 Hz) — d'où les bâtons, pas une courbe continue : entre deux bâtons, le spectre
ne dit rien, une ligne qui les relierait inventerait une information qui n'existe pas (défaut
trouvé et corrigé en construisant cette figure — boucle 10 appliquée à une figure, pas
seulement à une diapo). La case de résolution, centrée sur 3n = 75,44 Hz, a **exactement la largeur de l'écart entre deux
bâtons** (~25 Hz) : la fenêtre ne place un bâton pile sur 75,44 Hz que par chance (3n est un
multiple entier de la résolution ici) — un signal réel à 70 ou 80 Hz, légèrement décalé, serait
indiscernable du bâton voisin. C'est exactement pourquoi LOT 0A conclut « creux, pas absence, et
pas de conclusion possible sans calcul plus long » — pas un artefact de présentation, une limite
réelle de cette fenêtre.
kOmegaSST volontairement absent (exclu de toute mesure de fréquence, LOT 0A).
