# Guide pas à pas — TD Hélice marine en eau libre (OpenFOAM)
## FON-S7 · Mécanique des fluides – Hydrodynamique · TD 6 h

---

## 1. Mission

Sur **un seul cas** — une hélice en eau libre (tutoriel officiel OpenFOAM `propeller`, interface
tournante AMI, solveur `pimpleFoam` instationnaire) — décliné en **3 fermetures de turbulence** :

| Cas | Fermeture | Champs turbulents résolus |
|---|---|---|
| `case_kEpsilon` | RANS k-ε | $k$, $\varepsilon$, $\nu_t$ |
| `case_kOmegaSST` | RANS k-ω SST | $k$, $\omega$, $\nu_t$ |
| `case_laminar` | aucune (laminaire) | — |

À la fin, vous devez répondre :
1. Comment $K_T$, $K_Q$ et $\eta_0$ diffèrent-ils selon la fermeture ? Lequel des trois coefficients est le plus sensible, et **pourquoi** ?
2. Lequel des deux modèles RANS est réputé le plus fiable ici, et sur quel argument physique ?
3. Pourquoi le cas laminaire n'est-il **pas** une erreur de calcul, mais un cas volontairement dégradé ?

**Paramètres du cas** (identiques aux 3 fermetures) : $\nu = 10^{-6}$ m²/s, $D = 0{,}2$ m,
$n = 25{,}15$ tr/s, vitesse d'avance $V_a = 5$ m/s (entrée `inlet`), soit $J = V_a/(nD) \approx 0{,}99$.
Reynolds de fonctionnement $\sim 10^6$ → **écoulement franchement turbulent**.

---

## 2. Parcours conseillé (6 h)

| Phase | Durée | Activité |
|---|---|---|
| 0h00 – 0h15 | 15 min | QCM prérequis (`02_QCM_PREREQUIS.md`) |
| 0h15 – 0h35 | 20 min | **Lancer le calcul** (§3) — puis on enchaîne pendant qu'il tourne |
| 0h35 – 1h20 | 45 min | Théorie (`03_BASE_THEORIQUE.md`) : $K_T$/$K_Q$/$J$/$\eta_0$, ce qu'une fermeture change |
| 1h20 – 2h30 | 70 min | Visualisation ParaView (`05_GUIDE_PARAVIEW.md`) : sillage, pression sur pale, comparaison qualitative |
| 2h30 – 3h30 | 60 min | **Pause déjeuner / le calcul continue** |
| 3h30 – 4h45 | 75 min | Analyse quantitative (§4 et §5) : tableau $K_T$/$K_Q$/$\eta_0$, moyennes sur le dernier tour |
| 4h45 – 5h45 | 60 min | Interprétation physique (§6) + rédaction de la restitution |
| 5h45 – 6h00 | 15 min | QCM final (`06_QCM_FINAL.md`) |

> Les 3 cas sont **longs** (maillage `snappyHexMesh` + calcul instationnaire parallèle, > 1 h chacun
> sur 4 cœurs). On lance en tout premier, on travaille la théorie et la visualisation pendant ce temps.

---

## 3. Lancer le calcul

```bash
source /usr/lib/openfoam/openfoam2412/etc/bashrc     # environnement OpenFOAM 2412
cd ~/Work_ENSM/TD-Helice-Marine/Helice
bash 02_run.sh        # maille + calcule les 3 cas, l'un après l'autre
```

