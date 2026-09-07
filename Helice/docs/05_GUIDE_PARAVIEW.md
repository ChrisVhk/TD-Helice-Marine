# Guide ParaView — TD Hélice marine en eau libre

> Réécrit pour **ce cas précis** (hélice `propeller`, 3 fermetures de turbulence). Objectif : produire
> **3 vues comparables** des 3 cas (même instant, même échelle de couleurs) pour la restitution.
> Le guide s'appuie sur les champs réellement écrits par ce setup : `U`, `p`, `Q`.

---

## 1. Pré-requis

- Les 3 cas sont calculés : dossiers de temps `0.001 … 0.06` présents et reconstruits
  (`reconstructPar` déjà passé — vérifier `ls case_kEpsilon/0.06/`).
- ParaView installé (`paraview --version`).
- Se placer dans le dossier du TD :
  ```bash
  cd ~/Work_ENSM/TD-Helice-Marine/Helice
  ```

---

## 2. Ouvrir un cas

OpenFOAM n'écrit pas de fichier `.foam` tout seul — on le crée (vide, il sert juste de point
d'entrée pour ParaView) :

```bash
touch case_kEpsilon/case_kEpsilon.foam
touch case_kOmegaSST/case_kOmegaSST.foam
touch case_laminar/case_laminar.foam
paraview case_kEpsilon/case_kEpsilon.foam &
```

Dans ParaView :
1. Le lecteur **OpenFOAM** s'ouvre → dans *Properties*, cocher **Reconstructed Case** (pas
   *Decomposed*), puis **Apply**.
2. *Mesh Regions* : garder `internalMesh` ; cocher aussi les patchs `propeller...` pour voir la pale.
3. Aller au **dernier pas de temps** ($t = 0{,}06$ s) avec le bouton ⏭ de la barre d'animation.
4. Renommer la source dans le *Pipeline Browser* (clic droit → *Rename*) en `kEpsilon` pour s'y retrouver.

---

## 3. Vue 1 — Sillage : vitesse dans un plan axial

Le sillage (accélération du fluide en aval, contraction de la veine) est la signature la plus
visible de la fermeture de turbulence.

1. Source `kEpsilon` sélectionnée → **Filters → Alphabetical → Slice** (ou *Common → Slice*).
2. *Slice Type* : **Plane**. L'axe de rotation de l'hélice est **Y** (`axis (0 1 0)`), l'écoulement
   va dans le sens $-Y$. Pour couper **le long** du sillage, prendre un plan **normal à Z** :
   *Normal* = `0 0 1`, *Origin* = `0 0 0`. **Apply**.
3. *Coloring* : **U** → **Magnitude**.
4. **Rescale to Data Range**, puis **noter les bornes min/max** : il faudra **imposer la même
   échelle** sur les 3 cas (voir §6).
5. *Show Color Legend* (bouton barre de couleurs). Vérifier que la légende indique `U Magnitude (m/s)`.
6. Cadrer sur : hélice + 2 à 3 diamètres de sillage en aval.

**À observer** : longueur et intensité du jet en aval, présence/absence d'une zone de recirculation
(vitesse quasi nulle) juste derrière le moyeu. Le cas laminaire ne diffuse pas la quantité de
mouvement de la même manière que les cas RANS.

---

## 4. Vue 2 — Pression sur la pale

1. Sélectionner la source `kEpsilon` (pas le Slice).
2. Dans *Mesh Regions* / *Representation*, s'assurer que les patchs `propeller...` sont visibles,
   *Representation* = **Surface**.
3. *Coloring* : **p**.
   > `p` est la **pression cinématique** (m²/s²) : $p_{[Pa]} = p \times \rho$. Pour la comparaison
   > entre modèles, l'échelle en m²/s² suffit.
4. **Rescale to Data Range**, noter min/max, imposer la même échelle sur les 3 cas.
5. Orienter la caméra pour voir la **face en pression** (intrados, côté amont) puis la **face en
   dépression** (extrados). Deux captures.

