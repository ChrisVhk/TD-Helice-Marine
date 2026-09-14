# Plan de séance 3 — TD Hélice marine (FON-S7)

Fait suite à la consigne « Correction-ensemble » du 13/09 (LOT E). `Helice/docs/STATUT.md`
est gitignoré (registre enseignant local, jamais suivi) : ce plan, lui, est **suivi**, pour
que le contenu traverse un changement de compte ou de machine (INV-11).

**Support de projection** : `Seances/S03_Arborescence-et-perspective_Slides.md` (deck,
14/09) — couvre l'arborescence, les mécanismes d'erreur et la perspective couches
détaillés ici.

---

## ACTE 1 — Le diagramme en eau libre construit en classe

Chaque binôme reçoit **un point de fonctionnement J** (un cas déjà calculé, ou une valeur
de $J$ à traiter). La classe reconstitue en direct, au tableau, le diagramme en eau libre
complet : $K_T(J)$, $10K_Q(J)$, $\eta_0(J)$.

**Avertissement à donner explicitement aux binômes avant qu'ils ne lancent quoi que ce
soit** : les points à **bas J** sont ceux qui vont le plus probablement diverger ou produire
des résultats aberrants (hélice chargée, écoulement décollé sur l'extrados). **Ce n'est pas
un échec de leur manipulation** — c'est le comportement physique attendu à ce régime, et ça
fait partie de la leçon : un point qui casse est une donnée, pas une faute.

## ACTE 2 — De la courbe au calcul d'auto-propulsion

La courbe construite en Acte 1 devient l'**entrée** d'un calcul d'auto-propulsion. **Théorie
et exploitation seulement — aucun calcul lancé.**

Relation d'équilibre : $T(1-t) = R_T$, avec $T$ lu sur la courbe du binôme au point
$J = \dfrac{V(1-w)}{nD}$.

Mobilise directement la matière Molland/Larsson déjà dérivée dans les masters
`ENSM-Enseignement` (coefficients de sillage $w$, de succion $t$, courbe de résistance
$R_T(V)$) — pas de nouvelle théorie à introduire, un raccord à un cours déjà fait.

## PISTE AVANCÉE — maillage à couches (binômes rapides uniquement, décision enseignant)

**Socle pour tout le monde = le point de J (Actes 1 et 2).** Cette piste est une option
réservée aux binômes qui ont fini en avance.

Objectif borné : **construire le maillage à couches de prismes, lancer 200 pas, vérifier
y⁺ et la stabilité.** C'est exactement l'échelle du test qui a réussi le 13/09
(`case_kEpsilon_layers`, pas fixe 1e-5 s, 200 pas francs, Courant max 0,58 — voir
`_Methodo/JOURNAL.md` côté `ENSM-Enseignement`, entrée « Pas fixe assumé »).

**Motif de cette piste** : `Helice/docs/ETAT-DES-LIEUX.md`, item INCERTAIN « y+ du
maillage à couches, à convergence » — jamais mesuré à ce jour (seul témoin,
`log.yPlus2`, donné à t=0,0005 s, transitoire non convergé). C'est la mesure qui
manque, et c'est exactement ce que cette piste irait chercher.

**INTERDIT, sans exception : demander un calcul en production.** Un cas à couches en
production coûte **35-41 h sur 16 cœurs** (`Helice/Results/amplitude_KT_fenetre-propre.md`
et JOURNAL.md, LOT A) — infaisable dans une séance, et le budget disque hôte ne le permet de
toute façon pas pour cinq cas simultanés (INV-23).

**Sa valeur pédagogique propre, à dire aux binômes qui la choisissent** : raffiner le
maillage (ajouter des couches) a **dégradé** la stabilité du calcul avant qu'un pas fixe ne
la restaure — un raffinement n'est pas automatiquement un progrès, et découvrir pourquoi
(couches au bout de pale retirées, `nSurfaceLayers 0` sur `propellerTipEdge`) est la leçon,
pas un aparté.

## EXÉCUTION

**PC personnel ou salle C009** (décision enseignant, cf. `01_FICHE_CONSIGNE.md`).

**À vérifier avant la séance, non fait ici** : OpenFOAM et WSL sont-ils disponibles sur les
postes de la salle C009 ? Aucun accès à cette information depuis ce poste — à confirmer par
l'enseignant ou le service informatique avant de compter sur cette salle comme repli.

## RÉSERVES

- **Identité de l'hélice** : voir section dédiée ci-dessous — une valeur au moins (le
  diamètre) ne correspond pas à ce qui est documenté, à trancher avant de bâtir la courbe
  J sur des grandeurs sans doute fausses.
