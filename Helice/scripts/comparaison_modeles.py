#!/usr/bin/env python3
"""Comparaison K_T, 10 K_Q, eta_0 des trois fermetures de turbulence sur les tours complets -- LOT 3, 20/09.

Lit les CSV du kit (`Helice/data/perf_<modele>.csv`, D corrigé, colonnes time,n,U_aval,J,KT,10KQ,eta0,tours,angle_deg ;
`J` = avance IMPOSÉE V_inlet/(nD), constante, et `eta0` calculé avec elle -- voir extraire_kit_donnees.py).
Pour chaque modèle, sur une fin COMMUNE t_end = min des fins (les trois séries sont alors comparées
sur les mêmes tours) :
  - moyennes par TOUR COMPLET, ancrées en reculant depuis t_end (dernier tour, avant-dernier, ...),
    PONDÉRÉES PAR LE TEMPS (règle des trapèzes) : le pas de temps de kOmegaSST est adaptatif, une moyenne
    sur les lignes ne serait pas une moyenne temporelle ;
  - amplitude crête-à-crête de K_T dans le dernier tour ;
  - dérive d'un tour au suivant (en % de la moyenne, et en % de l'effet inter-modèles) ;
  - écarts entre modèles sur la fenêtre retenue (le dernier tour complet), rapportés à la dérive.
Aucun verdict ici : le script chiffre, l'interprétation est dans le rapport.

Usage : python3 Helice/scripts/comparaison_modeles.py [--tours 3]
"""
import argparse
import csv
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
CASES = ["kEpsilon", "kOmegaSST", "laminar"]
COLS = ["KT", "10KQ", "eta0"]
T_TRANSIT = 0.001  # même filtre du démarrage impulsif que les autres outils


def lire(case):
    with open(DATA / f"perf_{case}.csv") as f:
        rows = [{k: float(v) for k, v in r.items()} for r in csv.DictReader(f)]
    return [r for r in rows if r["time"] >= T_TRANSIT]


def moyenne_temps(rows, col, t0, t1):
    """Moyenne temporelle (trapèzes) de `col` sur [t0, t1] ; retourne (moyenne, min, max, nb de lignes)."""
    pts = [r for r in rows if t0 - 1e-12 <= r["time"] <= t1 + 1e-12]
    if len(pts) < 3:
        return None
    s = sum(0.5 * (pts[i]["time"] - pts[i - 1]["time"]) * (pts[i][col] + pts[i - 1][col]) for i in range(1, len(pts)))
    d = pts[-1]["time"] - pts[0]["time"]
    v = [p[col] for p in pts]
    return s / d, min(v), max(v), len(pts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tours", type=int, default=3, help="nombre de tours complets à examiner en reculant")
    a = ap.parse_args()
    series = {c: lire(c) for c in CASES}
    import math
    n = 158 / (2 * math.pi)  # dynamicMeshDict : omega / 2 pi (le n du CSV est arrondi à 25,15 : 0,014 % d'écart)
    T = 1.0 / n
    t_end = min(s[-1]["time"] for s in series.values())
    print(f"Fin commune t_end = {t_end:.6f} s ({t_end / T:.3f} tours) ; T = 2 pi / omega = {T:.6f} s (n = {n:.4f} tr/s)")
    for c, s in series.items():
        print(f"  {c:10s} fin de série {s[-1]['time']:.6f} s ({s[-1]['tours']:.3f} tours), {len(s)} lignes")

    tab = {c: {} for c in CASES}  # tab[c][k][col] = moyenne, k = 1 (dernier tour) ... a.tours
    print("\n=== Moyennes par tour complet (pondérées par le temps), en reculant depuis t_end ===")
    print(f"{'tour':<22s}{'fenêtre (s)':<22s}" + "".join(f"{c:>26s}" for c in CASES))
    for col in COLS:
        print(f"-- {col}")
        for k in range(1, a.tours + 1):
            t1, t0 = t_end - (k - 1) * T, t_end - k * T
            ligne = f"  {'dernier' if k == 1 else f'dernier-{k - 1}':<20s}[{t0:.4f} ; {t1:.4f}]  "
            for c in CASES:
                m = moyenne_temps(series[c], col, t0, t1)
                tab[c].setdefault(k, {})[col] = m[0] if m else None
                tab[c][k][col + "_pp"] = (m[2] - m[1]) if m else None
                ligne += f"{m[0]:>18.4f} (pp {m[2] - m[1]:.4f})" if m else f"{'—':>26s}"
            print(ligne)

    print("\n=== Dérive d'un tour au suivant (dernier tour moins avant-dernier) ===")
    eff = {col: max(tab[c][1][col] for c in CASES) - min(tab[c][1][col] for c in CASES) for col in COLS}
    for col in COLS:
        print(f"-- {col} (effet inter-modèles sur le dernier tour : max-min = {eff[col]:.4f})")
        for c in CASES:
            m1, m2 = tab[c][1][col], tab[c][2][col]
            d = m1 - m2
            print(f"  {c:10s} dernier {m1:.4f}  avant-dernier {m2:.4f}  dérive {d:+.4f} = {100 * d / m1:+.2f} % de la moyenne"
                  f" = {100 * d / eff[col]:+.0f} % de l'effet inter-modèles")

    print("\n=== Écarts entre modèles, dernier tour complet ===")
    for col in COLS:
        v = {c: tab[c][1][col] for c in CASES}
        moy = sum(v.values()) / 3
        print(f"-- {col} : " + " ; ".join(f"{c} {v[c]:.4f}" for c in CASES))
        print(f"   max-min = {eff[col]:.4f} = {100 * eff[col] / moy:.1f} % de la moyenne des trois")
        for a_, b_ in (("kOmegaSST", "kEpsilon"), ("laminar", "kEpsilon"), ("laminar", "kOmegaSST")):
            print(f"   {a_} - {b_} : {v[a_] - v[b_]:+.4f} ({100 * (v[a_] - v[b_]) / v[b_]:+.1f} %)")

    print("\n=== Cohérence eta_0 : moyenne de eta_0 contre J K_T / (2 pi K_Q) des moyennes (dernier tour) ===")
    for c in CASES:
        j = moyenne_temps(series[c], "J", t_end - T, t_end)[0]
        e_moy = tab[c][1]["eta0"]
        e_rec = j / (2 * math.pi) * tab[c][1]["KT"] / (tab[c][1]["10KQ"] / 10)
        print(f"  {c:10s} <eta0> = {e_moy:.4f}   eta0(<KT>,<KQ>) = {e_rec:.4f}   J moyen = {j:.4f}")


if __name__ == "__main__":
    main()
