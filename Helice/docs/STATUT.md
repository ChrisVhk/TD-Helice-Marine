# Statut de la suite pédagogique — TD Hélice marine

Suite standard (voir `TD-TP/FON-S7_MecaFluides-Hydro/Poiseuille/docs/` pour le modèle) :

| # | Document | Statut |
|---|---|---|
| 01 | Fiche consigne | ✅ rédigée |
| 02 | QCM prérequis | 🟡 à faire |
| 03 | Base théorique | ✅ rédigée (KT/KQ/J/η0, fermetures RAS vs laminaire) |
| 04 | Guide pas-à-pas | 🟡 à faire |
| 05 | Guide ParaView | ✅ porté depuis `PerfNav/Propulseur` (à revalider sur ce cas précis) |
| 06 | QCM final | 🟡 à faire |
| 07 | Aide-mémoire | 🟡 à faire |
| 08 | Corrigé QCM | 🟡 à faire (dépend de 02/06) |
| 09 | Fiche enseignant | 🟡 à faire |
| 10 | Corrigé étudiant détaillé | 🟡 à faire — **dépend d'une exécution réelle des 3 cas** (valeurs KT/KQ/η0 non encore mesurées dans ce dépôt, `02_run.sh` jamais lancé au moment de la création du repo) |
| — | Annexe installation | ✅ portée depuis `PerfNav/Propulseur` |

## Non encore validé

- **Aucun des 3 cas n'a été exécuté** dans ce repo au moment de sa création : la géométrie/maillage
  (`snappyHexMesh`), le calcul parallèle (4 sous-domaines) et le function object `propellerInfo`
  proviennent tels quels du tutoriel officiel OpenFOAM 2412, non re-vérifiés ici pour ce jeu de
  3 variantes. À faire avant tout usage en séance : `bash 02_run.sh` puis `bash 03_postprocess.sh`
  sur la machine cible, vérifier que les 3 lignes du tableau sont cohérentes (KT différent de zéro,
  pas de NaN), ajuster `docs/10_CORRIGE_ETUDIANT_DETAILLE.md` avec les valeurs réelles obtenues.
- `omega0` de `case_kOmegaSST` est dérivé par calcul (voir `03_BASE_THEORIQUE.md` §2), pas mesuré —
  cohérent avec la pratique standard mais à confirmer par une convergence propre du calcul.
- Le doublon `PerfNav/Propulseur/tp_propulseur_eau_libre_v2412/` (cas MRF + squelette overset KP505)
  reste dans son propre repo, non synchronisé avec celui-ci — ce TD est reparti de zéro depuis le
  tutoriel officiel (la copie PerfNav avait `0.orig/` manquant, cf. journal de la session de création).
