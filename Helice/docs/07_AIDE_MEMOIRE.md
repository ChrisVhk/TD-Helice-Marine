# Aide-mémoire — TD Hélice marine en eau libre · OpenFOAM
*À imprimer recto-verso · A4 · ENSM — Génie Maritime · FON-S7*

---

## ① Hélice en eau libre — coefficients

| Grandeur | Formule | Sens |
|---|---|---|
| Coefficient d'avance | $J = \dfrac{V_a}{nD}$ | régime de fonctionnement (sans dim.) |
| Coefficient de poussée | $K_T = \dfrac{T}{\rho\,n^2 D^4}$ | poussée adimensionnée |
| Coefficient de couple | $K_Q = \dfrac{Q}{\rho\,n^2 D^5}$ | couple adimensionné |
| Rendement en eau libre | $\eta_0 = \dfrac{J}{2\pi}\,\dfrac{K_T}{K_Q}$ | puissance utile / puissance à l'arbre |

**Ce cas** : $\nu = 10^{-6}$ m²/s, $D = 0{,}2$ m, $n = 25{,}15$ tr/s, $V_a = 5$ m/s
→ $J \approx 0{,}99$, $Re \approx 10^6$ (turbulent).
Période de rotation $T = 1/n \approx \mathbf{0{,}0398}$ **s**. Calcul jusqu'à $t = 0{,}06$ s ≈ **1,5 tour**.

> Fichier de sortie `postProcessing/propellerInfo1/<t0>/propellerPerformance.dat`
> colonnes : `Time  n  URef  J  KT  10*KQ  eta0`.
> **`10*KQ` = $K_Q \times 10$** → diviser par 10.
> `URef` échantillonné en amont → **diffère un peu entre cas** → comparer à $J$ voisin.
> Normalisation avec $\rho_{ref} = 1{,}2$ (valeur du tutoriel, identique aux 3 cas → écarts relatifs valides).

---

## ② Les 3 fermetures de turbulence

| Cas | Modèle | Idée | Réputation |
|---|---|---|---|
| `case_kEpsilon` | RANS k-ε (2 éq. : $k$, $\varepsilon$) | robuste en cisaillement libre | **sur-estime** la turbulence en proche paroi et en gradient de pression adverse |
| `case_kOmegaSST` | RANS k-ω SST (2 éq. : $k$, $\omega$) | $k$-$\omega$ à la paroi + $k$-$\varepsilon$ au large, transition SST | **référence** hydrodynamique navale (décollement, paroi) |
| `case_laminar` | aucun ($\nu_t = 0$) | Navier-Stokes résolu tel quel | **incorrect** à ce $Re$ — cas dégradé assumé, sert de repère |

$\omega_0$ du cas k-ω est dérivé de $k_0$, $\varepsilon_0$ du cas k-ε via $\varepsilon = C_\mu k\omega$
($C_\mu = 0{,}09$) → même intensité turbulente en entrée, seule la fermeture change.

---

## ③ Ce qu'on doit lire dans les résultats

- **$K_T$ proche entre les 3 modèles, $K_Q$ plus dispersé** → signature attendue :
  poussée ← pression (peu sensible) ; couple ← frottement pariétal + sillage proche (sensible).
- **$\eta_0$ laminaire hors de l'intervalle des 2 cas RANS** → normal, pas une anomalie.
- **k-ω SST vs k-ε** : donner un écart **chiffré** sur $K_T$ ET sur $K_Q$.

---

## ④ POINT DE COURS — moyenner sur un tour

Les efforts oscillent au cours du tour — sur ce cas, à la **fréquence de rotation de l'arbre**
($n$), pas au passage de pale ($3n$) — cause : sillage instationnaire + interface AMI rotor/stator
recalculée à chaque pas.

