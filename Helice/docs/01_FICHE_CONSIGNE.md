# Fiche consigne — TD Hélice marine en eau libre (FON-S7)

> **Aujourd'hui et à la séance 2 : un tableur suffit.** Les données sont trois fichiers CSV de
> moins de 500 Ko au total. Pas d'OpenFOAM, pas de ParaView, pas de ligne de commande. ParaView
> servira à la séance 3 — son installation est le travail de l'inter-séance B, et la salle C009
> est là si votre machine ne suit pas.

**Volume : 3 séances de 2 h (6 h)** — bloc « Mécanique des fluides » du référentiel FON-S7
(TD 6 h). Le bloc « Hydrodynamique » (houle, tenue à la mer) n'est pas traité ici.

**Binômes.** Travail en autonomie entre les séances — c'est là que se fait le travail personnel.

## Ce que couvre le TD (référentiel FON-S7)

- **Portance et traînée d'une pale d'hélice marine** — séance 1-B (doc [`11`](11_PORTANCE_TRAINEE_PALE.md)) :
  décomposition du torseur des efforts, passage à la portance/traînée d'une section, triangle des
  vitesses.
- **Différence des résultats selon le modèle de turbulence** — séance 2 : non pas « classer les
  modèles » mais **savoir quand une différence n'en est pas une** (transitoire, maillage de paroi, pas de
  temps : d'autres sources d'écart peuvent peser autant que le choix de la fermeture).
- **Lecture critique d'un résultat de simulation** — séances 1 et 3 : distinguer le signal physique
  du bruit numérique, relier une image de champ à un chiffre.

## Parti pris

**Le calcul est un fait acquis, pas un travail.** Les 3 cas OpenFOAM (hélice en eau libre, tutoriel
officiel `propeller`, solveur `pimpleFoam` instationnaire, interface AMI rotor/stator, 3 fermetures
de turbulence sur géométrie/maillage/CL **identiques**) ont déjà tourné. Un cas coûte ~2 h sur
4 cœurs et 12–14 Go : impossible à lancer en séance à 12 binômes. **Les résultats sont fournis.**

| Cas | Fermeture | $K_T$ | $10\,K_Q$ | $\eta_0$ |
|---|---|---|---|---|
| `case_kEpsilon` | RANS k-ε standard | 0,363 | 1,055 | 0,560 |
| `case_kOmegaSST` | RANS k-ω SST | 0,371 | 1,026 | 0,590 |
| `case_laminar` | aucune (laminaire) | 0,378 | 1,020 | 0,603 |

(moyennes sur le dernier tour complet, $J \approx 1{,}02$, $n = 25{,}15$ tr/s, $D = 0{,}2$ m)

> **Base théorique.** Le doc [`03`](03_BASE_THEORIQUE.md) est volontairement court : le TD s'adosse
> au cours de **mécanique des fluides**, en reconstruction. Les liens vers le cours de l'an dernier
> sont maintenus en attendant ; les prérequis seront revus à la reconstruction du cours.

---

## Séance 1 (2 h) — Lire un résultat

### A. « Quelle est la valeur de $K_T$ ? » (1 h)

On distribue **deux** séries temporelles pour cette question — `perf_kEpsilon.csv` et
`perf_laminar.csv` (kit `data/`) — **sans cours préalable**. `perf_kOmegaSST.csv` rejoint le kit à
la séance 2 : sa fenêtre « dernier tour » est trop courte pour une mesure de fréquence fiable
(incident de calcul du 05/09, diagnostiqué le 06/09 ; ses moyennes $K_T$/$K_Q$/$\eta_0$, elles, restent
valides). Vous lirez d'abord le dernier instant ; le tracé vous montrera que ça **oscille**.
À vous de trouver qu'il faut **moyenner**, et **sur quelle fenêtre**.

Puis la question qui fait la séance :

> L'hélice a **4 pales** et tourne à 25,15 tr/s.
> **a)** À quelle fréquence la poussée devrait-elle osciller ? Justifiez.
> **b)** Mesurez la fréquence dominante réellement présente dans les données.
> **c)** Un mécanisme sans aucun rapport avec les pales prédit exactement la même fréquence.
> Lequel ? Proposez un test qui séparerait les deux causes.

Zéro manipulation logicielle : du raisonnement, et une compétence d'ingénieur — **distinguer le
signal physique du bruit de son propre calcul**.

