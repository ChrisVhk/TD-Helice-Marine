#!/usr/bin/env python3
"""Décomposition pression / frottement de la poussée et du couple, dernier tour complet -- 20/09.

Lit les fonctions `forces` (force.dat, moment.dat : colonnes Time, total xyz, pression xyz, visqueux xyz) des quatre cas, RECOLLE les segments de reprise
(règle de compare_turbulence.recoller : le segment le plus récent remplace tout ce qui est >= son premier temps), et moyenne sur le dernier tour complet
[t_fin - T ; t_fin] avec T = 2 pi / omega (omega = 158 rad/s), moyennes pondérées par le temps (trapèzes). Composante selon l'axe (y). Rien n'est recalculé :
lecture seule des colonnes déjà écrites par OpenFOAM. Contrôles imprimés : pression + visqueux = total ; couple total -> 10 K_Q et poussée -> K_T comparés aux
valeurs des propellerPerformance.dat du même cas sur la même fenêtre.

Usage : python3 Helice/scripts/decomposition_pression_frottement.py            (tableau des moyennes du dernier tour)
        python3 Helice/scripts/decomposition_pression_frottement.py --csv     (écrit Helice/data/decomposition_<modele>.csv, séance 3, seconde partie)
"""
import argparse
import glob
import math
import os
import re

import numpy as np

HELICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OMEGA = 158.0
T = 2 * math.pi / OMEGA
N = 25.15  # n de system/propellerInfo (arrondi) : c est lui qui donne les K_T, 10K_Q publiés ; 158/2pi = 25,1465 donnerait +0,028 %
D = 0.227378
RHO = 1.0  # `forces` : rhoInf 1 (cinématique) ; K_T = F / (n^2 D^4), K_Q = Q / (n^2 D^5) avec la même normalisation que propellerInfo (rho s'annule)
CASES = {
    "kEpsilon": {"dir": "case_kEpsilon", "fichiers": {"force": ["0.06/force.dat"], "moment": ["0.06/moment.dat"]}},
    "kOmegaSST": {"dir": "case_kOmegaSST", "fichiers": {"force": ["0.06/force_0.06.dat", "0.143/force.dat"],
                                                          "moment": ["0.06/moment_0.06.dat", "0.143/moment.dat"]}},
    "laminar": {"dir": "case_laminar", "fichiers": {"force": ["0.06/force_0.06.dat"], "moment": ["0.06/moment_0.06.dat"]}},
    "kEpsilon_layers": {"dir": "case_kEpsilon_layers", "fichiers": {"force": ["0/force_0.dat"], "moment": ["0/moment_0.dat"]}},
}


def lire(chemin):
    lignes = []
    for l in open(chemin, encoding="utf-8", errors="replace"):
        if l.startswith("#") or not l.strip():
            continue
        v = re.split(r"\s+", l.replace("(", " ").replace(")", " ").strip())
        lignes.append([float(x) for x in v[:10]])
    return np.array(lignes)


def recoller(segments):
    """segments : liste de tableaux ordonnés du plus ancien au plus récent ; le plus récent remplace tout ce qui est >= son premier temps."""
    out = segments[0]
    for seg in segments[1:]:
        out = np.vstack([out[out[:, 0] < seg[0, 0]], seg])
    return out


def moyenne(S, col, t0, t1):
    s = S[(S[:, 0] >= t0 - 1e-12) & (S[:, 0] <= t1 + 1e-12)]
    return np.trapz(s[:, col], s[:, 0]) / (s[-1, 0] - s[0, 0])


T_CSV_DEBUT = 0.06  # les fonctions `forces` sont continues sur les trois cas à partir de 0,06 s (laminar : trou 0,0475-0,058 s avant)
ENTETE_CSV = ("# Séparation pression / frottement = façon dont la force arrive à la paroi (contrainte normale / cisaillement tangentiel), "
              "PAS portance / traînée. Composante selon l'axe de rotation, sans dimension (normalisation de perf_*.csv : n = 25,15 tr/s, D = 0,227378 m) ; "
              "couple = 10 K_Q, poussée = K_T ; total = pression + frottement. Lire avec pandas.read_csv(fichier, comment='#').")


def ecrire_csv():
    fK_T = 1.0 / (N ** 2 * D ** 4)
    fK_Q = 10.0 / (N ** 2 * D ** 5)
    for nom in ("kEpsilon", "kOmegaSST", "laminar"):
        c = CASES[nom]
        d = os.path.join(HELICE, c["dir"], "postProcessing", "forces")
        F = recoller([lire(os.path.join(d, f)) for f in c["fichiers"]["force"]])
        M = recoller([lire(os.path.join(d, f)) for f in c["fichiers"]["moment"]])
        F = F[F[:, 0] >= T_CSV_DEBUT]
        M = M[M[:, 0] >= T_CSV_DEBUT]
        assert len(F) == len(M) and np.allclose(F[:, 0], M[:, 0], atol=1e-9), f"{nom} : temps de force.dat et moment.dat différents"
        chemin = os.path.join(HELICE, "data", f"decomposition_{nom}.csv")
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(ENTETE_CSV + "\n")
            f.write("temps_s,tours,couple_10KQ_total,couple_10KQ_pression,couple_10KQ_frottement,poussee_KT_total,poussee_KT_pression,poussee_KT_frottement\n")
            for t, ff, mm in zip(F[:, 0], F, M):
                f.write(f"{t:.7g},{t * OMEGA / (2 * math.pi):.6f},{-mm[2] * fK_Q:.6f},{-mm[5] * fK_Q:.6f},{-mm[8] * fK_Q:.6f},"
                        f"{ff[2] * fK_T:.6f},{ff[5] * fK_T:.6f},{ff[8] * fK_T:.6f}\n")
        print(f"écrit : {chemin} ({len(F)} lignes, t de {F[0, 0]:.6f} à {F[-1, 0]:.6f} s)")


