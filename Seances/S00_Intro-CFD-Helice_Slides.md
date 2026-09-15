# Introduction CFD Hélice — source des diapositives

Une diapo = un bloc `## Diapo <N> — <titre>`, se termine à `---`. Champs : voir
`_Setup/NOTE_GABARIT_PPTX.md`. Matière fournie par
`/mnt/d/kdrive/ENSEIGNEMENT/2026-09-14_CONSIGNE-ACTIVE_Deck-intro-et-rescale-D.md` §3.

**Deck générique, réutilisable en Informatique-Appliquee-S5 comme en FON-S7** — introduction
au calcul d'écoulement autour d'une hélice, indépendant d'une séance particulière.

**Conformité au gabarit (LOT C, 14/09) — divergences trouvées et corrigées par rapport à la
source fournie dans la consigne, qui suivait une convention supposée, pas la convention réelle
du dépôt (vérifiée sur `Seances/S02_Slides.md`, `_Setup/NOTE_GABARIT_PPTX.md` et
`_Setup/MODELE_generer_pptx_seance.py`) :**
- Disposition `Titre` → **n'existe pas** dans le gabarit (quatorze dispositions nommées
  exactement : voir `NOTE_GABARIT_PPTX.md`). Remplacée par `Couverture` (TITLE + BODY
  sous-titre), l'équivalent le plus proche — c'est celle qu'utilise déjà `S02_Slides.md` pour
  sa propre diapo d'ouverture.
- Disposition `Image pleine` → **n'existe pas**. Remplacée par `Figure` (TITLE ligne de sens +
  PICTURE + BODY crédit optionnel).
- Disposition `Deux images` → **n'existe pas**. Remplacée par `DeuxFigures` (TITLE + PICTURE +
  PICTURE + BODY crédits optionnels).
- Disposition `Corps` → existe telle quelle, aucun changement.
- Champ `**Image** :` / `**Image gauche/droite** :` → **n'existe pas** ; le parseur
  (`FIELD_NAMES` dans `MODELE_generer_pptx_seance.py`) n'attend qu'un seul champ
  `**Figure(s)** :`, un chemin par ligne, chacun entre backticks. Pour `DeuxFigures`, les deux
  chemins vont dans CE MÊME champ, dans l'ordre gauche puis droite (ordre des placeholders
  PICTURE 10 puis 11 du gabarit).
