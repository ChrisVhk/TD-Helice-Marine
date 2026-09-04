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

- **Les 3 cas sont en cours d'exécution** (lancés lors de la session de validation, non encore
  terminés au moment de ce commit). Constat en cours de route : `KT`/`10·KQ`/`eta0` oscillent avec
  la période de rotation (T = 1/n ≈ 0,0398 s) et ne se stabilisent pas en un point unique — une
  lecture de la dernière ligne à un instant arbitraire est trompeuse. Décisions prises :
  - `endTime` ramené de 0,1 s à **0,06 s** (~1,5 tour) sur les 3 cas — compromis temps de calcul
    (chaque cas ≈ 1h+ de calcul parallèle sur 4 cœurs) vs nombre de tours disponibles pour moyenner.
  - `scripts/compare_turbulence.py` moyenne désormais sur le **dernier tour complet** plutôt que de
    lire l'instant final, avec un flag explicite si le calcul n'a pas encore couvert un tour complet.
  - À faire avant tout usage en séance : relancer `bash 03_postprocess.sh` une fois les 3 cas au-delà
    de t=0,06 sans flag `⚠`, vérifier la plausibilité physique, ajuster
    `docs/10_CORRIGE_ETUDIANT_DETAILLE.md` avec les valeurs réelles obtenues.
- `omega0` de `case_kOmegaSST` est dérivé par calcul (voir `03_BASE_THEORIQUE.md` §2), pas mesuré —
  cohérent avec la pratique standard mais à confirmer par une convergence propre du calcul.
- Le doublon `PerfNav/Propulseur/tp_propulseur_eau_libre_v2412/` (cas MRF + squelette overset KP505)
  reste dans son propre repo, non synchronisé avec celui-ci — ce TD est reparti de zéro depuis le
  tutoriel officiel (la copie PerfNav avait `0.orig/` manquant, cf. journal de la session de création).
