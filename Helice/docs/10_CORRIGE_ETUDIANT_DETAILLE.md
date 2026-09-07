# Corrigé étudiant détaillé — TD Hélice marine en eau libre

> Corrigé « comme si vous l'aviez rédigé » : la trame de restitution attendue, avec les
> **valeurs réellement obtenues** sur les 3 cas du dépôt (OpenFOAM 2412).
> Version enseignant condensée : [`09_FICHE_ENSEIGNANT.md`](09_FICHE_ENSEIGNANT.md).

> **État au 2026-09-06** : les **3 cas** sont terminés à $t = 0{,}06$ s (≈ 1,5 tour) et
> reconstruits sur toute la plage. Toutes les valeurs ci-dessous sont **définitives**
> (sortie de `bash 03_postprocess.sh` + `python3 scripts/bilan_helice.py`, moyennes sur le
> dernier tour $[0{,}0202 ;\ 0{,}06]$). `case_kOmegaSST` avait calé sur un incident de **disque
> hôte saturé** (et non un manque de mémoire) ; repris via `scripts/reprise_cas.sh` jusqu'à
> $t = 0{,}06$.

---

## 1. Rappel du cas

Hélice en eau libre (tutoriel officiel OpenFOAM `incompressible/pimpleFoam/RAS/propeller`),
solveur `pimpleFoam` instationnaire, interface AMI rotor/stator, **3 fermetures de turbulence**
sur géométrie / maillage / conditions aux limites U-p **identiques**.

| Paramètre | Valeur |
|---|---|
| $\nu$ | $10^{-6}$ m²/s |
| $D$ | 0,2 m |
| $n$ | 25,15 tr/s → $T = 1/n \approx 0{,}0398$ s |
| $V_a$ (inlet) | 5 m/s |
| $J$ nominal | $V_a/(nD) = 5/(25{,}15 \times 0{,}2) \approx 0{,}99$ |
| $Re$ | $\sim 10^6$ → turbulent |
| $endTime$ | 0,06 s ≈ 1,5 tour ; moyenne sur le dernier tour $[0{,}0202 ;\ 0{,}06]$ |
| Normalisation `propellerInfo` | $\rho_{ref} = 1{,}2$ (valeur du tutoriel, identique aux 3 cas) |

---

## 2. Tableau comparatif (moyenne sur le dernier tour complet)

Sortie de `bash 03_postprocess.sh` + `python3 scripts/bilan_helice.py`, colonne « amplitude » =
étendue crête-à-crête sur le dernier tour (lecture de `Results/comparaison_performance.png`).

| Cas | $t_{end}$ | tours | $J$ | $K_T$ | ampl. $K_T$ | $10\,K_Q$ | ampl. $10K_Q$ | $\eta_0$ |
|---|---|---|---|---|---|---|---|---|
| `case_kEpsilon` | 0,060 | 1,51 | 1,024 | **0,363** | 0,029 | **1,055** | 0,053 | **0,560** |
| `case_kOmegaSST` | 0,060 | 1,51 | 1,025 | **0,371** | 0,037 | **1,026** | 0,067 | **0,590** |
| `case_laminar` | 0,060 | 1,51 | 1,024 | **0,378** | 0,040 | **1,020** | 0,071 | **0,603** |

> `URef` (donc $J$) diffère légèrement d'un cas à l'autre : il est **échantillonné** dans
> l'écoulement en amont du disque, pas imposé. La comparaison se fait à $J$ **voisin** (≈ 1,02),
> pas rigoureusement égal. Écart de $J$ entre cas < 1 % → n'explique pas les écarts de $K_T$/$K_Q$.

---

## 3. Analyse

### 3.1 $K_T$ resserré, $\eta_0$ dispersé — pourquoi

Les trois $K_T$ tiennent dans un intervalle étroit (**0,36–0,38**, soit ~4 %), alors que $\eta_0$
s'étale davantage (**0,56–0,60**, soit ~7 %).

