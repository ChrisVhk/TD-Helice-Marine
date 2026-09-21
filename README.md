# TD Hélice marine — OpenFOAM (ENSM FON-S7)

TD CFD couvrant les 2 attendus OpenFOAM du référentiel **FON-S7 — Mécanique des fluides – Hydrodynamique**
(TD 6h, réf. ING-GM 2e cycle DMO-FISE p.17 / EGN-FISE p.19) :

- Calcul de **portance et traînée d'une pale d'hélice marine** (script OpenFOAM).
- Comparaison des résultats selon le **modèle de turbulence** (tutoriel OpenFOAM).

Les deux attendus sont traités sur un **même cas** : l'hélice en eau libre (tutoriel officiel
OpenFOAM `incompressible/pimpleFoam/RAS/propeller`), décliné en 3 fermetures de turbulence.

## Structure

```
Helice/
├── case_kEpsilon/    — fermeture RAS k-epsilon (référence, config native du tutoriel)
├── case_kOmegaSST/   — fermeture RAS k-omega SST
├── case_laminar/     — sans modèle de turbulence (simulationType laminar)
├── scripts/          — post-traitement Python (comparaison KT/KQ/eta0 entre modèles)
└── docs/             — supports pédagogiques (à compléter, voir Helice/docs/STATUT.md)
```

Rattachement : [`TD-TP/FON-S7_MecaFluides-Hydro/README.md`](https://github.com/ChrisVhk/ENSM-Enseignement)
(dépôt cours privé) et fiche référentiel `_Fiches/Fiche_FON-S7_MecaFluides-Hydrodynamique.md`.

## Démarrage rapide

```bash
source /usr/lib/openfoam/openfoam2412/etc/bashrc   # environnement OpenFOAM 2412
cd Helice
bash 02_run.sh          # maille + calcule les 3 cas (long : snappyHexMesh + parallèle)
bash 03_postprocess.sh  # compare KT, KQ, eta0 entre les 3 modèles
bash 04_clean.sh        # nettoyage
```

**Avant tout calcul long : pré-vol INV-23** (l'espace du disque HÔTE, jamais `df /` — le disque de la distro
affiche des centaines de Go libres même quand l'hôte est plein).

```bash
bash _Setup/outils/preflight.sh                 # disque hôte, RAM ; sort en code != 0 et NOMME le seuil franchi
bash _Setup/outils/preflight.sh Helice/case_X   # + vérifie qu'un calcul Foam est vivant sur ce cas
```

`_Setup/outils/preflight.sh` est une copie synchronisée du noyau ENSM (source de vérité :
`ENSM-Enseignement/_Setup/outils/preflight.sh`, dépôt privé ; ce dépôt-ci ignore `_Setup/` sauf une liste
d'outils propres). Sur une machine neuve, le recopier ou lancer
`bash ~/ENSM-Enseignement/_Setup/synchroniser_noyau.sh <ce dépôt>`. Seuils : bloquant sous 15 Go libres sur
l'hôte, alerte sous 40 Go.

Chaque cas est autonome (mesh + solve), self-contained comme le tutoriel officiel dont il dérive.
