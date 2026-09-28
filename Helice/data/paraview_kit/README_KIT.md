# Kit ParaView — laminaire vs turbulent (séance 3)

> ParaView s'ouvre sur les dossiers de l'ARCHIVE (champs à 0,158 s). Les `.foam` du dépôt
> cloné servent si vous maillez ou copiez des pas de temps vous-mêmes.

Sept cas, chacun s'ouvre seul (`<cas>.foam` à sa racine). Les chiffres de référence
(K_T, 10K_Q, η₀…) ne sont PAS recopiés ici : voir `Helice/docs/PARAMETRES_CAS.md`,
source unique de vérité.

## Ce qu'il y a

| Cas | Instant | Champs | Ce que ça permet de voir |
|---|---|---|---|
| `case_kEpsilon` | 0,158 s | U, p, Q, k, nut, epsilon | comparaison laminaire / turbulent |
| `case_kOmegaSST` | 0,158 s | U, p, Q, k, nut, omega | comparaison laminaire / turbulent |
| `case_laminar` | 0,158 s | U, p, Q | comparaison laminaire / turbulent (pas de nut : pas de viscosité turbulente) |
| `case_kOmegaSST` (série) | 0,155 → 0,159 s | U, p, Q, k, nut, omega | le sillage qui tourne, 5 images sur 36° de rotation (0,004 s = 0,10 tour), soit 0,4 passage de pale (Z = 4) |
| `case_kEpsilon_layers` | 0,158 s | U, p, Q, k, nut, epsilon | la paroi, comparée à `case_kEpsilon` (sans couches) au même instant |
| `case_kEpsilon_MRF`, `case_kOmegaSST_MRF`, `case_laminar_MRF` | itération 1500 | U, p, Q (+ k/nut/epsilon\|omega selon le modèle) | le même problème traité en stationnaire (rotor figé) |

Les trois fermetures à 0,158 s partagent le même instant : à même ω, le rotor est
au même angle dans les trois cas, les vues sont superposables. C'est aussi
l'instant du cas à couches.

## Avertissements

- **Un pas = 0,001 s = 1/40 de tour.** Ne concluez pas sur une seule image : regardez
  la série `case_kOmegaSST` pour voir ce qui bouge d'un pas au suivant.
- **Le cas à couches n'est pas une référence validée** (couches incomplètes, bande
  0,80–0,925R sans couches — voir `Helice/docs/ETAT-DES-LIEUX.md`).
- **MRF et AMI ne se comparent pas pas à pas** : le MRF n'a pas de temps physique
  (l'itération 1500 est un état stationnaire convergé, pas un instant).

## La question

Le laminaire a le η₀ le plus haut (`PARAMETRES_CAS.md`). Qu'est-ce que les images de
ce kit vous permettent d'en dire — et qu'est-ce qu'elles ne permettent PAS de conclure ?
