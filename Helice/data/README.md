# Kit de données — TD Hélice marine

Le calcul OpenFOAM ne tourne **pas** en séance (un cas = ~2 h sur 4 cœurs et 12–14 Go). Les
résultats sont fournis ici. Tout est régénérable depuis les 3 cas du dépôt via
`scripts/extraire_kit_donnees.py`.

## Séances 1–2 et inter-séance A — séries temporelles (versionné, < 1 Mo)

| Fichier | Fermeture | Séance 1 (question fréquence) | Séance 2 (comparaison modèles) |
|---|---|---|---|
| `perf_kEpsilon.csv` | RANS k-ε standard | ✅ distribué | ✅ distribué |
| `perf_laminar.csv` | laminaire | ✅ distribué | ✅ distribué |
| `perf_kOmegaSST.csv` | RANS k-ω SST | ❌ **retenu** — voir encadré | ✅ distribué |

> ⚠️ **`perf_kOmegaSST.csv` — ne pas distribuer pour la question de fréquence de la séance 1**
> (diagnostiqué le 06/09 au soir, LOT 0A). Sa fenêtre « dernier tour » n'a que 0,955 tour de
> données continues (trou de 0,0082 à 0,0220 s : reprise après l'incident disque du 05/09) — trop
> court pour qu'une FFT résolve la fréquence de rotation imposée (25,15 Hz) ; la mesure dérive vers
> ~26,2–26,3 Hz, un artefact de résolution spectrale et non un signal réel (confirmé : temps
> correctement recousu, checksum de régénération identique, $\omega = 158$ rad/s identique dans les
> 3 cas). **Les moyennes $K_T$/$K_Q$/$\eta_0$ de ce fichier restent valides** — c'est uniquement la
> mesure de fréquence qui est compromise. Séance 1 : distribuer seulement `perf_kEpsilon.csv` et
> `perf_laminar.csv`. Séance 2 : les trois fichiers, comme prévu. Détail complet :
> `docs/10_CORRIGE_ETUDIANT_DETAILLE.md` §4 et `docs/STATUT.md`.

Colonnes : `time, n, URef, J, KT, 10KQ, eta0` — sortie du *function object* `propellerInfo`,
une ligne par pas de temps écrit, série recousue sur les reprises et dédupliquée sur `time`.

> **Les toutes premières lignes sont un transitoire de démarrage** ($K_T$ de plusieurs centaines
> quand `URef` ≈ 0) : c'est normal, ça s'établit en quelques millisecondes. Fait partie de ce que
> les étudiants doivent repérer eux-mêmes.
>
> `URef` est **négatif** (convention d'axe : écoulement dans le sens $-y$) et **échantillonné** dans
> le sillage amont, pas imposé → $J$ diffère légèrement d'un cas à l'autre (< 1 %).

Régénérer : `python3 scripts/extraire_kit_donnees.py --csv`

## Séance 3 — champs pour ParaView (NON versionné, ~1 Go)

`data/paraview_kit/` : 5 pas du dernier tour sur `case_kOmegaSST` + le pas final ($t = 0{,}06$) sur
`case_kEpsilon` et `case_laminar`, avec maillage. Un fichier `<case>.foam` par cas pour l'ouverture
ParaView.

À produire **avant la séance 3** (pas dans le dépôt — trop lourd, régénérable) :

```
python3 scripts/extraire_kit_donnees.py --champs
```

Distribution : archiver `data/paraview_kit/` et le diffuser hors dépôt (kDrive, clé USB, partage
réseau école).
