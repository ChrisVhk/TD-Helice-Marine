# Séance 1-B — Du torseur de l'hélice à la portance et la traînée d'une pale

> **1 h sur papier**, finie en inter-séance A. Aucune manipulation logicielle.
> Prérequis : le profil d'aile du cours de mécanique des fluides ($C_l$, $C_d$, incidence,
> décrochage, finesse $C_l/C_d$). Ici, la seule nouveauté est que la section **tourne**.

Le calcul OpenFOAM ne produit que **quatre nombres pour l'hélice entière** : $K_T$, $K_Q$, $J$,
$\eta_0$ (poussée et couple globaux). Le référentiel demande de savoir remonter de là à la
**portance et la traînée d'une section de pale**. C'est de la théorie de l'élément de pale
(*blade element theory*) : on découpe la pale en tranches et on traite chaque tranche comme un
profil d'aile 2D.

---

## 1. Ce que voit une section de pale

Prenons une section à la distance $r$ de l'axe. Elle est balayée par deux écoulements :

| | vitesse vue par la section | origine |
|---|---|---|
| **axiale** | $V_a$ (≈ vitesse d'avance) | l'hélice avance dans l'eau |
| **tangentielle** | $\Omega r = 2\pi n\, r$ | l'hélice tourne ($n = 25{,}15$ tr/s) |

La **vitesse relative** $W$ vue par la section est la somme vectorielle des deux. Elle fait avec le
plan de rotation l'angle **$\varphi$** (angle d'avance hydrodynamique) :

$$\tan\varphi = \frac{V_a}{2\pi n\, r}, \qquad W = \sqrt{V_a^{\,2} + (2\pi n\, r)^2}$$

```
        plan de rotation
   ─────────────────────────────►  Ω r  (tangentiel)
   │\                    φ = angle d'avance hydrodynamique
   │ \                   β = angle de calage géométrique de la section
   │  \  W               α = β − φ  = incidence vue par le profil
 Va│   \
   │    \
   ▼     ◄ W (vitesse relative, la section « croit » avancer dans cette direction)
```

L'incidence du profil est $\alpha = \beta - \varphi$, où $\beta$ est le calage géométrique de la
section (donné par la géométrie de la pale). **C'est exactement l'incidence d'une aile** — sauf
qu'ici $\varphi$ change le long de la pale (près du moyeu $\Omega r$ est petit, $\varphi$ grand ;
en bout de pale l'inverse).

---

## 2. Portance et traînée de la section

La section se comporte comme un profil 2D dans l'écoulement $W$ :

$$\mathrm{d}L = \tfrac{1}{2}\rho\, W^2\, c\, C_l(\alpha)\, \mathrm{d}r \quad (\perp W), \qquad
  \mathrm{d}D = \tfrac{1}{2}\rho\, W^2\, c\, C_d(\alpha)\, \mathrm{d}r \quad (\parallel W)$$

$c$ = corde de la section. $C_l$, $C_d$ sont les **mêmes coefficients qu'en cours de méca flux**
(courbe $C_l(\alpha)$ linéaire puis décrochage, $C_d$ minimale près de l'incidence de portance
nulle).

### Projection sur les axes de l'hélice

$L$ est $\perp W$ et $D$ est $\parallel W$ : on les projette sur l'axe (poussée) et sur la
tangente (couple) en tournant de $\varphi$ :

$$\boxed{\ \mathrm{d}T = \mathrm{d}L\,\cos\varphi \;-\; \mathrm{d}D\,\sin\varphi\ }
\qquad
\boxed{\ \mathrm{d}F_\theta = \mathrm{d}L\,\sin\varphi \;+\; \mathrm{d}D\,\cos\varphi\ }$$

$$\mathrm{d}Q = r\,\mathrm{d}F_\theta$$

La poussée totale et le couple total s'obtiennent en intégrant du moyeu ($r_h$) au bout ($R$) et
en multipliant par le nombre de pales $Z = 3$ :

$$T = Z\!\int_{r_h}^{R}\!\mathrm{d}T, \qquad Q = Z\!\int_{r_h}^{R}\! r\,\mathrm{d}F_\theta$$

---

## 3. Pourquoi c'est **la** clé du TD

