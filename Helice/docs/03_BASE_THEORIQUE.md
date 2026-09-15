# Base théorique — Hélice en eau libre et fermetures de turbulence

## 1. Performance hélice en eau libre

Une hélice en eau libre (open water) est caractérisée sans interaction carène par 3 grandeurs
adimensionnées, fonctions du coefficient d'avance $J$ :

$$J = \frac{V_a}{nD}$$

avec $V_a$ la vitesse d'avance, $n$ la vitesse de rotation (tr/s), $D$ le diamètre de l'hélice.

$$K_T = \frac{T}{\rho n^2 D^4} \qquad K_Q = \frac{Q}{\rho n^2 D^5} \qquad \eta_0 = \frac{K_T}{K_Q}\cdot\frac{J}{2\pi}$$

où $T$ est la poussée (thrust), $Q$ le couple (torque), $\rho$ la masse volumique du fluide,
$\eta_0$ le rendement en eau libre. Ce sont les 3 sorties comparées entre modèles de turbulence
dans ce TD (colonnes `KT`, `10*KQ`, `eta0` de `postProcessing/propellerInfo1/*/propellerPerformance.dat`,
écrites directement par le function object `propellerInfo` du tutoriel — $K_Q$ y est tabulé
multiplié par 10 par convention d'affichage, à diviser par 10 pour la valeur physique).

## 2. Pourquoi le modèle de turbulence change le résultat

Les équations de Navier-Stokes exactes (DNS) sont hors de portée en TD (coût de calcul). Les
solveurs RANS (Reynolds-Averaged Navier-Stokes, ici `pimpleFoam`) résolvent un écoulement moyenné
et modélisent l'effet des fluctuations turbulentes via un tenseur de Reynolds fermé par un
**modèle de fermeture** — d'où l'attendu référentiel « se familiariser à la différence des
résultats selon le modèle de turbulence » : le modèle n'est pas un détail numérique, c'est une
hypothèse physique sur la turbulence qui change directement la traînée et donc $K_Q$/$\eta_0$.

### k-epsilon (RAS, `case_kEpsilon`)

Deux équations de transport (énergie cinétique turbulente $k$, taux de dissipation $\varepsilon$).
Robuste et peu coûteux en zone de cisaillement libre (sillage loin de la paroi), mais connu pour
sur-estimer la turbulence en proche paroi et en gradient de pression adverse — précisément la
situation sur l'extrados/l'intrados d'une pale où l'écoulement peut décoller localement.

### k-omega SST (RAS, `case_kOmegaSST`)

Combine $k$-$\omega$ en proche paroi (meilleur comportement en sous-couche visqueuse, pas besoin
de fonction de paroi aussi restrictive) et $k$-$\varepsilon$ en zone externe, avec un critère de
transition ("Shear Stress Transport"). Référence pour les écoulements avec gradient de pression
adverse et décollement — cas d'usage classique en hydrodynamique navale (carène, hélice, safran).
`omega0` de ce cas est dérivé de `epsilon0`/`k0` du cas k-epsilon via $\varepsilon = C_\mu k \omega$
($C_\mu = 0{,}09$) pour partir de la même intensité turbulente en entrée — seule la fermeture change.

### Laminaire (`case_laminar`)

Aucun modèle : les équations de Navier-Stokes incompressibles sont résolues telles quelles, sans
tenseur de Reynolds ($\nu_t = 0$ partout, pas de champ $k$/$\varepsilon$/$\omega$/$\nu_t$ à
résoudre). Physiquement incorrect au nombre de Reynolds réel d'une hélice marine (très supérieur
au seuil de transition), mais pédagogiquement utile : il matérialise ce qu'un modèle RAS *ajoute*
au calcul — sans lui, la couche limite ne peut ni s'épaissir ni décoller comme en réalité, ce qui
biaise directement $K_Q$ (couple/traînée visqueuse sous-estimée ou mal répartie).

## 3. Ce qu'il faut lire dans les résultats

- **KT proche entre les 3 modèles, KQ qui diverge davantage** : signature typique — la poussée
  est surtout pilotée par le champ de pression (moins sensible à la fermeture), le couple par le
  frottement pariétal et le sillage proche (très sensible à la fermeture).
- **η0 laminaire hors de l'intervalle RAS** : signal que le cas laminaire n'est pas physiquement
  représentatif à ce Reynolds — c'est le résultat attendu, pas une anomalie de calcul.

## 4. La paroi : $y^+$ et couches de prismes

Un modèle RAS ne modélise pas la turbulence de la même façon partout : près d'une paroi solide
(la pale), la turbulence est amortie par la viscosité sur une épaisseur bien plus fine que la
taille des cellules du maillage de cœur. Ce que le maillage fait de cette zone conditionne
directement $K_Q$ (§3) — c'est le sujet de cette section.

### $y^+$, distance à la paroi adimensionnée

$$y^+ = \frac{y\, u_\tau}{\nu} \qquad u_\tau = \sqrt{\frac{\tau_w}{\rho}}$$

où $y$ est la distance du centre de la première cellule à la paroi, $u_\tau$ la **vitesse de
frottement** (déduite de la contrainte de paroi $\tau_w$), et $\nu$ la viscosité cinématique
(§1). $y^+$ n'est pas une longueur physique : c'est une distance à la paroi mesurée dans l'unité
naturelle de l'écoulement proche paroi lui-même — la même distance physique correspond à un $y^+$
différent selon l'intensité du frottement local.

### Les trois régions de la couche limite turbulente

