# QCM final — TD Hélice marine en eau libre

> À faire en fin de séance, après l'analyse quantitative. 15 min, une réponse par question.
> Corrigé : `08_CORRIGE_QCM.md`. Les questions 11 et 12 demandent un **calcul chiffré**.

---

## Q1. Sur ce cas, quel coefficient est le plus dispersé entre les 3 fermetures de turbulence ?
A. $J$ (fixé par les conditions aux limites)
B. $K_T$
C. $K_Q$ (donc $10\,K_Q$)
D. aucun, ils sont identiques

## Q2. Physiquement, cette dispersion s'explique parce que :
A. la poussée dépend surtout de la pression (peu sensible à la fermeture), le couple du frottement pariétal et du sillage proche (très sensible)
B. le couple ne dépend d'aucun phénomène visqueux
C. le maillage change d'un cas à l'autre
D. le solveur n'est pas le même

## Q3. Le cas laminaire, à ce nombre de Reynolds ($\sim 10^6$) :
A. est la référence physique
B. est un cas volontairement dégradé : sans modèle, la couche limite ne s'épaissit ni ne décolle correctement
C. ne converge jamais
D. donne exactement le résultat k-ω SST

## Q4. k-ω SST est généralement préféré à k-ε standard pour une hélice parce qu'il :
A. est plus rapide à calculer
B. se comporte mieux en proche paroi et en gradient de pression adverse (décollement)
C. n'a pas besoin de maillage
D. supprime la turbulence

## Q5. Les coefficients $K_T$ et $K_Q$ au cours du calcul :
A. sont constants dès le premier pas de temps
B. oscillent au cours du tour ; on moyenne sur le dernier tour complet
C. divergent toujours
D. ne peuvent pas être calculés en instationnaire

## Q6. La période de rotation de cette hélice ($n = 25{,}15$ tr/s) vaut environ :
A. 0,0398 s
B. 0,398 s
C. 25,15 s
D. 2,515 s

## Q7. Le calcul s'arrête à $t = 0{,}06$ s. Cela représente :
A. environ 1,5 tour d'hélice
B. environ 15 tours
C. exactement 1 tour
D. moins d'un dixième de tour

## Q8. Un drapeau `⚠ < 1 tour écoulé` dans le tableau de post-traitement signifie :
A. le calcul a divergé
B. la moyenne est partielle et ne doit pas être exploitée telle quelle
C. le maillage est faux
D. ParaView n'est pas installé

## Q9. `URef` (donc $J$) diffère légèrement d'un cas à l'autre parce que :
A. on a changé la vitesse d'entrée entre les cas
B. `URef` est échantillonné dans l'écoulement en amont, qui dépend un peu de la fermeture
C. c'est une erreur du function object
D. le diamètre de l'hélice change

## Q10. La colonne `10*KQ` du fichier `propellerPerformance.dat` :
A. est déjà la valeur physique de $K_Q$
B. est $K_Q$ multiplié par 10 : diviser par 10 pour la valeur physique
C. est le rendement
D. est le couple en N·m

## Q11. (calcul) Vitesse d'avance $V_a = 5$ m/s, $n = 25{,}15$ tr/s, $D = 0{,}2$ m. Le coefficient d'avance nominal $J = V_a/(nD)$ vaut environ :
A. 0,99
B. 1,99
C. 0,50
D. 5,03

## Q12. (calcul) Un cas donne $K_T = 0{,}37$ et $10\,K_Q = 1{,}06$ à $J = 1{,}02$. Le rendement $\eta_0 = \dfrac{J}{2\pi}\dfrac{K_T}{K_Q}$ vaut environ :
A. 0,57
B. 0,37
C. 1,02
D. 0,06

---

## Grille de réponses

Q1 ___  Q2 ___  Q3 ___  Q4 ___  Q5 ___  Q6 ___
Q7 ___  Q8 ___  Q9 ___  Q10 ___  Q11 ___  Q12 ___

## Checkpoint

- **10/12 et plus** : objectifs du TD atteints.
- **7–9/12** : revoir §5 du guide pas-à-pas (moyenne sur un tour) et §3 de la base théorique.
- **≤ 6/12** : reprendre l'interprétation $K_T$ vs $K_Q$ et le statut du cas laminaire avec l'enseignant.
