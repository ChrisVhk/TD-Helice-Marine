# Amplitude K_T sur fenêtre propre — LOT A, 13/09

Fait suite au défaut consigné le 13/09 : `Helice/data/perf_kOmegaSST.csv` a un trou de
13,8 ms entre t = 0,008194 et t = 0,022032 s (1433 points contre 1853 pour `kEpsilon` et
1886 pour `laminar`, sans trou). Le dernier tour complet commence à t = 0,06 − 0,03977 =
0,02023 s : le trou mord sur ses 1,8 premières ms.

## Méthode

Amplitude crête à crête de `KT`, calculée sur une fenêtre **commune aux trois modèles**,
qui exclut le trou : **[0,022032 ; 0,06] s**, durée 0,037968 s (0,955 tour). Chaque point
de `perf_<modèle>.csv` dans cette fenêtre est retenu ; l'amplitude est `max(KT) − min(KT)`
sur l'ensemble retenu. Aucun calcul relancé — lecture seule des CSV déjà sur disque.

## Résultat

| Modèle       | Points dans la fenêtre | Ancienne valeur publiée¹ | Nouvelle valeur (fenêtre propre) | Écart |
|---|---|---|---|---|
| `laminar`    | 1194 | 0,0404 | 0,040407 | +0,000007 |
| `kOmegaSST`  | 1168 | 0,0373 | 0,037294 | −0,000006 |
| `kEpsilon`   | 1168 | 0,0294 | 0,029420 | +0,000020 |

¹ Deck de la séance 2, diapo 3, valeurs de référence du présentateur (diapo 2 avant la
restructuration du 18/09) : « amplitude K_T (crête à crête)
0,0294 / 0,0404 / 0,0373 — re-vérifiées par exécution sur les CSV du dépôt, dernier tour ».

**Ordre inchangé** : `laminar` (0,0404) > `kOmegaSST` (0,0373) > `kEpsilon` (0,0294),
identique à l'ordre publié.

## Constat, pas une correction

Les trois valeurs recalculées sur la fenêtre propre **coïncident avec les valeurs déjà
publiées à la 4ᵉ décimale près** — l'écart le plus grand (kEpsilon, +0,00002) est sous le
seuil de lecture d'un graphique. Explication la plus probable, non vérifiée par ailleurs :
la fenêtre « dernier tour » [0,02023 ; 0,06] s utilisée pour la valeur publiée n'avait de
toute façon aucune donnée `kOmegaSST` disponible dans les 1,8 premières ms (le trou les
couvre entièrement) — le calcul d'origine, exécuté sur les lignes réellement présentes
dans le CSV, a donc déjà, de fait, porté sur la même fenêtre que celle utilisée ici. Le
trou est un défaut de traçabilité réel (toute FFT couvrant cette fenêtre serait fausse,
cf. JOURNAL.md) mais **n'a pas corrompu cette métrique d'amplitude précise**.

**Rien à corriger dans les supports** : l'ordre et les valeurs publiées restent valides.

## Précision brute (fenêtre [0,022032 ; 0,06] s)

| Modèle | KT min | KT max | Amplitude |
|---|---|---|---|
| `kEpsilon`  | 0,3435849 | 0,3730054 | 0,0294205 |
| `kOmegaSST` | 0,3459818 | 0,3832759 | 0,0372941 |
| `laminar`   | 0,3512840 | 0,3916908 | 0,0404068 |