def main():
    res = {}
    for nom, c in CASES.items():
        d = os.path.join(HELICE, c["dir"], "postProcessing", "forces")
        F = recoller([lire(os.path.join(d, f)) for f in c["fichiers"]["force"]])
        M = recoller([lire(os.path.join(d, f)) for f in c["fichiers"]["moment"]])
        t1 = min(F[-1, 0], M[-1, 0]); t0 = t1 - T
        # continuité de l'horloge dans la fenêtre : plus grand saut de temps
        saut = max(np.diff(F[(F[:, 0] >= t0) & (F[:, 0] <= t1), 0]).max(), np.diff(M[(M[:, 0] >= t0) & (M[:, 0] <= t1), 0]).max())
        r = {"t0": t0, "t1": t1, "saut": saut}
        for grandeur, S in (("poussee", F), ("couple", M)):
            tot, pre, vis = (moyenne(S, k, t0, t1) for k in (2, 5, 8))
            s = S[(S[:, 0] >= t0) & (S[:, 0] <= t1)]
            r[grandeur] = {"total": tot, "pression": pre, "visqueux": vis,
                           "ecart_somme_max": float(np.max(np.abs(s[:, 5] + s[:, 8] - s[:, 2]) / np.abs(s[:, 2])))}
        # contrôles contre propellerPerformance
        pp = sorted(glob.glob(os.path.join(HELICE, c["dir"], "postProcessing", "propellerInfo1", "*", "propellerPerformance*.dat")))
        res[nom] = r
        r["pp"] = pp
    # propellerPerformance de référence : mêmes segments que les CSV (kit)
    import csv
    for nom, fichier in (("kEpsilon", "perf_kEpsilon.csv"), ("kOmegaSST", "perf_kOmegaSST.csv"), ("laminar", "perf_laminar.csv")):
        rows = [{k: float(v) for k, v in x.items()} for x in csv.DictReader(open(os.path.join(HELICE, "data", fichier)))]
        rows = np.array([[x["time"], x["KT"], x["10KQ"]] for x in rows if x["time"] >= 0.001])
        res[nom]["KT_pp"] = moyenne(rows, 1, res[nom]["t0"], res[nom]["t1"]); res[nom]["KQ_pp"] = moyenne(rows, 2, res[nom]["t0"], res[nom]["t1"])
    # layers : fichier final propellerPerformance_0.dat (D corrigé dans le segment)
    lp = os.path.join(HELICE, "case_kEpsilon_layers", "postProcessing", "propellerInfo1", "0", "propellerPerformance_0.dat")
    P = np.array([[float(x) for x in l.split()] for l in open(lp) if l.strip() and not l.startswith("#")])
    res["kEpsilon_layers"]["KT_pp"] = moyenne(P[:, [0, 4]], 1, res["kEpsilon_layers"]["t0"], res["kEpsilon_layers"]["t1"])
    res["kEpsilon_layers"]["KQ_pp"] = moyenne(P[:, [0, 5]], 1, res["kEpsilon_layers"]["t0"], res["kEpsilon_layers"]["t1"])

    fK_T = 1.0 / (N ** 2 * D ** 4)
    fK_Q = 10.0 / (N ** 2 * D ** 5)
    print(f"T = {T:.6f} s ; n = {N:.4f} tr/s ; D = {D} m\n")
    for nom, r in res.items():
        print(f"== {nom} : fenêtre [{r['t0']:.6f} ; {r['t1']:.6f}] s, plus grand saut de temps {r['saut']:.2e} s")
        for g, fac, cle in (("poussee", fK_T, "KT_pp"), ("couple", fK_Q, "KQ_pp")):
            x = r[g]; sgn = 1 if g == "poussee" else -1
            tot, pre, vis = sgn * x["total"], sgn * x["pression"], sgn * x["visqueux"]
            print(f"  {g:8s} total {tot:+.6f}  pression {pre:+.6f}  visqueux {vis:+.6f}  | part visqueuse {100 * vis / tot:6.2f} % | p+v-total {pre + vis - tot:+.1e} (écart ligne à ligne max {100 * x['ecart_somme_max']:.4f} %)"
                  f" | {'K_T' if g == 'poussee' else '10K_Q'} déduit {fac * tot:.5f} contre propellerPerformance {r[cle]:.5f} ({100 * (fac * tot / r[cle] - 1):+.3f} %)")
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", action="store_true")
    if ap.parse_args().csv:
        ecrire_csv()
    else:
        main()