**À observer** : étendue de la zone de dépression sur l'extrados (c'est elle qui porte la poussée) ;
présence de taches de dépression marquée en bord d'attaque (risque de décollement / cavitation en
réalité). k-ω SST et k-ε ne prédisent pas la même distribution en proche paroi.

---

## 5. Vue 3 — Structures tourbillonnaires (critère Q)

Le champ `Q` (critère Q) est déjà calculé et écrit par le cas.

1. Source `kEpsilon` → **Filters → Common → Contour**.
2. *Contour By* : **Q**. *Isosurfaces* : une seule valeur, **`1000`** (même valeur que la
   `isoValue` du setup, cohérente entre cas). **Apply**.
3. *Coloring* de l'iso-surface : **U** → **Magnitude** (même échelle que Vue 1).
4. Ajouter la pale en surface grise par-dessus (source principale, *Solid Color*).

**À observer** : le tourbillon de bout de pale (tip vortex) et le tourbillon de moyeu (hub vortex).
Leur cohérence en aval, leur rythme de désintégration : le cas laminaire les garde nets très loin
(pas de diffusion turbulente), k-ε les diffuse le plus vite, k-ω SST est intermédiaire.

---

## 6. Rendre les 3 cas comparables (étape obligatoire)

1. Ouvrir les 3 `.foam` dans la **même** session ParaView (ou 3 layouts côte à côte).
2. Reproduire Vue 1 / Vue 2 / Vue 3 sur chacun.
3. Pour **chaque grandeur** (`U Mag`, `p`, …) : clic droit sur la barre de couleurs →
   *Rescale to Custom Range* → entrer **les mêmes bornes** pour les 3 cas (prendre l'enveloppe des
   min/max relevés).
4. Se placer au **même pas de temps** ($t = 0{,}06$ s) sur les 3.
5. Utiliser le **même angle de caméra** : *Adjust Camera* → noter position/focal, ou *Save State*
   (§7) et recharger.

> Sans cette étape, les 3 captures ne prouvent rien : une différence de couleur pourrait n'être
> qu'une différence d'échelle automatique.

---

## 7. Sauvegarder / recharger l'état

- **File → Save State** → `post/paraview_helice.pvsm`.
- Rechargement : **File → Load State** → si ParaView demande les fichiers, pointer vers les 3
  `case_XXX/case_XXX.foam`.

---

## 8. Export des figures

1. Caméra en place, échelles imposées.
2. **File → Save Screenshot** → 1920×1080, fond blanc.
3. Nommage : `post/paraview_images/<vue>_<cas>_t060.png`
   (ex. `U_slice_kOmegaSST_t060.png`, `p_blade_laminar_t060.png`, `Q_contour_kEpsilon_t060.png`).

```bash
mkdir -p post/paraview_images
```

---

## 9. Checklist de rendu

- [ ] 1 coupe axiale de sillage (`U Mag`) × 3 cas, **même échelle**.
- [ ] 1 vue pression sur pale (`p`) × 3 cas, **même échelle**.
- [ ] 1 iso-surface Q (Q=1000, colorée par `U Mag`) × 3 cas.
- [ ] Toutes au même instant $t = 0{,}06$ s, même caméra.
- [ ] 1 état `post/paraview_helice.pvsm` sauvegardé.

---

## 10. Dépannage

| Symptôme | Cause probable | Correctif |
|---|---|---|
| Rien ne s'affiche | *Apply* pas cliqué, ou pas de temps sans données | Cliquer *Apply*, aller au dernier pas, *Reset Camera* |
| Le lecteur ne voit qu'un pas `0` | *Decomposed Case* coché | Cocher **Reconstructed Case**, re-*Apply* |
| Pas de champ `U`/`p`/`Q` dans *Coloring* | patchs non chargés / champ décoché dans *Cell/Point Arrays* | Cocher les champs dans *Properties*, re-*Apply* |
| Les 3 cas semblent identiques | échelles automatiques différentes | *Rescale to Custom Range* identique sur les 3 (§6) |
| La pale « disparaît » quand on tourne | patch `propeller` non coché dans *Mesh Regions* | le recocher, *Apply* |
| `.foam` introuvable au *Load State* | fichier jamais créé | `touch case_XXX/case_XXX.foam` |