- **`writeInterval` à dimensionner avant tout lancement** (INV-23, corollaire
  DIMENSIONNEMENT) : un point de la courbe de l'Acte 1 n'a besoin que des **forces**
  (`propellerInfo`), pas des champs volumiques — un `writeInterval` généreux sur les champs
  gonflerait le volume écrit pour rien. À fixer explicitement avant que les binômes ne
  lancent leur point.

---

## Identité de l'hélice — mesurée sur la géométrie, pas lue dans la documentation

**Pourquoi remesurer** : la documentation existante (`MATERIAU-INTRO_TD-Helice.md`) qualifiait
l'hélice de tripale — faux, corrigé le 13/09 (Z=4, `ERRATUM.md`). Une valeur non vérifiée sur
la géométrie s'est déjà révélée fausse une fois sur ce cas ; les autres grandeurs ci-dessous
ont donc été mesurées directement sur le maillage (`case_kEpsilon`, patches `propellerTip` /
`propellerStem1/2/3`, `t = 0,06 s`), pas recopiées.

| Grandeur | Valeur mesurée | Méthode | Incertitude |
|---|---|---|---|
| Nombre de pales Z | **4** | Histogramme angulaire du tiers extérieur de `propellerTip` (27 880 points), FFT de l'histogramme 36 bins/10° → harmonique dominante = 4 (période 90°). Contre-vérifié indépendamment sur `propellerStem1` (audit du 13/09). Deux méthodes indépendantes concordent. | Aucune — résultat entier, sans ambiguïté sur les deux méthodes. |
| Diamètre D | **0,227 m** (R_tip = 0,113689 m) | Rayon max $\sqrt{x^2+z^2}$ sur l'ensemble des points de `propellerTip`. **Vérification du 14/09, demandée avant tout arbitrage** : histogramme azimutal complet (360°) des 120 points au-delà de r=0,113 m → **QUATRE amas distincts** à 49,5°/139,5°/229,5°/319,5° (30 points chacun, séparés par des sauts >84°, aucun point intermédiaire) — exactement l'écart de 90° attendu pour Z=4. **Les quatre pales ont le MÊME r_max, 0,113689 m, identique à la 6ᵉ décimale.** Ce n'est pas une pale déviante isolée : les quatre sont géométriquement identiques à la précision du maillage. Percentiles de contrôle sur l'ensemble : p99 = 0,1120 m, p99,9 = 0,1135 m, p100 = 0,1137 m — progression lisse. | Aucune ambiguïté sur la symétrie (quatre amas identiques, conclusion (a) sans réserve). ~1 % sur la valeur elle-même (résolution du maillage de surface à la pointe de pale). **Écart avec la documentation existante (D = 0,2 m, `MATERIAU-INTRO_TD-Helice.md` §2) : ~14 %, non expliqué, signalé ici sans être corrigé ailleurs — arbitrage enseignant nécessaire avant de rebâtir la courbe J dessus.** Un premier calcul rapide sur la boîte englobante (bounding box) des patchs propeller avait donné ≈0,190 m — plus proche de la valeur documentée mais **faux** : la pointe de pale au rayon maximal n'est pas alignée avec les axes X ou Z, une boîte englobante la sous-estime. Piège méthodologique à ne pas reproduire. |
| Rayon de moyeu | **≈ 0,0264 m** | Rayon $\sqrt{x^2+z^2}$ moyen sur les points de `propellerStem1`, `propellerStem2`, `propellerStem3` (trois tranches indépendantes). | Très faible : écart min/max sur chaque tranche < 0,00015 m (< 0,6 %) ; les trois tranches concordent à moins de 0,00005 m entre elles — le moyeu est cylindrique à la précision du maillage. |
| Moyeu / D (rayon moyeu / rayon bout de pale) | **≈ 0,232** | Rapport direct des deux mesures ci-dessus (0,0264 / 0,1137). | Domine par l'incertitude sur D (~1 %) — le rayon de moyeu est très précis. |
| Pas géométrique P | **≈ 0,275 m** (dispersion 0,269–0,279 m selon le rayon) | Pente corde locale : une seule pale isolée angulairement (fenêtre de 85°), bande de rayon de ±4 mm centrée sur r/R = 0,4 à 0,9 (6 rayons), $P(r) = 2\pi r \cdot \Delta Y/\Delta s$ avec $\Delta s = r\cdot\Delta\theta$ sur les points de la bande. Mesure directe sur le nuage de points de surface (pression + succion mélangées), pas sur la ligne de cambrure — proxy de premier ordre, pas la définition exacte du pas géométrique d'un plan de pale. | ~4 % (dispersion inter-rayons observée, 0,269 à 0,279 m). Décroissance visible vers le bout de pale (r/R=0,9 : 0,269 m) : pourrait être un effet géométrique réel (pas non constant) ou un artefact de bord de pale sur cette méthode — **non tranché, à ne pas sur-interpréter.** |
| P/D | **≈ 1,21** (± ~0,04) | Rapport direct P / D ci-dessus. | Cumule les incertitudes de P (~4 %) et D (~1 %). |
| Rapport de surface (EAR ou aire projetée) | **NON MESURÉ PROPREMENT** | Tenté : comptage d'occupation sur grille 2D de la projection des points de `propellerTip` sur le plan (x,z), à 8 résolutions de 20×20 à 800×800 bins. **Aucun plateau de convergence** : le ratio mesuré descend de façon monotone de 0,77 (grille grossière) à 0,05 (grille fine) sans jamais se stabiliser — la densité de points de ce maillage est insuffisante pour cette méthode au-delà d'une résolution grossière, où elle surestime au contraire l'aire réelle (bins plus grands que l'espace entre les pales). | **Grandeur déclarée non mesurable proprement avec les outils et le temps de cette boucle** — elle ne s'estime pas au jugé (consigne explicite). Une mesure correcte demanderait l'union géométrique des polygones du maillage de surface (pas un comptage de points), ou la définition normée de l'EAR (contour développé, pas projeté) — ni l'une ni l'autre tentée ici. |

