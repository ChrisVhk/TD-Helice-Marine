#!/usr/bin/env python3
"""Borne de l'effet du PAS DE TEMPS sur K_T / 10 K_Q, sur le MÊME maillage (case_kEpsilon_layers) -- 20/09.

Compare, sur le 2e tour [T ; 2T] (T = 2 pi / 158 = 0,039767 s), deux historiques du même cas à couches :
  - postProcessing/propellerInfo1/0/propellerPerformance_0.dat          : calcul final, deltaT 1e-5 (pas fixe)
  - postProcessing/propellerInfo1/0/propellerPerformance_0_recupere.dat : essai à 2 tours, deltaT 2e-5, RECONSTRUIT
    à partir du log du solveur (log.pimpleFoam.LOT6_2tours) le 18/09, l'historique brut ayant été écrasé.
Moyennes pondérées par le temps. Un facteur 2 sur le pas ; le cas case_kEpsilon, lui, tourne en pas ADAPTATIF
(maxCo 2, pas observé ~3,2e-5) : le facteur entre les deux cas est ~3, au-delà de ce qui est borné ici.
CETTE FENÊTRE N'EST PAS LE RÉGIME ÉTABLI (établi vers 2,5 tours) : borne indicative, pas mesure de régime.

Usage : python3 Helice/scripts/borne_pas_de_temps.py
"""
import csv
import math
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from avance_imposee import vitesse_inlet, j_impose  # noqa: E402

HELICE = Path(__file__).resolve().parents[1]
D = HELICE / "case_kEpsilon_layers" / "postProcessing" / "propellerInfo1" / "0"
T = 2 * math.pi / 158
VINLET = vitesse_inlet(HELICE / "case_kEpsilon_layers")
COLS = ["time", "n", "URef", "J", "KT", "10KQ", "eta0"]


D_CORRECT = 0.227378  # docs/PARAMETRES_CAS.md ; les deux fichiers de ce cas portent déjà radius 0,113689 dans leur segment


def lire(p):
    """Lit un fichier du solveur. `J` et `eta0` sont ceux du solveur (calculés avec URef, mesuré en aval) : ils sont
    REMPLACÉS ici par l'avance imposée (correction du 20/09, soir) ; K_T et K_Q ne sont pas touchés."""
    rows = []
    for l in open(p):
        if l.startswith("#") or not l.strip():
            continue
        x = l.split()
        if len(x) >= 7:
            try:
                r = dict(zip(COLS, map(float, x[:7])))
                j_imp = j_impose(VINLET, r["n"], D_CORRECT)
                r["eta0"] = r["eta0"] * j_imp / r["J"] if r["J"] else r["eta0"]
                r["J"] = j_imp
                rows.append(r)
            except ValueError:
                pass
    return rows


def moy(rows, col, t0, t1):
    pts = [r for r in rows if t0 - 1e-12 <= r["time"] <= t1 + 1e-12]
    s = sum(0.5 * (pts[i]["time"] - pts[i - 1]["time"]) * (pts[i][col] + pts[i - 1][col]) for i in range(1, len(pts)))
    return s / (pts[-1]["time"] - pts[0]["time"])


def pas(rows, t0, t1):
    t = [r["time"] for r in rows if t0 <= r["time"] <= t1]
    d = [b - a for a, b in zip(t, t[1:])]
    return st.median(d)


def main():
    fin = lire(D / "propellerPerformance_0.dat")
    rec = lire(D / "propellerPerformance_0_recupere.dat")
    t0, t1 = T, 2 * T
    print(f"2e tour [{t0:.6f} ; {t1:.6f}] s  --  cas à couches, même maillage (polyMesh du 13/09)")
    print(f"  final    : dt = {pas(fin, t0, t1):.1e} s ({len(fin)} lignes)   |   récupéré : dt = {pas(rec, t0, t1):.1e} s ({len(rec)} lignes)")
    print(f"  {'grandeur':7s}{'dt 1e-5':>10s}{'dt 2e-5':>10s}{'variation (1e-5 vs 2e-5)':>28s}")
    for c in ("J", "KT", "10KQ", "eta0"):
        a, b = moy(fin, c, t0, t1), moy(rec, c, t0, t1)
        print(f"  {c:7s}{a:10.4f}{b:10.4f}{100 * (a - b) / b:+27.2f} %")
    # pas réel de case_kEpsilon (adaptatif), dernier tour
    k = [{c: float(v) for c, v in r.items()} for r in csv.DictReader(open(HELICE / "data" / "perf_kEpsilon.csv"))]
    tend = k[-1]["time"]
    print(f"\ncase_kEpsilon (adaptatif, maxCo 2), dernier tour : dt médian = {pas(k, tend - T, tend):.2e} s "
          f"(cas à couches : 1,00e-05 s, fixe) -> facteur {pas(k, tend - T, tend) / 1e-5:.1f}")


if __name__ == "__main__":
    main()