### B. Du torseur à la pale (1 h) — sur papier

Décomposition axiale / tangentielle des efforts fournis, passage à la **portance** et à la
**traînée** d'une section de pale, **triangle des vitesses**. On raccroche explicitement au profil
d'aile du cours de méca flux. Support : doc [`11`](11_PORTANCE_TRAINEE_PALE.md).

> **Inter-séance A** (~1 h) — chaque binôme reçoit **une** fermeture et caractérise son cas seul
> (moyennes, amplitudes, allure de la courbe), puis termine la décomposition des efforts commencée
> en 1-B.

---

## Séance 2 (2 h) — Confronter

### A. Retour des trois fermetures (30 min)

Chaque groupe pose ses chiffres au tableau. On reconstitue le tableau comparatif en direct.

### B. Le classement impossible (1 h 30) — cœur du TD

Vous allez vouloir classer les modèles. Vous devez découvrir que, sur le dernier tour d'un calcul de
4 tours (régime établi) :

| | valeur |
|---|---|
| écart entre les 3 fermetures | $\Delta K_T \approx 0{,}0096$ (4,3 %) |
| amplitude de l'oscillation | 0,0039 à 0,0048 — l'écart est **2 à 2,5 fois plus grand** |
| origine de cette oscillation | **indéterminée** entre passage de pale et interface numérique — les deux prédisent la même fréquence |

À 1,5 tour, sur la fenêtre qu'on croyait « le dernier tour », c'était l'inverse (oscillation 0,017 à 0,024,
plus grande que l'écart) : cette fenêtre recouvrait la mise en régime. **Un écart entre modèles ne se lit
qu'en régime établi, et une fois les autres incertitudes bornées** — par exemple, sur le couple, changer le
maillage de paroi déplace $10\,K_Q$ de +4,2 % sur un cas test (couches de prismes sur 63 % seulement de la surface de pale), contre 3,1 % entre les trois modèles (résultat
à confirmer, l'enseignant y reviendra). C'est la leçon du TD : elle est démontrée par vos
propres mesures, et elle vaut mieux qu'un classement.

> **Inter-séance B** — installation de **ParaView** (script de vérification, page « ça n'a pas
> marché », repli : un poste qui marche par binôme suffit). Chaque binôme prépare **une** question
> à poser aux images.

---

## Séance 3 (2 h) — Voir, puis conclure

### A. Session ParaView guidée (1 h 15)

Jeu de données allégé (`data/`, ~750 Mo), **une seule session collective**. Sillage, tourbillons de
bout de pale, critère $Q$. Objectif unique : **expliquer pourquoi le laminaire surestime $\eta_0$**
(pas de dissipation turbulente → moins de pertes de couple). On relie l'image au chiffre de la
séance 2. Support : doc [`05`](05_GUIDE_PARAVIEW.md).

### B. Restitution croisée (45 min)

Chaque binôme répond devant les autres à la question qu'il avait préparée sur les images.

---

## Moyens et évaluation

- **Calcul en séance : aucun.** Poste étudiant : un tableur (séances 1–2), ParaView en lecture
  seule (séance 3). Données fournies : < 1 Mo (séances 1–2), puis ~750 Mo (séance 3).
- **QCM** : [`02`](02_QCM_PREREQUIS.md) en début de séance 1.
- **Rendu de binôme** : la caractérisation de fermeture (inter-séance A), la décomposition d'efforts
  (1-B + inter-séance A), et une demi-page sur « le classement impossible » (séance 2).

## Checkpoints enseignant

- **Séance 1** — le binôme trouve seul qu'il faut moyenner sur un tour ; répond correctement au a)
  (passage de pale = $4n$) ; mesure le 1× dans les données ; nomme au c) le mécanisme concurrent
  (interface AMI sur maillage de fond) et propose un test qui le séparerait du passage de pale.
- **Inter-séance A** — chaque binôme a produit moyenne + amplitude + tracé pour sa fermeture.
- **Séance 2** — le binôme met **côte à côte** l'écart-entre-modèles et l'amplitude, et en tire que
  le classement n'est pas défendable en l'état.
- **Séance 3** — le laminaire est interprété comme un **cas dégradé assumé** (Reynolds hélice réel
  ≫ régime laminaire), relié à l'image (sillage, dissipation), pas comme une erreur de calcul.