**Point le plus important de ce tableau, à trancher avant de construire quoi que ce soit sur
cette géométrie en séance 3** : le diamètre mesuré (≈0,227 m) ne correspond pas au diamètre
documenté (0,2 m) utilisé pour dériver $U_{tip}$, $\beta$ et d'autres grandeurs dans
`MATERIAU-INTRO_TD-Helice.md` §2. Cet écart n'est ni expliqué ni corrigé dans cette boucle
(hors périmètre du LOT E, qui mesure et rapporte, ne corrige pas le matériau pédagogique
existant) — **arbitrage enseignant requis** avant la séance 3 si le diamètre doit servir de
donnée d'entrée à l'Acte 2.

**Arbitrage rendu le 14/09** : D = 0,227378 m remplace 0,2 m dans `system/propellerInfo` (les
quatre cas) et dans toute la documentation qui le cite. J, K_T, 10K_Q rééchelonnés par
arithmétique (facteurs r/r⁴/r⁵) sur les données existantes, sans relance de calcul ; η₀
inchangé (invariant par construction, vérifié à moins de 5.10⁻⁵ sur les trois cas — voir
`_Methodo/JOURNAL.md`, 14/09). $U_{tip}$ et β de `MATERIAU-INTRO_TD-Helice.md` §2 recalculés
avec le rayon réel (0,113689 m).
