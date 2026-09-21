#!/usr/bin/env python3
"""MRF contre instationnaire, par modèle de turbulence : l'écart de méthode dépend-il du modèle ? -- 20/09 soir.

Critère et seuils écrits AVANT les calculs : ENSM-Enseignement/_Reserve/comparaison-3-modeles/LOT4b_MRF_kOmegaSST_laminaire_critere.md
Pour chaque cas MRF présent (`case_<modele>_MRF`), sur les 200 dernières itérations :
  - K_T, 10 K_Q (propellerPerformance.dat), leur dérive (200 dernières contre les 200 précédentes) et leur pente sur 500 itérations ;
  - amplitude crête-à-crête sur les 500 dernières itérations (un état permanent la ramène à ~0) ;
  - résidus initiaux de p et de Ux au début, à mi-parcours et à la fin (log.simpleFoam) ;
  - écart relatif à la MOYENNE du dernier tour de l'instationnaire du même modèle (lue dans data/perf_<modele>.csv) ;
  - décomposition pression / frottement de l'écart (force.dat, moment.dat du MRF contre la moyenne du dernier tour de
    l'instationnaire, mêmes conventions que decomposition_pression_frottement.py).
Rien n'est recalculé : lecture seule. Aucun verdict imprimé : la lecture est dans le document de critère.
"""
import contextlib
import io
import math
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decomposition_pression_frottement as dpf  # noqa: E402

HELICE = dpf.HELICE
MODELES = ["kEpsilon", "kOmegaSST", "laminar"]
fK_T = 1.0 / (dpf.N ** 2 * dpf.D ** 4)
fK_Q = 10.0 / (dpf.N ** 2 * dpf.D ** 5)


def perf_instationnaire(m):
    d = np.genfromtxt(os.path.join(HELICE, "data", f"perf_{m}.csv"), delimiter=",", names=True)
    t1 = d["time"][-1]
    s = d[d["time"] >= t1 - dpf.T - 1e-12]
    f = lambda c: np.trapz(s[c], s["time"]) / (s["time"][-1] - s["time"][0])
    return f("KT"), f("10KQ")


def residus(log, champ):
    r = []
    for l in open(log, errors="ignore"):
        mm = re.search(rf"Solving for {champ}, Initial residual = ([0-9.e+-]+)", l)
        if mm:
            r.append(float(mm.group(1)))
    return r


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        ref = dpf.main()
    lignes = {}
    for m in MODELES:
        d_ = os.path.join(HELICE, f"case_{m}_MRF")
        pp = os.path.join(d_, "postProcessing", "propellerInfo1", "0", "propellerPerformance.dat")
        if not os.path.isfile(pp):
            print(f"{m} : pas de propellerPerformance.dat (non lancé)")
            continue
        P = np.array([[float(x) for x in l.split()] for l in open(pp) if l.strip() and not l.startswith("#")])
        n = len(P)
        kt, kq = P[:, 4], P[:, 5]
        dern, prec = slice(n - 200, n), slice(n - 400, n - 200)
        ktm, kqm = kt[dern].mean(), kq[dern].mean()
        pente = lambda y: 100 * (y[n - 500:].mean() - y[n - 1000:n - 500].mean()) / y[n - 500:].mean() if n >= 1000 else float("nan")
        print(f"\n=== MRF {m} : {n} itérations")
        print(f"  K_T {ktm:.5f}  10K_Q {kqm:.5f}  (200 dernières)  | dérive 200/200 : K_T {100 * (ktm / kt[prec].mean() - 1):+.4f} %, 10K_Q {100 * (kqm / kq[prec].mean() - 1):+.4f} %"
              f"  | 500/500 : K_T {pente(kt):+.4f} %, 10K_Q {pente(kq):+.4f} %")
        print(f"  amplitude crête-à-crête sur les 500 dernières itérations : K_T {kt[n - 500:].max() - kt[n - 500:].min():.2e} ({100 * (kt[n - 500:].max() - kt[n - 500:].min()) / ktm:.4f} %), "
              f"10K_Q {kq[n - 500:].max() - kq[n - 500:].min():.2e} ({100 * (kq[n - 500:].max() - kq[n - 500:].min()) / kqm:.4f} %)")
        log = os.path.join(d_, "log.simpleFoam")
        for ch in ("p", "Ux"):
            r = residus(log, ch)
            if r:
                print(f"  résidu initial {ch} : it. 1 {r[0]:.2e} ; it. {len(r) // 2} {r[len(r) // 2]:.2e} ; it. {len(r)} {r[-1]:.2e} ; min {min(r):.2e} ; max sur les 500 dernières {max(r[-500:]):.2e}")
        ktu, kqu = perf_instationnaire(m)
        ekt, ekq = 100 * (ktm / ktu - 1), 100 * (kqm / kqu - 1)
        lignes[m] = (ekt, ekq)
        print(f"  contre l'instationnaire {m} (dernier tour) : K_T {ktu:.4f} -> écart {ekt:+.2f} % ; 10K_Q {kqu:.4f} -> écart {ekq:+.2f} %")
        try:
            F = dpf.lire(os.path.join(d_, "postProcessing/forces/0/force.dat"))
            M = dpf.lire(os.path.join(d_, "postProcessing/forces/0/moment.dat"))
            tt = dict(poussee=(F, fK_T, 1), couple=(M, fK_Q, -1))
            out = []
            for g, (S, fac, sg) in tt.items():
                v = {k: sg * fac * S[-200:, c].mean() for k, c in (("total", 2), ("pression", 5), ("visqueux", 8))}
                u = ref[m][g]
                uv = {k: sg * fac * u[k] for k in ("total", "pression", "visqueux")}
                out.append(f"{g} : écart total {100 * (v['total'] / uv['total'] - 1):+.2f} % = pression {100 * (v['pression'] - uv['pression']) / uv['total']:+.2f} pt + frottement {100 * (v['visqueux'] - uv['visqueux']) / uv['total']:+.2f} pt (de l'instationnaire total)")
            print("  décomposition : " + " | ".join(out))
        except Exception as e:  # noqa: BLE001
            print(f"  décomposition non calculée : {e}")
    if len(lignes) >= 2:
        print("\n=== Écarts de méthode (MRF contre moyenne de l'instationnaire), par modèle")
        for m, (a, b) in lignes.items():
            print(f"  {m:10s} K_T {a:+.2f} %   10K_Q {b:+.2f} %")
        for g, i in (("K_T", 0), ("10K_Q", 1)):
            v = [x[i] for x in lignes.values()]
            print(f"  étendue sur les modèles, {g} : {max(v) - min(v):.2f} point(s)")


if __name__ == "__main__":
    main()
