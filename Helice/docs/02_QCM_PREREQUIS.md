# QCM de positionnement — TD Hélice marine en eau libre (OpenFOAM)

> **Ce n'est pas une note.** C'est un auto-diagnostic : savez-vous ce qu'il faut savoir
> *avant* de lancer le TD ? Répondez sans support, puis vérifiez avec `08_CORRIGE_QCM.md`.
> Durée conseillée : 10 min. Une seule réponse par question.

---

## 1. Rappels utiles avant de commencer

- Hélice en eau libre : poussée $T$, couple $Q$, vitesse d'avance $V_a$, rotation $n$ (tr/s), diamètre $D$.
- Coefficient d'avance : $J = \dfrac{V_a}{nD}$
- Coefficients adimensionnés :
$$K_T = \frac{T}{\rho\,n^2 D^4} \qquad K_Q = \frac{Q}{\rho\,n^2 D^5} \qquad \eta_0 = \frac{J}{2\pi}\,\frac{K_T}{K_Q}$$
- Reynolds : $Re = \dfrac{U L}{\nu}$, avec $\nu$ la viscosité cinématique ($\nu_{eau} \approx 10^{-6}$ m²/s).
- RANS (Reynolds-Averaged Navier-Stokes) : on résout l'écoulement **moyenné** ; l'effet des
  fluctuations turbulentes est **modélisé** par un modèle de fermeture (k-ε, k-ω SST…).

---

## 2. QCM

### Q1. Le coefficient d'avance $J = V_a/(nD)$ est :
A. Une vitesse, en m/s
B. Un nombre sans dimension
C. Un débit
D. Une puissance

### Q2. À poussée $T$ donnée, si on double la vitesse de rotation $n$, le coefficient $K_T = T/(\rho n^2 D^4)$ :
A. double
B. est divisé par 2
C. est divisé par 4
D. ne change pas

### Q3. Le rendement en eau libre $\eta_0$ d'une hélice représente :
A. le rapport puissance utile (poussée × vitesse d'avance) sur puissance absorbée à l'arbre (couple × vitesse angulaire)
B. le rapport du couple sur la poussée
C. le rendement du moteur
D. toujours une valeur supérieure à 1

### Q4. Le nombre de Reynolds d'une hélice marine réelle en fonctionnement est :
A. de l'ordre de 1 (écoulement rampant)
B. de l'ordre de 100
C. très grand ($>10^5$) — écoulement turbulent
D. négatif

### Q5. Un « modèle de turbulence » dans un calcul RANS sert à :
A. accélérer l'ordinateur
B. représenter l'effet moyen des fluctuations turbulentes sur l'écoulement moyen (tenseur de Reynolds)
C. supprimer la viscosité
D. imposer les conditions aux limites

### Q6. Un calcul « **laminaire** » (aucun modèle de turbulence) sur une hélice marine réelle est :
A. la référence la plus fidèle
B. physiquement discutable (le Reynolds réel est bien au-delà de la transition), mais utile comme point de comparaison
C. impossible à lancer
D. équivalent à un calcul k-ω SST

### Q7. Entre deux fermetures RANS, k-ε standard et k-ω SST, laquelle est réputée la plus fiable en proche paroi et en gradient de pression adverse (décollement) ?
A. k-ε standard
B. k-ω SST
C. elles sont strictement équivalentes
D. aucune des deux ne gère la paroi

### Q8. La poussée d'une hélice est majoritairement pilotée par :
A. le champ de pression sur les pales
B. uniquement le frottement visqueux
C. la température du fluide
D. la couleur des pales

### Q9. Dans un calcul instationnaire d'hélice en rotation, les efforts (donc $K_T$, $K_Q$) :
A. sont rigoureusement constants dès la première itération
B. oscillent au cours du tour — il faut moyenner sur au moins un tour complet
C. divergent toujours
D. ne peuvent pas être calculés

### Q10. Une simulation dont le log se termine par `End` est :
A. forcément validée
B. terminée, ce qui ne garantit ni la convergence ni la pertinence physique
C. forcément fausse
D. encore en cours

### Q11. Pour comparer équitablement deux modèles de turbulence sur ce cas, on garde identiques :
A. la géométrie, le maillage et les conditions aux limites U/p ; seule la fermeture change
B. rien, on change tout à chaque fois
C. uniquement la couleur des figures
D. le nombre de cœurs de calcul uniquement

### Q12. La commande qui charge l'environnement OpenFOAM 2412 dans le terminal est :
A. `python openfoam`
B. `source /usr/lib/openfoam/openfoam2412/etc/bashrc`
C. `apt install openfoam`
D. `cd openfoam`

---

## 3. Grille de réponses

Q1 ___  Q2 ___  Q3 ___  Q4 ___  Q5 ___  Q6 ___
Q7 ___  Q8 ___  Q9 ___  Q10 ___  Q11 ___  Q12 ___

## 4. Checkpoint

- **10/12 et plus** : pré-requis solides, démarrez.
- **7–9/12** : démarrez, mais relisez `03_BASE_THEORIQUE.md` §1 et §2 pendant que les calculs tournent.
- **6/12 ou moins** : revoyez la notion de coefficient adimensionné d'hélice (cours Performances
  navire) et la notion de modèle de turbulence RANS avant d'attaquer l'analyse.
