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
