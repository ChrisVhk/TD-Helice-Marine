# Corrigé QCM — prérequis et final (côté enseignant)

Barème conseillé : 1 point par question. Bonus possible +1 pour deux justifications
scientifiques claires au choix.

---

## 1. QCM prérequis (`02_QCM_PREREQUIS.md`)

| Q | Rép. | Justification courte |
|---|---|---|
| 1 | **B** | $J = V_a/(nD)$ : [m/s] / ([1/s]·[m]) → sans dimension. |
| 2 | **C** | $K_T = T/(\rho n^2 D^4)$ ; à $T$ fixé, $n \to 2n$ ⇒ $K_T$ divisé par $4$. |
| 3 | **A** | $\eta_0 = \dfrac{T V_a}{2\pi n Q}$ = puissance utile / puissance à l'arbre. |
| 4 | **C** | $Re \sim 10^6$ pour une hélice marine réelle → turbulent. |
| 5 | **B** | Le modèle ferme le tenseur de Reynolds (effet moyen des fluctuations). |
| 6 | **B** | Physiquement discutable ($Re$ ≫ transition) mais utile comme borne / cas de comparaison. |
| 7 | **B** | k-ω SST : formulation $\omega$ en proche paroi + SST pour le gradient de pression adverse. |
| 8 | **A** | La poussée vient d'abord de la distribution de pression sur les pales. |
| 9 | **B** | Efforts instationnaires → oscillation au cours du tour (fréquence de rotation de l'arbre sur ce cas, pas le passage de pale) → moyenne sur ≥ 1 tour. |
| 10 | **B** | `End` = calcul terminé ; ne dit rien de la convergence ni de la physique. |
| 11 | **A** | Comparaison équitable : géométrie + maillage + CL U/p identiques, seule la fermeture change. |
| 12 | **B** | `source /usr/lib/openfoam/openfoam2412/etc/bashrc`. |

**Lecture des scores** : ≥ 10/12 acquis solides ; 7–9 démarrage possible avec relecture §1–§2 de la
base théorique ; ≤ 6 revoir coefficients d'hélice + notion de fermeture RANS avant l'analyse.

---

## 2. QCM final (`06_QCM_FINAL.md`)

| Q | Rép. | Justification courte |
|---|---|---|
| 1 | **C** | $K_Q$ (couple) est le plus sensible à la fermeture. |
| 2 | **A** | Poussée ↔ pression (robuste) ; couple ↔ frottement pariétal + sillage proche (sensible). |
| 3 | **B** | Cas dégradé assumé : sans modèle, pas d'épaississement ni de décollement corrects de la couche limite. |
| 4 | **B** | Meilleur comportement proche paroi et en gradient de pression adverse. |
| 5 | **B** | Oscillation au cours du tour (fréquence de rotation) → moyenne sur le dernier tour complet. |
| 6 | **A** | $T = 1/n = 1/25{,}15 \approx 0{,}0398$ s. |
| 7 | **A** | $0{,}06 / 0{,}0398 \approx 1{,}5$ tour. |
| 8 | **B** | Moyenne partielle : à ne pas exploiter telle quelle. |
| 9 | **B** | `URef` est échantillonné en amont ; l'écoulement amont dépend un peu de la fermeture. |
| 10 | **B** | `10*KQ` = $K_Q \times 10$ ; diviser par 10. |
| 11 | **A** | $J = 5 / (25{,}15 \times 0{,}2) = 5 / 5{,}03 \approx 0{,}99$. |
| 12 | **A** | $\eta_0 = \dfrac{1{,}02}{2\pi}\cdot\dfrac{0{,}37}{0{,}106} = 0{,}162 \times 3{,}49 \approx 0{,}57$. |

**Lecture des scores** : ≥ 10/12 objectifs atteints ; 7–9 revoir la moyenne sur un tour (§5 guide) ;
≤ 6 reprendre $K_T$ vs $K_Q$ et le statut du cas laminaire avec l'enseignant.

---

## 3. Remédiation rapide (5 min)

- Rappeler la définition de $\eta_0$ (rapport de puissances) et refaire le calcul Q12 au tableau.
- Rejouer la figure `comparaison_performance.png` : montrer l'oscillation, tracer la fenêtre « dernier tour ».
- Reformuler « laminaire = dégradé assumé », pas « calcul raté ».
