<!-- destinations: github -->
# Fiche 18 — ParaView en autonomie : laminaire vs turbulent

> Travail **autonome**, hors séance (chez vous ou en salle C09), **par binôme**. Cette fiche se
> suffit à elle-même : chaque clic est décrit, une page « ça ne marche pas » est fournie en fin
> de fiche. Elle ne donne **aucune réponse** — les trois questions qui closent chaque vue sont
> pour vous, pas pour nous.

**Durée visée** : environ 2 h 10 pour les parties 0, A, B et la synthèse (partie C en bonus,
20–25 min de plus). Voir le détail par partie ci-dessous — ces durées sont une estimation par
comptage des opérations, pas une moyenne mesurée sur des binômes réels : si vous êtes très en
dessous ou très au-dessus, ce n'est pas anormal en soi, mais notez l'écart.

---

## 0. Avant de commencer (≈ 15 min)

- **Poste installé** : suivez `ANNEXE_Installation-OpenFOAM-ParaView.md` si ce n'est pas déjà
  fait (script de vérification inclus, page « ça n'a pas marché »). Un poste qui marche par
  binôme suffit.
- **Récupérer et décomposer l'archive** : le pack ParaView vous est distribué à part du dépôt
  (voir `data/paraview_kit/README_KIT.md` pour le format et le contenu exact — ne le recopiez
  pas ici). Décompressez l'archive où vous voulez sur votre poste ; chaque dossier de cas
  contient déjà un fichier `<cas>.foam` (vide, c'est normal — c'est un point d'entrée pour
  ParaView, pas un fichier de données).
- **Ouvrir les trois fermetures dans UNE session ParaView** :
  ```bash
  paraview case_kEpsilon/case_kEpsilon.foam case_kOmegaSST/case_kOmegaSST.foam case_laminar/case_laminar.foam &
  ```
  Pour chacun des trois : dans *Properties*, cocher **Reconstructed Case** (le pack est déjà
  reconstruit, mais la case existe toujours dans l'interface), puis **Apply**.
- **Se placer à t = 0,158 s — SAISI au clavier, jamais le bouton ⏭.** Dans la barre
  d'animation, tapez `0.158` dans le champ *Time* et validez. **Piège à connaître avant de
  commencer** : sur `case_kOmegaSST` uniquement, le dernier pas du pack est **0,159**, pas
  0,158 (c'est la série de la partie B). Le bouton ⏭ (« dernier pas ») vous y amènerait
  directement — 9° de rotor d'écart avec les deux autres cas, assez pour que les vues ne se
  superposent plus. Toujours taper `0.158`, jamais cliquer ⏭, sur les trois fermetures.
- **Renommez chaque source** dans le *Pipeline Browser* (clic droit → *Rename*) en `kEpsilon`,
  `kOmegaSST`, `laminar` pour vous y retrouver.

**Question d'entrée (à répondre avant de continuer, pas d'image nécessaire)** : Pourquoi le
même instant (t = 0,158 s) donne-t-il le même angle de rotor dans les trois cas ? Qu'est-ce qui
deviendrait faux dans une comparaison d'images si ce n'était pas le cas ?

---

## Partie A — Socle : les trois fermetures à t = 0,158 s (≈ 1 h 20)

Pour chaque vue (V1 à V4), vous manipulez **les trois cas l'un après l'autre** avec les
**mêmes réglages imposés** ci-dessous (échelle, caméra), puis vous répondez aux trois questions
**une seule fois**, en comparant les trois images entre elles.

Convention de capture, pour les quatre vues : **File → Save Screenshot → 1920×1080, fond
blanc**, nommage exact `<vue>_<cas>_t0158.png` (ex. `V1_sillage_kEpsilon_t0158.png`).

### V1 — Sillage (vitesse dans un plan axial)

1. Sélectionnez la source `kEpsilon` → **Filters → Common → Slice**. *Slice Type* : **Plane**,
   *Normal* = `0 0 1`, *Origin* = `0 0 0`. **Apply**.
2. Sur ce Slice : **Filters → Alphabetical → Cell Data to Point Data**, **Apply**. (Sans ce
   filtre, ParaView affiche les données par maille en damier plat, pas en dégradé continu —
   `TUTORIEL_OpenFOAM-et-ParaView.md` §5, piège 3.)
3. *Coloring* : **U → Magnitude**. Clic droit sur la barre de couleurs → **Rescale to Custom
   Range** → entrez **0 à 10**. *Ne cliquez pas sur « Rescale to Data Range »* : le maximum réel
   dépasse 17 m/s (vitesse du bout de pale, ω·R), une seule petite zone qui écraserait tout le
   reste de l'image dans une seule teinte plate si vous l'utilisiez comme borne.
4. Caméra (menu *View → Camera → Adjust Camera*, ou taper directement les champs) :
   **Position (0 ; −0,300 ; 2,253)**, **Focal Point (0 ; −0,300 ; 0)**, **View Up (0 ; 1 ; 0)**,
   **View Angle 30°**.
5. Capture : `V1_sillage_<cas>_t0158.png`.

Répétez sur `kOmegaSST` et `laminar` (même Slice, mêmes réglages, seule la source change).

**Sur cette vue (les trois cas ensemble)** :
- Qu'observez-vous dans la forme et l'intensité du jet en aval de l'hélice, d'un cas à l'autre ?
- Qu'est-ce que ces trois images vous permettent de conclure sur l'effet du modèle de
  turbulence sur le sillage proche ?
- Qu'est-ce qu'elles ne vous permettent **pas** de conclure (pensez à l'avertissement du
  README_KIT sur un pas de temps unique) ?

### V2 — Viscosité turbulente (nut)

Vue que `05_GUIDE_PARAVIEW.md` n'avait pas.

1. Reprenez le même Slice (celui de V1) pour `kEpsilon`. *Coloring* : cherchez **nut** dans la
   liste. Cochez **Use Log Scale** (bouton dédié à côté de la barre de couleurs — sans lui,
   l'échelle linéaire écrase un champ qui varie sur 4 ordres de grandeur, `TUTORIEL` §5,
   piège 2). **Rescale to Custom Range** → **6e-7 à 9,1e-3**.
2. Caméra : identique à V1 (même Position/Focal/View Up/Angle).
3. Capture : `V2_nut_kEpsilon_t0158.png`.
4. Répétez sur `kOmegaSST`.
5. Sur `laminar` : ouvrez la liste *Coloring* du même Slice. **`nut` n'y figure pas** — normal,
   pas une panne : le calcul laminaire n'a pas de modèle de turbulence, donc pas de viscosité
   turbulente à afficher. Pas de capture pour ce cas sur cette vue ; notez-le tel quel dans
   votre planche.

**Sur cette vue (kEpsilon et kOmegaSST)** :
- Qu'observez-vous : où `nut` est-il grand, où est-il petit, par rapport à la forme du sillage
  vue en V1 ?
- **Sans le dire pour vous** : reliez les zones où `nut` est grand aux endroits où les vues V1 et
  V4 diffèrent (ou pas) entre `laminar` et les deux fermetures RANS. Qu'est-ce que ce
  rapprochement vous permet de conclure ?
- Qu'est-ce qu'il ne permet pas de conclure ?

### V3 — Pression sur la pale (deux caméras)

1. Sélectionnez la source `kEpsilon` (pas le Slice). Dans *Properties → Mesh Regions*, décochez
   `internalMesh` et tout ce qui n'est pas la pale ; cochez seulement `propellerTip`,
   `propellerStem1`, `propellerStem2`, `propellerStem3`. **Apply**.
2. **Filters → Alphabetical → Cell Data to Point Data**, **Apply**.
3. *Coloring* : **p**. **Rescale to Custom Range** → **−34 à 16**. (Ici aussi, le min/max brut du
   champ va de −111 à +99 — un pic très localisé au bord d'attaque — et écrase toute la pale en
   deux couleurs plates si vous l'utilisez ; −34/16 est la plage où 96 % des valeurs de la pale
   vivent réellement, sur les trois fermetures.)
4. **Caméra « aval » (face en pression, l'intrados — l'eau y est accélérée)** : Position
   (0 ; −0,696 ; 0), Focal Point (0 ; 0,070 ; 0), View Up (0 ; 0 ; 1), View Angle 30°. Capture :
   `V3_pression_aval_<cas>_t0158.png`.
5. **Caméra « amont » (face en dépression, l'extrados)** : mêmes Focal Point/View Up/Angle,
   **Position (0 ; 0,835 ; 0)**. Capture : `V3_pression_amont_<cas>_t0158.png`.

Répétez sur `kOmegaSST` et `laminar` (mêmes réglages).

**Sur cette vue (les trois cas, les deux caméras)** :
- Qu'observez-vous sur la répartition de la dépression (face amont) entre les trois cas ?
- Qu'est-ce que cela vous permet de conclure sur la charge portée par la pale selon le modèle ?
- Qu'est-ce que cela ne vous permet pas de conclure sur le couple ou la poussée globale (K_T,
  10K_Q) ?

### V4 — Structures tourbillonnaires (iso-Q)

1. Repartez de la source `kEpsilon` avec **tous les Mesh Regions cochés** (comme à l'ouverture).
   **Filters → Alphabetical → Cell Data to Point Data**, **Apply**.
2. **Filters → Common → Contour**. *Contour By* : **Q**. *Isosurfaces* : une seule valeur,
   **1000**. **Apply**. (C'est la valeur du montage d'origine — vérifiée sur les trois
   fermetures avant d'écrire cette fiche : elle montre des structures lisibles sur les trois,
   pas besoin d'en changer.)
3. *Coloring* de l'iso-surface : **U → Magnitude**, **Rescale to Custom Range 0 à 10** (même
   plage qu'en V1).
4. Ajoutez la pale en gris : dupliquez la source `kEpsilon` (clic droit → *Add representation to
   view* ou rechargez le `.foam`), gardez seulement les Mesh Regions `propellerTip` +
   `propellerStem1/2/3`, **Apply**, *Coloring* → **Solid Color** gris clair.
5. Caméra : **Position (0 ; −0,243 ; 1,83)**, **Focal Point (0 ; −0,243 ; 0)**, **View Up
   (0 ; 1 ; 0)**, **View Angle 30°**. (La cote y varie de quelques millimètres d'un cas à
   l'autre selon l'étendue exacte de l'iso-surface — sans conséquence visible sur le cadrage.)
6. Capture : `V4_isoQ_<cas>_t0158.png`.

Répétez sur `kOmegaSST` et `laminar`.

**Sur cette vue (les trois cas)** :
- Qu'observez-vous sur la longueur et la netteté du tourbillon de bout de pale (tip vortex), le
  long de l'axe, d'un cas à l'autre ?
- Qu'est-ce que cela vous permet de conclure sur la diffusion de ces structures par chaque
  modèle ?
- Qu'est-ce que cela ne vous permet **pas** de conclure — pensez à l'échelle de temps couverte
  par une seule image (voir README_KIT.md) et à la question de synthèse plus bas.

---

## Partie B — Ce qu'une image ne dit pas (≈ 25 min)

La série `case_kOmegaSST`, **5 pas de 0,155 à 0,159 s** : 0,004 s = **36° de rotation = 0,10
tour**, soit **0,4 passage de pale** (l'hélice a Z = 4 pales, un passage de pale = 90° —
`PARAMETRES_CAS.md`, ligne « Z (nombre de pales) »).

Pour chacun des 5 pas (0,155 · 0,156 · 0,157 · 0,158 · 0,159), reproduisez **V1** et **V4** sur
`case_kOmegaSST` avec les mêmes réglages qu'en partie A (bornes, filtres). Caméra V1 :
identique à la partie A. Caméra V4 : **Position (0 ; −0,242 ; 1,82)**, **Focal Point
(0 ; −0,242 ; 0)**, **View Up (0 ; 1 ; 0)**, **View Angle 30°** (quasi identique au t = 0,158 s
de la partie A). Nommage : `V1_sillage_kOmegaSST_t<temps>.png` /
`V4_isoQ_kOmegaSST_t<temps>.png` (ex. `t155`, `t156`…).

**Questions** :
- Ce que vous avez comparé en partie A (entre les trois fermetures) tient-il d'une image à
  l'autre de cette série (entre 0,155 et 0,159 s) ? Où voyez-vous le plus de changement : sur V1
  (la coupe du sillage) ou sur V4 (les structures 3D) ? Pourquoi, à votre avis ?
- Qu'est-ce que cela change à vos conclusions de la partie A ?

---

## Partie C — Pour aller plus loin, au choix (≈ 20–25 min, bonus)

Choisissez **C1 ou C2** (pas besoin des deux).

### C1 — Couches de prismes vs sans couches, à t = 0,158 s

Reproduisez **V1** et **V3** (les deux caméras) sur `case_kEpsilon_layers`, à comparer à
`case_kEpsilon` (déjà fait en partie A). Réglages V1 identiques à la partie A. Réglages V3 :
mêmes bornes de pression, caméras **aval Position (0 ; −0,730 ; 0)** et **amont Position
(0 ; 0,869 ; 0)**, mêmes Focal Point/View Up/Angle qu'en partie A.

> ⚠️ **Avant de conclure quoi que ce soit** : lisez l'avertissement de
> `data/paraview_kit/README_KIT.md` sur ce cas — le maillage à couches n'est **pas une
> référence validée** (couches incomplètes, bande 0,80–0,925R sans couches,
> `ETAT-DES-LIEUX.md`).

**Question** : les deux images (avec/sans couches) vous permettent-elles de dire si les couches
« améliorent » le calcul ? Qu'est-ce qui vous manquerait pour répondre proprement ?

### C2 — MRF vs AMI

Reproduisez **V1** et **V4** sur les trois cas `case_kEpsilon_MRF`, `case_kOmegaSST_MRF`,
`case_laminar_MRF`, à l'**itération 1500** (tapez `1500` dans le champ Time — pas une seconde,
un numéro d'itération, cas stationnaire). Mêmes réglages V1/V4 qu'en partie A ; caméra V4 :
**Position (0 ; −0,252 ; 1,87)**, **Focal Point (0 ; −0,252 ; 0)**, **View Up (0 ; 1 ; 0)**,
**View Angle 30°**.

> ⚠️ **MRF et AMI ne se comparent pas pas à pas** : le MRF n'a pas de temps physique — c'est un
> état stationnaire convergé (rotor figé, repère tournant), pas un instant du même calcul que
> les cas AMI.

**Question** : la forme des structures tourbillonnaires (V4) est-elle comparable entre MRF et
AMI ? Qu'est-ce que cette différence — ou cette ressemblance — vous dit sur ce que chaque
méthode représente réellement ?

---

## Synthèse — LA question (≈ 10 min)

Le laminaire a le rendement en eau libre **η₀ le plus haut** des trois fermetures
(`Helice/docs/PARAMETRES_CAS.md`, ligne « η₀ (laminar) »).

**Qu'est-ce que vos images permettent d'en dire, et qu'est-ce qu'elles ne permettent PAS de
conclure ?** Réponse en **10 lignes maximum**.

---

## Rendu

- **La planche** : la liste exacte des captures (nommage `<vue>_<cas>_t0158.png`, ou `_t15X.png`
  pour la série, ou `_i1500.png` pour le MRF), rangées dans l'ordre des parties A, B, (C).
- **Les réponses** : une réponse courte par question posée (pas de réponse = vue incomplète).
- **Critères** (repris de `16_CONSIGNE_SEANCE-3.md` §c) : chaque chiffre cité porte sa source
  (fichier + ligne, comme `PARAMETRES_CAS.md`) ; lecture d'image correcte (légende, échelle,
  ce qui est colorié vs ce qui ne l'est pas) ; capacité à dire ce que vous ne savez pas — un
  « je ne peux pas conclure » sourcé vaut mieux qu'une affirmation inventée. Barème chiffré :
  non communiqué dans cette fiche.

---

## Ça ne marche pas

| Symptôme | Cause probable | Correctif |
|---|---|---|
| Rien ne s'affiche | *Apply* pas cliqué | Cliquer *Apply*, *Reset Camera* |
| Le lecteur ne voit qu'un pas `0` | *Decomposed Case* coché | Cocher **Reconstructed Case**, re-*Apply* (le pack est déjà reconstruit — la case existe quand même dans l'interface) |
| Pas de champ `U`/`p`/`Q`/`nut` dans *Coloring* | patchs non chargés / champ décoché dans *Mesh/Cell Arrays* | Cocher les champs dans *Properties*, re-*Apply* |
| `nut` absent de la liste sur `case_laminar` | **normal, pas une panne** — pas de modèle de turbulence en laminaire | Voir V2 : pas d'image pour ce cas, notez l'absence |
| Les trois cas semblent identiques | échelle automatique (*Rescale to Data Range*) au lieu de l'échelle imposée | Toujours *Rescale to Custom Range*, jamais *to Data Range*, avec les bornes de cette fiche |
| Sur `case_kOmegaSST`, l'image ne se superpose pas aux deux autres cas | bouton ⏭ cliqué au lieu de taper `0.158` | Taper `0.158` dans le champ *Time* — le dernier pas de ce cas est 0,159, pas 0,158 |
| Rendu vide sur les cas MRF au Time demandé | temps tapé en secondes au lieu du numéro d'itération | Taper `1500` (un entier, pas `1500.0` ni `1,5`) |
| La pale « disparaît » en tournant la caméra | patch `propeller*` non coché dans *Mesh Regions* | Le recocher, *Apply* |
| `.foam` introuvable | fichier jamais créé, ou mauvais dossier après décompression | Vérifier que `<cas>/<cas>.foam` existe (vide, c'est normal) ; sinon `touch <cas>/<cas>.foam` |
| Coloration en damier plat, pas en dégradé | `Cell Data to Point Data` oublié | Filters → Alphabetical → *Cell Data to Point Data*, avant de colorier |
| Champ `nut` illisible, presque tout d'une seule couleur | échelle linéaire sur un champ qui varie sur 4 ordres de grandeur | Cocher **Use Log Scale** avant de rescaler |
