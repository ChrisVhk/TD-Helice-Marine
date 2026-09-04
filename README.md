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

Chaque cas est autonome (mesh + solve), self-contained comme le tutoriel officiel dont il dérive.
