# Séance 3 — Arborescence, incertitude, perspective (TD Hélice marine)

Une diapo = un bloc `## Diapo <N> — <titre>`, se termine à `---`. Champs : voir
`_Setup/NOTE_GABARIT_PPTX.md`. Rédigé à partir de la spécification
`2026-09-14_CONSIGNE-ACTIVE_Deck-S03-arborescence-et-perspective.md` — la consigne ne
fournissait aucun texte de diapositive, celui-ci est rédigé depuis les sources du dépôt
(voir le rapport de boucle pour la liste valeur → source complète).

**Deux dispositions supplémentaires utilisées** au-delà des quatre citées par la
consigne (`Couverture`/`Figure`/`DeuxFigures`/`Corps`) : `Tableau` et `Comparaison`.
Les deux EXISTENT dans le gabarit (`NOTE_GABARIT_PPTX.md`, quatorze dispositions) et
correspondent mieux au contenu demandé — un tableau fichier-clé-effet, et l'établi/
l'incertain « côte à côte » — que ne l'aurait fait un pavé de texte dans `Corps`. La
consigne ne les interdit pas, elle liste seulement les quatre déjà vérifiées au LOT C
du 14/09 ; ce n'est pas une disposition inventée.

---

## Diapo 0 — Titre
**Disposition** : Couverture

**Contenu affiché** :
Arborescence, incertitude, perspective
Séance 3 — TD Hélice marine

**Notes d'orateur** :
Trois manques que l'introduction (S00) ne couvre pas : où vivent les paramètres du cas,
pourquoi nous nous sommes trompés quatre fois, et ce qui reste à mesurer sur le
maillage à couches.

---

## Diapo 1 — Ce qui est établi, ce qui ne l'est pas
**Disposition** : Comparaison

**Contenu affiché** :
Ce qui est établi, ce qui ne l'est pas

**Comparaison** :
A — Établi
Z=4 · D=0,227378 m · ρ sans effet sur K_T/K_Q · y+ (sans couches) 83,7% dans [30;300] ·
amplitude K_T laminaire>kOmegaSST>kEpsilon · η₀=0,5599/0,5901/0,6033
B — Incertain — assumé, pas minimisé
Origine de la raie à 4x · y+ des couches à convergence, jamais mesuré · les couches
améliorent-elles quoi que ce soit · convergence en maillage jamais faite · pas de temps
pour §4 · P/D et EAR