1. **Ne pas lire la dernière ligne** du `.dat` : instant arbitraire du cycle.
2. **Moyenner** sur la fenêtre $[\,t_{end} - T,\ t_{end}\,]$ (dernier tour complet).
3. Drapeau **`⚠ < 1 tour écoulé`** → moyenne partielle, **ne pas exploiter**.
4. Regarder l'**amplitude** de l'oscillation : si ≈ l'écart entre modèles → conclusion prudente.

---

## ⑤ Validation — à vérifier

| Critère | Attendu | Où |
|---|---|---|
| `log.pimpleFoam` se termine par `End` | calcul allé au bout | fin du log |
| Résidu $p$ | sous le critère de `fvSolution` en fin de calcul | `log.pimpleFoam` / `convergence_residus.png` |
| Tableau post-traitement | 3 lignes, **aucun `⚠`** | `03_postprocess.sh` |
| Plausibilité | $K_T \sim 0{,}3$–$0{,}4$ ; $\eta_0 \sim 0{,}55$–$0{,}65$ ; pas de NaN | `bilan_helice.txt` |

> **Terminé ≠ convergé ≠ validé.**

---

## ⑥ Commandes en un coup d'œil

```bash
source /usr/lib/openfoam/openfoam2412/etc/bashrc     # environnement
cd ~/Work_ENSM/TD-Helice-Marine/Helice

bash 02_run.sh                    # maille + calcule les 3 cas (long)
foamListTimes -case case_kEpsilon # voir jusqu'où un cas est allé
bash 03_postprocess.sh            # tableau comparatif KT / 10KQ / eta0
python3 scripts/bilan_helice.py   # figures Results/ + bilan_helice.txt
bash 04_clean.sh                  # nettoyage (garde configs, supprime résultats)

# relancer un seul cas
cd case_kOmegaSST && ./Allrun.pre && ./Allrun
```

---

## ⑦ Structure d'un cas

```
case_kOmegaSST/
├── 0.orig/        conditions initiales/limites (U, p, k, omega, nut) — copiées vers 0/ par restore0Dir
├── constant/
│   ├── transportProperties      nu = 1e-6
│   ├── turbulenceProperties     simulationType RAS / modèle
│   └── dynamicMeshDict          rotation du domaine rotor (AMI)
└── system/
    ├── controlDict     endTime 0.06, deltaT adaptatif (maxCo 2), writeInterval 0.001
    ├── fvSchemes / fvSolution
    ├── snappyHexMeshDict        maillage autour de la géométrie de pale
    ├── forces / propellerInfo   function objects → postProcessing/
    └── decomposeParDict         4 sous-domaines
```

---

## ⑧ ParaView — essentiel

| Action | Menu |
|---|---|
| Ouvrir le cas | `touch case_X/case_X.foam` puis File → Open ; cocher **Reconstructed Case** |
| Dernier pas de temps | bouton ⏭ |
| Coupe de sillage | Filters → Slice, *Normal* `0 0 1` |
| Pression sur pale | source → *Coloring* `p`, patchs `propeller...` visibles |
| Tourbillons | Filters → Contour, *Contour By* `Q`, iso = `1000` |
| Comparer 3 cas | *Rescale to Custom Range* **identique** sur les 3, même caméra, même $t$ |
| Export | File → Save Screenshot, 1920×1080, fond blanc |

---

## ⑨ Tableau à compléter (restitution)

| Cas | $J$ | $K_T$ | $10\,K_Q$ | $\eta_0$ | amplitude $K_T$ (dernier tour) |
|---|---|---|---|---|---|
| k-ε | | | | | |
| k-ω SST | | | | | |
| laminaire | | | | | |

Écart k-ε ↔ k-ω SST : $\Delta K_T = \_\_\_$ (\_\_ %) · $\Delta K_Q = \_\_\_$ (\_\_ %)

---

*Références : Molland, Turnock & Hudson, *Ship Resistance and Propulsion* — Carlton, *Marine Propellers
and Propulsion* — tutoriel OpenFOAM `incompressible/pimpleFoam/RAS/propeller` (v2412).*