- Diapos 2 à 8 de la source fournie n'avaient **aucun champ `**Contenu affiché** :`** — or
  `Figure`/`DeuxFigures` exigent une ligne de sens en TITLE (`body_lines[0]`, sinon le titre
  reste le texte d'invite vide du gabarit). Une ligne courte a été dérivée du titre de chaque
  diapo de la source et ajoutée ici.
- Diapos 9 et 10 (Corps) avaient leurs puces/citation directement après `**Disposition** :`,
  **sans `**Contenu affiché** :`** — le parseur les aurait alors rattachées au champ
  `Disposition` (dernier champ vu), cassant la valeur de disposition elle-même. Champ ajouté,
  avec une ligne de titre dérivée en première ligne (exigence du même piège de rédaction que
  documenté dans `MODELE_generer_pptx_seance.py`, LOT G+H).
- **Chemin des images** : la source de la consigne écrivait `Images/galerie/....png`. Le
  générateur résout `Images/...` comme sibling de `Seances/` (racine du dépôt) — or la galerie
  réelle de ce dépôt vit sous `Helice/Images/galerie/`, pas `Images/galerie/` à la racine
  (structure propre à `TD-Helice-Marine`, différente d'un dépôt de cours autonome). Chemins
  corrigés en `Helice/Images/galerie/....png` ; en conséquence le générateur
  (`Seances/generer_pptx_seance.py`, unifié le 15/09 — LOT 4, remplace l'ancien
  `generer_pptx_S00.py` propre à ce deck) élargit la regex d'extraction (qui n'acceptait
  qu'un chemin commençant littéralement par `Images/`) pour accepter aussi ce préfixe
  `Helice/` — pour les trois séances désormais, pas seulement celle-ci.
- Numérotation des diapos : la source de la consigne commençait à 1 ; renumérotée à partir de
  0 pour suivre la convention réelle (`S02_Slides.md` : `Diapo 0 — Couverture`).
- Champ `Segment / timing` : aucune durée n'était donnée dans la source fournie — laissé vide
  plutôt qu'inventé (ce deck n'est pas découpé en séance/segments comme `S02_Slides.md`, c'est
  une introduction générique).

---

## Diapo 0 — Titre
**Disposition** : Couverture

**Contenu affiché** :
Ce qu'on calcule, et ce qu'on croit voir
Introduction au calcul d'écoulement autour d'une hélice

**Notes d'orateur** :
Deck générique d'introduction, réutilisable en Informatique-Appliquée-S5 comme en FON-S7 —
indépendant d'une séance particulière du TD Hélice.

---

## Diapo 1 — L'objet
**Disposition** : Figure

**Contenu affiché** :
L'objet

**Figure(s)** :
`Helice/Images/galerie/01_geometrie.png`

**Notes d'orateur** :
Quatre pales. C'est vérifiable à l'œil, et c'est le premier réflexe : compter avant de
croire. La documentation de ce cas en annonçait trois — pendant des semaines.

---

## Diapo 2 — On ne calcule pas une hélice
**Disposition** : Figure

**Contenu affiché** :
On ne calcule pas une hélice

**Figure(s)** :
`Helice/Images/galerie/02_geometrie_domaine.png`

**Notes d'orateur** :
On calcule un volume de fluide autour d'elle. L'hélice n'est qu'une frontière. Tout ce
qui suit — taille du domaine, position de l'entrée et de la sortie — est un choix, et
chaque choix se paie.

---

## Diapo 3 — Discrétiser
**Disposition** : Figure

**Contenu affiché** :
Discrétiser

**Figure(s)** :
`Helice/Images/galerie/03_maillage_coupe.png`

**Notes d'orateur** :
Fin près de la pale, grossier au loin. Le maillage n'est pas un décor : c'est là que se
décide ce que le calcul peut voir, et ce qu'il coûte. 600 000 cellules ici.

---

## Diapo 4 — La paroi
**Disposition** : Figure

**Contenu affiché** :
La paroi

**Figure(s)** :
`Helice/Images/galerie/06_couches_prismes.png`

**Notes d'orateur** :
Les couches de prismes servent à résoudre la couche limite. On en demande six, on en
obtient nettement moins sur le bout de pale (chiffre exact, sourcé fichier+ligne :
`Helice/docs/PARAMETRES_CAS.md`). Un maillage ne se déclare pas, il se négocie.

---

## Diapo 5 — Deux maillages qui glissent
**Disposition** : Figure

**Contenu affiché** :
Deux maillages qui glissent

**Figure(s)** :
`Helice/Images/galerie/04_interface_AMI.png`

**Notes d'orateur** :
Le rotor tourne dans un fond fixe. À l'interface, le solveur interpole les flux. Retenir
ceci pour plus tard : une interface qui tourne dans un fond cartésien retrouve la même
configuration quatre fois par tour.

---

## Diapo 6 — La poussée vient de la pression
**Disposition** : Figure

**Contenu affiché** :
La poussée vient de la pression

**Figure(s)** :
`Helice/Images/galerie/05_pression_pales.png`

**Notes d'orateur** :
Les deux faces de la pale ne portent pas la même pression. C'est de cette différence,
intégrée sur la surface, que naît la poussée — pas d'un effet de vis.

---

## Diapo 7 — Le sillage, et où naît la turbulence
**Disposition** : DeuxFigures

**Contenu affiché** :
Le sillage, et où naît la turbulence

**Figure(s)** :
`Helice/Images/galerie/07_vitesse.png`
`Helice/Images/galerie/08_turbulence.png`

**Notes d'orateur** :
À gauche l'accélération aux bouts de pale et le sillage. À droite l'énergie turbulente :
elle est produite au bout de pale, un ordre de grandeur au-dessus du niveau ambiant.
En échelle linéaire cette image est un rectangle noir — un champ étalé sur des décades ne
se montre jamais en linéaire.

---

## Diapo 8 — Ce que ces images ne disent pas
**Disposition** : Corps

**Contenu affiché** :
Ce que ces images ne disent pas
- Elles sont belles. Elles ne sont pas une validation.
- y⁺ mesuré sur ce cas : 83,7 % de la surface dans la plage de la loi de paroi.
- Reste 16 % hors plage — dont le bout de pale, à y⁺ = 1043.
- Le diamètre utilisé dans les coefficients était faux de 14 %.
- L'origine de l'oscillation de poussée n'est toujours pas établie.

**Notes d'orateur** :
Une belle image est un argument d'autorité. C'est exactement ce contre quoi ce TD veut
vous armer.
Les quatre réserves ci-dessus renvoient chacune à `Helice/docs/ETAT-DES-LIEUX.md` (LOT 7,
14/09) : (1) rappel de méthode, pas de ligne dédiée ; (2) ÉTABLI « y+ (SANS couches),
propellerTip 83,7 % dans [30;300] » ; (3) ÉTABLI « D = 0,227378 m », qui a remplacé les
0,2 m codés en dur ; (4) INCERTAIN « origine de la raie à 4× », toujours ouvert.

---

## Diapo 9 — La question de la prochaine séance
**Disposition** : Corps

**Contenu affiché** :
La question de la prochaine séance
Voici un objet dont tout est connu depuis un siècle.
Nous avons eu quatre nombres faux : le nombre de pales, le diamètre, la masse
volumique de référence, et l'origine d'une raie spectrale.
Pourquoi ?

**Notes d'orateur** :
La réponse n'est pas de l'hydrodynamique. Des constantes héritées jamais mesurées ; des
noms de fichiers pris pour des données ; une vérification qui ne pouvait pas échouer ;
un adimensionnement qui amplifie l'erreur ; un cas de démonstration réemployé comme
instrument de mesure.