| Région | Plage en $y^+$ | Ce qui domine |
|---|---|---|
| Sous-couche visqueuse | $y^+ \lesssim 5$ | viscosité seule, profil de vitesse linéaire en $y^+$ |
| Zone tampon | $5 \lesssim y^+ \lesssim 30$ | ni l'un ni l'autre — zone de transition, aucune loi simple n'y est valide |
| Zone logarithmique | $30 \lesssim y^+ \lesssim 300$ | turbulence établie, profil de vitesse en $\ln(y^+)$ |

### Deux stratégies, deux exigences opposées sur $y^+$

- **Loi de paroi (wall function)** : le solveur ne résout pas la sous-couche visqueuse ni la zone
  tampon — il IMPOSE le profil logarithmique connu de la zone log comme condition à la première
  cellule. Cette loi n'est valide que si la première cellule tombe **dans** la zone log, d'où
  l'exigence $30 < y^+ < 300$ : en dessous, on impose une loi log à une cellule qui est en réalité
  dans la sous-couche visqueuse (où le profil est linéaire, pas logarithmique) ; au-dessus, la
  cellule sort de la zone où la loi log elle-même reste valable.
- **Résolution directe de la couche limite (low-$y^+$ / wall-resolved)** : le solveur calcule lui-
  même ce qui se passe dans la sous-couche visqueuse, sans loi imposée — il faut alors que la
  première cellule y soit vraiment, d'où l'exigence $y^+ \lesssim 1$. C'est une contrainte
  beaucoup plus dure : elle impose une première cellule environ 30 à 300 fois plus proche de la
  paroi que pour une loi de paroi, donc un maillage local bien plus fin.

### Les couches de prismes

Un maillage de cœur non structuré (comme celui produit par `snappyHexMesh` sans traitement
particulier) ne peut pas, à coût raisonnable, placer une cellule assez proche de la paroi pour
l'une ou l'autre stratégie — ses cellules près d'une surface courbe restent grossières et
irrégulières. Les **couches de prismes** (`addLayersControls` de `snappyHexMeshDict`) insèrent,
entre la surface et le maillage de cœur, un empilement de cellules fines et régulières,
alignées sur la normale à la paroi, d'épaisseur croissante (`expansionRatio`) — c'est ce qui
permet de viser un $y^+$ donné à la première cellule sans devoir raffiner tout le maillage de
cœur autour de la pale.

### Conclusion sur NOTRE cas

Chiffres sourcés dans `Helice/docs/PARAMETRES_CAS.md` (fichier et ligne pour chacun) :

- **Sans couches** (`case_kEpsilon`, celui des trois fermetures comparées au §2) : $y^+$ sur
  `propellerTip` a pour médiane 161 et va de 27,9 à 1043, avec 83,7 % de la surface dans
  $[30\,;\,300]$. La majorité de la surface EST dans la zone log — mais 16,3 % n'y est pas,
  dont tout le bout de pale au-delà de $y^+ \approx 300$ : ce cas n'est pas proprement dans le
  régime « loi de paroi » sur l'ensemble de la pale, il l'est seulement en majorité.
- **Avec couches** (`case_kEpsilon_layers`) : la stratégie visée était justement de descendre
  vers $y^+ \lesssim 1$ pour se rapprocher d'une résolution directe. Le seul relevé disponible
  (transitoire, non convergé) donne `propellerTip` de $y^+ = 14{,}6$ à $1845$ — **jamais sous 1**,
  pas même au minimum. Ce cas n'atteint pas non plus le régime qu'il visait.

**Notre cas n'est donc proprement dans aucun des deux régimes** : ni une loi de paroi
correctement posée sur toute la surface (régime 1), ni une couche limite réellement résolue
(régime 2) — un rappel que « mettre des couches de prismes » ne garantit pas, par construction,
d'atteindre l'objectif visé en les ajoutant : encore faut-il le mesurer, ce qui n'a jamais été
fait ici à convergence.

### La pale est un baffle, pas un volume

Tout ce qui précède (couches, $y^+$, loi de paroi) suppose une surface qui SÉPARE le fluide
d'un solide. Sur `propellerTip` (et plus généralement la pale de ce cas), ce n'est pas ce que
`snappyHexMesh` construit : le log le dit explicitement — `Converting baffles back into zoned
faces` (`Helice/case_kEpsilon_layers/log.snappyHexMesh`). Un **baffle** est une surface
d'ÉPAISSEUR NULLE, dupliquée en deux patches coïncidents (un jeu de faces « intrados », un jeu
de faces « extrados », géométriquement au même endroit) — pas une géométrie solide 3D creusée
hors du maillage fluide. Vérifié le 15/09 par une analyse indépendante de l'écart angulaire
entre centres de cellules fluides à plusieurs rayons/tranches Y de la pale : l'écart maximal
observé (2,39°–4,09°) correspond à la taille angulaire normale d'une cellule de cœur, jamais à
un vide de la taille du profil de pale — il n'existe, à aucun rayon, de trou en forme de pale
dans le volume fluide.

Deux conséquences directes :
- Les couches de prismes de `addLayersControls` croissent sur LES DEUX faces coïncidentes à la
  fois — pas seulement « autour » d'un solide unique. La couche limite est résolue deux fois,
  une pour chaque face, avec potentiellement deux profils $y^+$ différents (normales opposées).
- « La pression sur la pale » désigne en réalité la pression sur DEUX faces coïncidentes de
  normales opposées (patch intrados, patch extrados) au même endroit géométrique — jamais une
  seule surface. C'est exactement pour cela que séparer intrados et extrados **par orientation
  de la normale** (et non par une découpe géométrique/spatiale, impossible ici puisque les deux
  faces occupent la même position) est la méthode correcte, et la seule qui fonctionne, pour
  isoler la portance et la traînée d'une pale depuis ce maillage.