**Mécanisme.** La poussée $T$ vient d'abord de la **distribution de pression** sur les pales
(dépression sur l'extrados). Le champ de pression est peu sensible à la fermeture de turbulence.
Le couple $Q$, lui, intègre le **frottement pariétal** et l'entraînement du **sillage proche** —
tous deux directement pilotés par la viscosité turbulente $\nu_t$ que le modèle ajoute. Comme
$\eta_0 = \dfrac{J}{2\pi}\dfrac{K_T}{K_Q}$, la dispersion se reporte sur $\eta_0$ via $K_Q$.

> Signature classique : **$K_T$ robuste, $K_Q$ (et $\eta_0$) sensibles au modèle.**

### 3.2 Le cas laminaire

`case_laminar` donne le **$K_T$ le plus élevé** (0,378) et le **$10\,K_Q$ le plus bas** (1,020),
donc le **$\eta_0$ le plus élevé** (0,603 — hors de l'intervalle des deux cas RANS).

**Ce n'est pas un bug.** À $Re \sim 10^6$, l'écoulement réel est turbulent. Un calcul laminaire
résout Navier-Stokes sans terme turbulent ($\nu_t = 0$) : la couche limite ne s'épaissit pas
comme en réalité, le mélange turbulent dans le sillage est absent → la **traînée visqueuse et le
couple sont sous-estimés** → rendement **optimiste**. Le cas laminaire sert de **repère** : il
matérialise ce qu'un modèle RANS *ajoute* au calcul. Il n'est **pas** utilisable pour prédire une
performance.

### 3.3 k-ε vs k-ω SST

$$\Delta K_T = K_T^{k\omega} - K_T^{k\varepsilon} = 0{,}371 - 0{,}363 = +0{,}008 \quad (\approx +2\ \%)$$
$$\Delta (10K_Q) = 1{,}026 - 1{,}055 = -0{,}029 \quad (\approx -3\ \%)$$
$$\Delta \eta_0 = 0{,}590 - 0{,}560 = +0{,}030 \quad (\approx +5\ \%)$$

k-ω SST donne un **couple plus faible** que k-ε (de ~3 %), donc un **rendement plus élevé**
(de ~5 %), et se place **entre** k-ε et le cas laminaire — ce qui est cohérent : il diffuse moins
que k-ε sans annuler la turbulence comme le laminaire.

Interprétation : k-ε standard **sur-diffuse** la turbulence en proche paroi et en gradient de
pression adverse (extrados de pale) ; k-ω SST, avec sa formulation en $\omega$ près de la paroi et
son limiteur SST, représente mieux ce régime — c'est la fermeture de **référence** en
hydrodynamique navale (carène, hélice, safran). L'écart chiffré sur $K_Q$ traduit cette différence
de traitement du frottement pariétal. L'écart entre modèles (~3 % sur $K_Q$) reste **du même ordre
que l'amplitude d'oscillation** ($10K_Q$ : ampl. 0,05–0,07) : la hiérarchie k-ε → k-ω SST →
laminaire est nette et cohérente, mais les valeurs absolues demandent la prudence du §5.

### 3.4 Convergence

`Results/convergence_residus.png` : les 3 cas font descendre le résidu de pression sous le critère
de `fvSolution` à chaque pas de temps. Le cas laminaire converge le plus « facilement » (moins
d'équations), les cas RANS demandent quelques itérations PIMPLE de plus. Aucun cas ne diverge.

> **Attention** : « le calcul converge à chaque pas » **≠** « le résultat est établi ». Ici le
> résultat est **périodique** (il oscille au cours du tour), il n'y a pas de point fixe — d'où
> la moyenne sur un tour.

---

## 4. Le point de méthode : moyenner sur un tour

$K_T(t)$ et $K_Q(t)$ **oscillent** au cours du tour. La mesure (spectre du dernier tour) donne, sur
`case_kEpsilon` et `case_laminar`, une raie dominante à la **fréquence de rotation de l'arbre**
$n \approx 25{,}15$ Hz ($T = 1/n \approx 0{,}0398$ s) et ses harmoniques ($2n$, $4n$) —
**pas** à la fréquence de passage de pale $3n \approx 75$ Hz, pourtant attendue pour une hélice
tripale. Causes de l'instationnarité : sillage instationnaire + interface AMI recalculée à chaque
pas de temps.

> **`case_kOmegaSST` exclu de cette mesure — diagnostiqué le 06/09 au soir (LOT 0A).** Une
> première lecture y plaçait la raie à **26,2–26,3 Hz** au lieu de 25,15 Hz (écart ~4 %). Vérifié :
> ce n'est ni un mauvais recousage du CSV (série régénérée depuis les `.dat` bruts, checksum
> identique à celle déjà versionnée ; temps strictement croissant, un seul trou réel de
> $0{,}0082$ à $0{,}0220$ s — la reprise après l'incident disque du 05/09), ni une différence de
> vitesse imposée ($\omega = 158$ rad/s, identique dans les 3 `dynamicMeshDict`, soit exactement
> $158/2\pi = 25{,}15$ Hz). **La cause réelle : ce trou pousse le début de la « dernière fenêtre
> d'un tour » à $t=0{,}0220$ au lieu de $t=0{,}0202$, ce qui ne laisse que $0{,}955$ tour de
> données continues après le trou — plus court qu'un tour complet.** Une FFT ne peut pas résoudre
> une fréquence en dessous de $1/\text{durée de la fenêtre}$ ; $1/0{,}038 \approx 26{,}3$ Hz, quasi
> exactement la valeur erronée mesurée. Ce n'est donc pas un signal physique différent, mais une
> **limite de résolution spectrale** propre à ce cas. Les moyennes $K_T$/$K_Q$/$\eta_0$ du §2 ne
> sont **pas** affectées (une moyenne temporelle sur 0,955 tour reste fiable ; seule une analyse en
> fréquence exige un tour complet et continu) : `case_kOmegaSST` reste valide pour la comparaison
> de modèles (séance 2). **Conséquence pour la séance 1** : ne distribuer, pour la question de
> fréquence (§1-A), que `perf_kEpsilon.csv` et `perf_laminar.csv` — voir `data/README.md`.

- Lire la **dernière ligne** du `.dat` revient à échantillonner un instant arbitraire du cycle :
  deux modèles peuvent sembler très différents juste parce qu'ils ne sont pas en phase.
- On moyenne sur la fenêtre $[t_{end} - T,\ t_{end}]$ (dernier tour complet). `compare_turbulence.py`
  pose un drapeau `⚠` si le calcul n'a pas couvert un tour → moyenne partielle, à ne pas exploiter.
- L'**amplitude** de l'oscillation de $K_T$ (0,03–0,04, soit ~10 % de la moyenne) est du même
  ordre que l'écart entre modèles → toute conclusion doit reporter moyenne **et** amplitude, et
  rester prudente quand les intervalles se recouvrent.

> **Réserve — l'amplitude n'est pas un résultat purement physique.** L'absence de raie à $3n$
> (le passage de pale) alors que l'hélice est tripale, la présence d'un $4n$ sur un maillage de
> fond cartésien, et des poids d'interpolation AMI qui varient de 0,88 à 1,05 sur l'interface,
> pointent une **contribution numérique** à l'oscillation. Sur une fenêtre d'un seul tour, la
> résolution spectrale n'est que de $n \approx 25$ Hz : elle suffit à **écarter** le passage de
> pale comme moteur, pas à **établir** l'origine de l'amplitude. À traiter comme une question
> ouverte — un calcul plus long (`endTime = 0,10`, cf. §6 bonus) et un raffinement de l'interface
> AMI seraient nécessaires pour trancher.

---

## 5. Conclusion d'ingénieur

Pour prédire le rendement d'une hélice au point de fonctionnement :

- **Fermeture** : k-ω SST. k-ε standard convient pour un pré-dimensionnement rapide mais tend à
  biaiser le couple (sur-diffusion en proche paroi). Le calcul laminaire n'est utilisable que
  comme borne.
- **Durée de calcul** : au moins **2–3 tours** après établissement du régime, pour moyenner sur
  un tour propre avec marge. Ici 1,5 tour est un minimum acceptable pour un TD, pas pour une étude.
- **Lecture** : toujours en **moyenne sur le dernier tour**, avec report de l'amplitude
  d'oscillation.
- **À vérifier avant d'accorder une confiance quantitative aux valeurs absolues** : le $y^+$ sur
  les pales (adéquation modèle de paroi / maillage), la sensibilité au maillage, et une
  normalisation avec la vraie masse volumique de l'eau si on veut des efforts en Newtons.

**Ce que le TD démontre** : le choix du modèle de turbulence n'est pas un réglage numérique de
second ordre — c'est une **hypothèse physique** qui déplace directement le couple, donc le
rendement, de plusieurs pour-cent.

---

## 6. Livrables (rappel)

1. Tableau §2 complété (vos valeurs, moyennes + amplitudes).
2. `Results/comparaison_performance.png` commentée (oscillation + écarts entre modèles).
3. `Results/convergence_residus.png` commentée.
4. 3 captures ParaView comparables (même instant, même échelle) — cf. `05_GUIDE_PARAVIEW.md`.
5. Conclusion d'ingénieur (§5), argumentée et chiffrée.