`02_run.sh` enchaîne pour chaque cas :
1. `Allrun.pre` — géométrie de pale, `blockMesh`, `surfaceFeatureExtract`, `snappyHexMesh`,
   `renumberMesh`, `topoSet`, `createPatch` (crée l'interface AMI rotor/stator).
2. `Allrun` — `restore0Dir`, `decomposePar` (4 sous-domaines), `pimpleFoam` en parallèle,
   `reconstructPar`.

Pour ne relancer qu'un seul cas :
```bash
cd case_kOmegaSST && ./Allrun.pre && ./Allrun
```

> **Si un cas est déjà calculé** (dossiers de temps `0.001 … 0.06` présents, log `log.pimpleFoam`
> terminé par `End`), ne le relancez pas : `02_run.sh` **remaillerait et recalculerait tout depuis
> zéro**. Vérifiez d'abord avec `foamListTimes -case case_XXX`.

**Contrainte mémoire** : sur une machine à 16 Go de RAM, les 4 processus d'écriture simultanés
peuvent saturer la mémoire au moment d'écrire un pas de temps (le noyau tue alors le calcul, et le
pas de temps concerné est écrit vide — 0 octet). Si ça arrive : supprimer le pas de temps corrompu
dans les 4 dossiers `processor*/`, puis relancer `./Allrun` (il repart du dernier pas valide grâce
à `startFrom latestTime`).

---

## 4. Ce qu'on lit dans les résultats : `propellerInfo`

Chaque cas embarque le *function object* `propellerInfo` du tutoriel : il écrit en cours de calcul,
dans `postProcessing/propellerInfo1/<t0>/propellerPerformance.dat`, les colonnes

```
Time   n   URef   J   KT   10*KQ   eta0
```

- `10*KQ` est $K_Q$ **multiplié par 10** (convention d'affichage) : diviser par 10 pour la valeur physique.
- `URef` est la vitesse de référence **échantillonnée** dans l'écoulement en amont du disque — elle
  n'est pas exactement égale à $V_a = 5$ m/s et **diffère légèrement d'un cas à l'autre**. Donc $J$
  aussi. La comparaison entre modèles se fait à $J$ **voisin**, pas rigoureusement égal — à mentionner
  dans la restitution.
- La normalisation utilise $\rho_{\text{ref}} = 1{,}2$ kg/m³ (valeur laissée du tutoriel). Comme elle
  est **la même pour les 3 cas**, la comparaison reste valide ; les valeurs absolues de $K_T$/$K_Q$
  ne sont donc pas celles d'un essai en bassin, mais leurs **écarts relatifs** entre fermetures le sont.

Post-traitement automatique :
```bash
bash 03_postprocess.sh              # tableau comparatif des 3 modèles (compare_turbulence.py)
python3 scripts/bilan_helice.py     # + figures dans Results/ (résidus, KT/KQ/eta0 vs temps)
```

---

## 5. POINT DE COURS — pourquoi on moyenne, et sur quoi

**$K_T$, $K_Q$ et $\eta_0$ n'atteignent pas une valeur unique : ils oscillent.**

L'hélice tourne. Le sillage est instationnaire, et l'interface AMI qui relie le domaine tournant
(rotor) au domaine fixe (stator) est recalculée à chaque pas de temps. Résultat : la poussée et le
couple **varient périodiquement** au cours d'un tour.

Période de **rotation de l'arbre** — c'est la période sur laquelle on moyenne :
$$T = \frac{1}{n} = \frac{1}{25{,}15} \approx 0{,}0398 \text{ s}$$

> Sur ce cas, la variation mesurée est dominée par cette fréquence de rotation ($1$ tour), **pas**
> par le passage des pales (qui serait 3 fois plus rapide, $T/3 \approx 0{,}013$ s) — signe que
> l'oscillation a une part numérique, détaillée dans la fiche enseignant. Quoi qu'il en soit, on
> moyenne sur **un tour complet**.

Le calcul s'arrête à $t = 0{,}06$ s, soit **≈ 1,5 tour**. Conséquences pratiques :

1. **Lire la dernière ligne du fichier est trompeur** : elle tombe sur un instant arbitraire du
   cycle (pale devant un point particulier). Deux modèles lus au même $t$ peuvent sembler très
   différents juste parce qu'ils ne sont pas en phase.
2. **On moyenne sur le dernier tour complet** écoulé : fenêtre $[\,t_{end}-T,\ t_{end}\,]$. C'est ce
   que fait `compare_turbulence.py` (et `bilan_helice.py`). Si le calcul n'a pas encore couvert un
   tour entier, le script pose un drapeau `⚠` : la moyenne est alors partielle, **à ne pas exploiter**.
3. **Vérifier l'amplitude de l'oscillation** sur la figure `Results/comparaison_performance.png` :
   si elle est du même ordre que l'écart entre modèles, la conclusion doit rester prudente.

> C'est un point de méthode CFD réutilisable : un résultat instationnaire ne se lit jamais à un
> instant isolé, il se moyenne (ou se décrit par sa moyenne **et** son amplitude) sur un cycle
> physique caractéristique.

---

## 6. Questions obligatoires (restitution)

1. **Tableau comparatif** des 3 fermetures : $J$, $K_T$, $10\,K_Q$, $\eta_0$ (moyenne dernier tour,
   nombre d'échantillons), + amplitude crête-à-crête de $K_T$ sur le dernier tour.
2. **$K_T$ vs $K_Q$** : lequel des deux est le plus dispersé entre les 3 modèles ? Proposez
   l'explication physique (rôle de la pression vs rôle du frottement pariétal et du sillage proche).
3. **k-ε vs k-ω SST** : donnez au moins **un indicateur chiffré** de l'écart sur $K_T$ et sur $K_Q$.
   Lequel retiendriez-vous pour un calcul d'hélice, et pourquoi (proche paroi, gradient de pression
   adverse, décollement) ?
4. **Cas laminaire** : son $\eta_0$ tombe-t-il dans l'intervalle des deux cas RANS ou en dehors ?
   Expliquez pourquoi ce n'est **pas** une anomalie numérique (Reynolds réel ≫ transition, la
   couche limite ne peut ni s'épaissir ni décoller correctement sans modèle).
5. **Conclusion d'ingénieur** (10–15 lignes) : pour un bureau d'études qui doit prédire le rendement
   d'une hélice au point de fonctionnement, quelle fermeture, quelle durée de calcul (combien de
   tours), quelles précautions de lecture des résultats ?