**Notes d'orateur** :
Source UNIQUE de cette diapositive : `Helice/docs/ETAT-DES-LIEUX.md`. Rien n'y est
ajouté qui n'y figure pas — chaque item ci-dessus est une ligne d'ÉTABLI ou d'INCERTAIN,
condensée, pas reformulée. La colonne de droite n'est pas un aveu de faiblesse : c'est
la carte de ce qui reste à faire, et une partie sert de matière à cette séance même
(l'y+ des couches).

---

## Diapo 2 — Trois dossiers, trois rôles
**Disposition** : Corps

**Contenu affiché** :
Trois dossiers, trois rôles
- `0/` (et `0.orig/`) — ce qui ÉVOLUE : les champs (U, p, k, epsilon, nut) à un instant. Résultat, jamais la définition du cas.
- `constant/` — ce qui DÉCRIT : la géométrie, les propriétés physiques (nu), le modèle de turbulence, la loi de rotation (dynamicMeshDict). Ne change jamais en cours de calcul.
- `system/` — ce qui PILOTE : le pas de temps, le découpage parallèle, les schémas numériques, les mesures demandées (propellerInfo). Ne décrit rien, ne calcule rien — configure.

**Notes d'orateur** :
Source : `Helice/docs/TUTORIEL_OpenFOAM-et-ParaView.md`, tableau §2 et partie 1. C'est
la grille de lecture qui manquait avant de chercher où vivent les valeurs de la diapo
suivante.

---

## Diapo 3 — Où vivent les valeurs clés
**Disposition** : Tableau

**Contenu affiché** :
Où vivent les valeurs clés
| Grandeur | Fichier · clé | Valeur | Effet |
|---|---|---|---|
| Rotation | constant/dynamicMeshDict, omega | 158 rad/s (= 25,15 tr/s) | pilote n, donc J et 4n=100,6 Hz |
| Vitesse imposée | 0.orig/U, patch inlet | uniform (0 -5 0) = 5,000 m/s | numérateur de J |
| Vitesse mesurée | postProcessing/.../propellerPerformance.dat, URef | ≈5,1657 m/s à t=0,06 s | J réellement rapporté |
| Viscosité | constant/transportProperties, nu | 1e-6 m²/s | Reynolds, ~1e6 |
| Diamètre | system/propellerInfo, radius | 0,113689 m (D=0,227378 m) | dénominateur de J (×D), K_T (×D⁴), K_Q (×D⁵) |
| Masse volumique | propellerInfo (1,2) vs forces (1) | deux valeurs différentes | aucun effet sur K_T/K_Q publiés |
| Pas de temps | system/controlDict, deltaT/maxCo | 1e-5 s, adjustTimeStep, maxCo=2 | stabilité, coût |
| Sous-domaines | system/decomposeParDict | 4, hierarchical | temps de calcul, jamais le résultat |

**Notes d'orateur** :
Chaque cellule vérifiée directement sur les fichiers du cas (`case_kEpsilon`) le 14/09,
pas recopiée d'un tableau antérieur. Le tableau lui-même sortira au style Office par
défaut, pas à la charte ENSM — le gabarit `TEMPLATE_ENSM_cours.pptx` a un
`tableStyles.xml` vide (chantier différé, voir JOURNAL).

---

## Diapo 4 — Le piège d'écrasement de `0/`
**Disposition** : Corps

**Contenu affiché** :
Le piège d'écrasement de 0/
- snappyHexMesh produit un dossier 0/ qui ne contient QUE le maillage remaillé, sans les champs physiques — inutilisable pour calculer.
- Allrun.pre le sait : il finit sur topoSet/createPatch, sans y toucher.
- C'est Allrun (le script parent), APRÈS Allrun.pre, qui appelle restore0Dir — une fonction standard des RunFunctions OpenFOAM — pour recopier 0.orig/ vers 0/, juste avant decomposePar.
- Éditer 0/U directement ne survit donc à AUCUN remaillage : la copie de sûreté, c'est 0.orig/.

**Notes d'orateur** :
Mécanisme vérifié le 14/09 en lisant `Allrun` et `Allrun.pre` du dépôt, pas supposé —
voir `Helice/docs/FICHES-CONDUITE_Enseignant.md`, correction du 14/09, et TUTORIEL §3
étape 5.

---

## Diapo 5 — Changer J, et sa réserve
**Disposition** : Corps

**Contenu affiché** :
Changer J, et sa réserve
- On édite 0.orig/U (patch inlet) pour changer la vitesse imposée — jamais 0/U, jamais URef.
- J imposé = V/(nD). Avec V=5,000 m/s, n=25,15 tr/s, D=0,227378 m : J imposé = 0,8743.
- Le J RAPPORTÉ dans propellerPerformance.dat ne coïncide PAS : à t=0,06 s, URef≈5,1657 m/s (mesuré en aval, pas imposé) donne J mesuré = 0,9033 — écart de 3,3 % sur la vitesse.
- La règle : on impose V, on lit le J mesuré, on porte le point au J lu — jamais au J visé.

**Notes d'orateur** :
Calcul refait le 14/09 directement sur `data/perf_kEpsilon_D0.2.csv` (dernière ligne,
t=0,06 s) avec le D corrigé — reproduit `FICHES-CONDUITE_Enseignant.md`
(J=0,9034, écart d'arrondi négligeable). Source de l'écart physique (~3,4 %) : URef est
échantillonné dans le sillage proche du disque, pas la vitesse d'entrée.

---

## Diapo 6 — Une vérification qui ne peut pas échouer ne vérifie rien
**Disposition** : Corps

**Contenu affiché** :
Une vérification qui ne peut pas échouer ne vérifie rien
- η₀ = J·K_T / (K_Q·2π). Les puissances de D (J en D¹, K_T en D⁴, K_Q en D⁵) s'annulent EXACTEMENT dans ce rapport — tout comme le facteur ρ.
- D était faux de 14 % (0,2 m codé en dur contre 0,227378 m mesuré) : K_T faux de ×1,67, K_Q faux de ×1,90 — et η₀ strictement inchangé.
- La seule grandeur qu'on vérifiait d'instinct (le rendement, « ça a l'air raisonnable ») était structurellement immunisée contre l'erreur cherchée.
- C'est pour ça que rien n'a alerté avant le 14/09.

**Notes d'orateur** :
Source : `_Methodo/DEFAUTS_DES_SOURCES.md`, entrée du 14/09 (« D codé en dur » —
« explique pourquoi rien n'a alerté jusqu'ici »). Mécanisme le plus important de la
séance — c'est pour ça qu'il a sa propre diapositive, à la demande explicite de la
consigne.

---

## Diapo 7 — Les quatre autres mécanismes de nos erreurs
**Disposition** : Corps

**Contenu affiché** :
Les quatre autres mécanismes de nos erreurs
- Constantes héritées jamais mesurées : D=0,2 m codé en dur depuis le tutoriel amont, jamais vérifié sur la géométrie avant le 13-14/09.
- Noms de fichiers pris pour des données : propellerStem1/2/3 lus comme « trois pales » — ce sont trois tranches de moyeu empilées, chacune d'ordre 4.
- Un adimensionnement qui amplifie l'erreur : 14 % d'écart sur D, élevé aux puissances 4 et 5, donne 67 % sur K_T et 90 % sur K_Q.
- Un chiffre non sourcé propagé comme s'il était mesuré : le « 60 % de surface en y+ valide » a circulé (audit, consignes, fiches) sans qu'aucun log ne soit jamais ouvert pour le vérifier.

**Notes d'orateur** :
Sources : `_Methodo/JOURNAL.md` (ENSM-Enseignement), entrées du 13/09 (erratum Z=4,
« lus comme trois pales ») et du 14/09 (« 60 % » retiré, jamais sourcé) ;
`_Methodo/DEFAUTS_DES_SOURCES.md` (D codé en dur, amplification ×1,67/×1,90). Le
quatrième point ici est la version sourcée du mécanisme parfois résumé « cas de
démonstration réemployé comme instrument de mesure » — la formulation exacte n'est
tracée nulle part dans le dépôt, celle-ci l'est.

---

## Diapo 8 — À quoi servent les couches de prismes
**Disposition** : Figure

**Contenu affiché** :
À quoi servent les couches de prismes

**Figure(s)** :
`Helice/Images/galerie/06_couches_prismes.png`

**Notes d'orateur** :
Elles résolvent la couche limite près de la paroi — la zone où le frottement se joue,
trop fine pour le maillage de coeur. Sans elles, le premier point de calcul près de la
pale serait trop loin de la paroi pour représenter le gradient de vitesse qui y règne.

---

## Diapo 9 — Demandé contre obtenu
**Disposition** : Tableau

**Contenu affiché** :
Demandé contre obtenu
| Patch | Faces | Couches demandées | Couches obtenues (moyenne) | Épaisseur | Couverture |
|---|---|---|---|---|---|
| propellerTip | 18480 | 6 | 3,71 | 0,00134 m | 76,8 % |
| propellerStem1 | 192 | 6 | 6 | 0,00179 m | 100 % |
| propellerStem2 | 576 | 6 | 6 | 0,00179 m | 100 % |
| propellerStem3 | 1536 | 6 | 6 | 0,00179 m | 100 % |

**Notes d'orateur** :
Source : `Helice/case_kEpsilon_layers/log.snappyHexMesh.tipedge` (le maillage
RÉELLEMENT sur disque aujourd'hui — nCells=608463, vérifié sur
`constant/polyMesh/owner`). Écart signalé : d'autres documents du dépôt
(`15_DECK-SEANCE1_Slides.md`, `MATERIAU-INTRO_TD-Helice.md`) citent encore « 4,42 en
moyenne, 82,7 % » — ce sont les chiffres d'un run ANTÉRIEUR
(`log.snappyHexMesh.v2`), avant que les couches du bout de pale ne soient retirées
(`propellerTipEdge`, `nSurfaceLayers 0`, voir `system/snappyHexMeshDict` ligne 367).
Pas corrigé ailleurs dans cette boucle — signalé dans le rapport.

---

## Diapo 10 — Le y+ des couches, jamais mesuré à convergence
**Disposition** : Corps

**Contenu affiché** :
Le y+ des couches, jamais mesuré à convergence
- Seul témoin disponible : log.yPlus (t=0,0005 s) — un régime transitoire précoce, pas un état convergé.
- propellerTip : y+ min 14,56, max 1845,09, moyenne 96,86. propellerTipEdge (sans couches) : min 37,72, max 1412,67, moyenne 186,94.
- Les champs de ce cas au-delà de ce maillage ont été détruits — aucune fraction pondérée par l'aire n'est calculable rétroactivement, contrairement au cas sans couches (83,7 % mesuré le 14/09).
- La leçon contre-intuitive : ajouter des couches a D'ABORD dégradé la stabilité du calcul, avant qu'un pas de temps fixe ne la restaure — un raffinement n'est pas automatiquement un progrès.

**Notes d'orateur** :
Source des y+ : `Helice/case_kEpsilon_layers/_bench_logs_tipedge/log.yPlus.tipedge`
(le log qui correspond au maillage tipedge actuellement sur disque — un log plus
ancien, `log.yPlus2`, donne des chiffres proches mais sans le patch
`propellerTipEdge` séparé, sur un maillage antérieur à la correction). Leçon de
stabilité : `Helice/docs/PLAN_SEANCE-3.md`, PISTE AVANCÉE.

---

## Diapo 11 — Le déroulé de la séance 3
**Disposition** : Corps

**Contenu affiché** :
Le déroulé de la séance 3
- Acte 1 : chaque binôme apporte SON point de J — mesuré sur son propre cas, pas le J nominal visé.
- Ces points, mis en commun, tracent le diagramme en eau libre collectif (K_T, K_Q, η₀ en fonction de J).
- Acte 2 : cette courbe entre comme donnée d'entrée dans un calcul d'auto-propulsion classique — SANS CFD, le calcul d'hélice reste en amont, jamais recalculé ici.
- Piste avancée, réservée aux binômes rapides : construire le maillage à couches jusqu'à un état mesurable et y mesurer le y+ — la mesure qui manque le plus (diapo précédente).

**Notes d'orateur** :
Source : `Helice/docs/ETAT-DES-LIEUX.md` §OÙ ON VA, et `Helice/docs/PLAN_SEANCE-3.md`
pour le détail de la piste avancée (bornes : interdit de lancer un calcul en
production, 35-41 h sur 16 cœurs).
