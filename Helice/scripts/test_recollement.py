#!/usr/bin/env python3
"""Test synthétique de `compare_turbulence.recoller` (20/09) : la règle de recollement des segments d'un
cas repris. Aucun cas OpenFOAM requis. Usage : python3 scripts/test_recollement.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compare_turbulence import recoller, RecollementError, _cle_segment  # noqa: E402


def seg(nom, temps, kt=0.4, d=None):
    rows = [{"time": str(t), "n": "25", "URef": "5", "J": "1", "KT": str(kt if d is None else d(t)),
             "10KQ": "0.5", "eta0": "0.6"} for t in temps]
    return {"path": Path(nom), "brut": rows, "sortie": rows}


def temps(rows):
    return [float(r["time"]) for r in rows]


# 1. redémarrage à pas de temps DIFFÉRENT : l'ancienne série ne doit pas rester entrelacée
a = seg("0/p.dat", [0.01, 0.02, 0.03, 0.04, 0.05])
b = seg("0.03/p.dat", [0.035, 0.045, 0.055])
t = temps(recoller([a, b])[0])
assert t == [0.01, 0.02, 0.03, 0.035, 0.045, 0.055], t          # 0.04 et 0.05 (ancienne grille) retirés

# 2. temps identiques et valeurs identiques : accepté, pas de doublon
a = seg("0/p.dat", [0.01, 0.02, 0.03]); b = seg("0.02/p.dat", [0.02, 0.03, 0.04])
rows, rap = recoller([a, b])
assert temps(rows) == [0.01, 0.02, 0.03, 0.04] and len(rap) == 1, (temps(rows), rap)

# 3. temps communs mais valeurs différentes à D égal : refusé
a = seg("0/p.dat", [0.01, 0.02, 0.03], kt=0.40); b = seg("0.02/p.dat", [0.02, 0.03, 0.04], kt=0.45)
try:
    recoller([a, b]); raise SystemExit("ECHEC : recouvrement incohérent accepté")
except RecollementError:
    pass

# 4. deux rayons d'en-tête différents (D=0,2 puis D correct) : les valeurs BRUTES diffèrent (x0,6) mais la
#    SORTIE rééchelonnée coïncide -> accepté (cas réel du 20/09 : reprise de kOmegaSST au rayon corrigé)
a = seg("0.06/p.dat", [0.01, 0.02, 0.03], kt=0.3707)
b = seg("0.02/p.dat", [0.02, 0.03, 0.04], kt=0.3707 * 0.5986)          # brut au rayon corrigé, plus petit
a["sortie"] = [dict(r, KT=str(0.3707 * 0.5986)) for r in a["brut"]]    # rééchelonné au même D
rows, _ = recoller([a, b]); assert temps(rows) == [0.01, 0.02, 0.03, 0.04]
#    ... et la comparaison fautive d'origine (rééchelonné d'un côté, brut de l'autre) serait refusée :
a2 = seg("0.06/p.dat", [0.01, 0.02, 0.03], kt=0.3707)
b2 = seg("0.02/p.dat", [0.02, 0.03, 0.04], kt=0.3707)
a2["sortie"] = [dict(r, KT="0.2219") for r in a2["brut"]]              # rééchelonné, alors que b2 ne l'est pas
try:
    recoller([a2, b2]); raise SystemExit("ECHEC : sortie non homogène acceptée")
except RecollementError:
    pass

# 5. un segment plus récent qui s'arrête AVANT la fin du précédent : refusé (queue perdue)
a = seg("0/p.dat", [0.01, 0.02, 0.03, 0.04]); b = seg("0.02/p.dat", [0.02, 0.025])
try:
    recoller([a, b]); raise SystemExit("ECHEC : queue perdue acceptée")
except RecollementError:
    pass

# 6. ordre des fichiers : normal avant suffixé, dossiers par temps numérique croissant
ps = [Path("x/0.06/propellerPerformance_0.06.dat"), Path("x/0.06/propellerPerformance.dat"),
      Path("x/0.058/propellerPerformance.dat"), Path("x/0/propellerPerformance.dat"), Path("x/0.01/propellerPerformance.dat")]
assert [str(p.relative_to("x")) for p in sorted(ps, key=_cle_segment)] == [
    "0/propellerPerformance.dat", "0.01/propellerPerformance.dat", "0.058/propellerPerformance.dat",
    "0.06/propellerPerformance.dat", "0.06/propellerPerformance_0.06.dat"]
print("OK -- 6 cas de recollement")