Le rendement d'une **section** s'écrit (rapport puissance utile / puissance fournie) :

$$\eta_{\text{section}} = \frac{V_a\,\mathrm{d}T}{\Omega r\,\mathrm{d}F_\theta}
= \frac{\tan\varphi}{\tan(\varphi + \gamma)}, \qquad \text{où}\quad \tan\gamma = \frac{\mathrm{d}D}{\mathrm{d}L} = \frac{C_d}{C_l}$$

Lisez cette formule :

- **La poussée** $\mathrm{d}T \approx \mathrm{d}L\cos\varphi$ : portée par la **portance**, donc par
  la pression sur le profil. Peu sensible au modèle de turbulence.
- **Le couple** $\mathrm{d}F_\theta$ et le **rendement** dépendent de $\gamma$, donc de
  $C_d/C_l$ : la **traînée** de section, c'est-à-dire le **frottement pariétal** que le modèle de
  turbulence pilote directement.

C'est la même hiérarchie que celle mesurée sur les 3 cas : $K_T$ resserré (0,363–0,378), $\eta_0$
et $K_Q$ dispersés. Le TD la fait retrouver *par le calcul global* en séance 2 ; ici on montre
*d'où elle vient* à l'échelle de la section.

---

## 4. Exercice — section de référence $r/R = 0{,}7$

Données : $R = 0{,}1$ m, $n = 25{,}15$ tr/s, $V_a \approx 5{,}1$ m/s (≈ `URef` du calcul,
$J \approx 1{,}02$), $Z = 3$.

1. Calculez $\Omega r$, puis $\varphi$ et $W$ à $r/R = 0{,}7$.
2. La courbe $C_l(\alpha)$ d'un profil mince donne $C_l \approx 2\pi\,\alpha$ (α en rad) tant qu'on
   ne décroche pas. Si la section est calée à $\beta = 40°$, quelle incidence $\alpha$ ? Quel $C_l$ ?
3. Avec $c = 0{,}025$ m et $\rho_{\text{ref}} = 1{,}2$ (voir encadré), estimez $\mathrm{d}L/\mathrm{d}r$.
4. En prenant une finesse réaliste $C_l/C_d = 40$, calculez $\gamma$ puis $\eta_{\text{section}}$.
   Comparez à $\eta_0 = 0{,}59$ mesuré sur l'hélice entière. Commentez l'écart (induction,
   sections non optimales près du moyeu, pertes de bout de pale).

*(Réponses détaillées : doc [`10`](10_CORRIGE_ETUDIANT_DETAILLE.md), non distribué.)*

> ### ⚠ Encadré — quelle masse volumique ?
> Le calcul du dépôt utilise $\rho_{\text{ref}} = 1{,}2$ kg/m³ (valeur héritée du tutoriel
> générique OpenFOAM — c'est de l'**air**). Les coefficients $K_T$, $K_Q$, $\eta_0$ sont des
> rapports **sans dimension** : $\rho$ s'y simplifie, **les valeurs du tableau restent justes**.
> Mais si vous reconstruisez une **force en newtons**, utilisez $\rho_{\text{ref}} = 1{,}2$
> **partout** (c'est la valeur qu'a utilisée `propellerInfo`). Pour une poussée physique en eau de
> mer, multipliez le résultat par $1025/1{,}2$.
>
> **Piège concret** : le fichier `postProcessing/forces/…/force.dat` est écrit avec
> $\rho_{\text{ref}} = 1$ (réglage `system/forces`), pas $1{,}2$. Une poussée sommée depuis
> `force.dat` sera donc **20 % plus faible** que celle cohérente avec `propellerInfo`. Ce n'est
> pas une erreur de calcul : c'est une incohérence de réglage entre deux *function objects* du même
> cas. Travaillez à partir des coefficients, ou fixez $\rho$ vous-mêmes.

---

## 5. Fin en inter-séance A

Terminez la décomposition pour **une deuxième section** ($r/R = 0{,}4$) et comparez $\varphi$,
$\alpha$, $\eta_{\text{section}}$ entre les deux rayons. Rendez une demi-page : le triangle des
vitesses aux deux rayons, et une phrase sur pourquoi la pale est **vrillée** (calage $\beta$
décroissant du moyeu au bout).