---

## 7. Livrables

1. Tableau comparatif des 3 cas (§6.1).
2. Figure `comparaison_performance.png` commentée (oscillation + écarts entre modèles).
3. Figure `convergence_residus.png` commentée (les 3 cas convergent-ils au même rythme ?).
4. 3 captures ParaView comparables (même instant, même échelle) : sillage des 3 cas.
5. Conclusion d'ingénieur argumentée et chiffrée.

---

## 8. Erreurs fréquentes à éviter

1. Lire $K_T$/$K_Q$ sur la **dernière ligne** du `.dat` au lieu de la moyenne sur un tour.
2. Exploiter une moyenne encore marquée `⚠ < 1 tour écoulé`.
3. Comparer deux modèles à des $J$ traités comme identiques alors que `URef` diffère.
4. Conclure « le laminaire est faux donc le calcul a raté » : il est **volontairement** dégradé.
5. Rester qualitatif : « k-ω donne un peu plus » sans chiffre = analyse incomplète.
6. Relancer `02_run.sh` sur un cas déjà terminé et perdre le résultat.
7. Oublier de diviser la colonne `10*KQ` par 10.

---

## 9. Checkpoints enseignant

- **A** — les 3 cas maillent et le solveur tourne sans erreur bloquante (`log.pimpleFoam` progresse,
  résidus $p$ sous le critère de `fvSolution`).
- **B** — `03_postprocess.sh` sort un tableau à 3 lignes **sans drapeau ⚠**.
- **C** — l'écart k-ε vs k-ω SST sur $K_T$ **et** $K_Q$ est chiffré (pas seulement qualitatif).
- **D** — le cas laminaire est interprété comme un cas dégradé assumé, pas comme un bug.
- **E** — l'étudiant sait expliquer *pourquoi* on moyenne sur un tour (§5), pas seulement qu'on le fait.
