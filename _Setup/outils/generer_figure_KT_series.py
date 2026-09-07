#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generer_figure_KT_series.py — Correctif A1 (deck V2, 07/09).

Série temporelle de K_T, les 3 cas superposés, axe des temps en TOURS (t/T, T = 1/n) plutôt
qu'en secondes -- lisible sans connaître la valeur de n. Source : data/perf_*.csv (les données
distribuées aux étudiants, pas un recalcul depuis les cas OpenFOAM bruts).

Le tout premier instant (démarrage impulsif) produit un pic de K_T de plusieurs centaines
d'ordres au-dessus du régime établi (cf. data/README.md) -- exclu de l'affichage comme le fait
déjà scripts/bilan_helice.py (T_TRANSIENT_SKIP = 0,001 s), sinon l'échelle utile est écrasée.

Usage : python3 generer_figure_KT_series.py
Sortie : Helice/Images/FIG-fon-s7-KT-series-tours.png
"""
import os
import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ICI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(ICI, "..", ".."))
HELICE = os.path.join(REPO, "Helice")
DATA = os.path.join(HELICE, "data")
OUT = os.path.join(HELICE, "Images", "FIG-fon-s7-KT-series-tours.png")

MARINE = "#1A346D"
TEAL = "#1A9988"
RUST = "#C0522D"
GREY = "#595959"

CASES = [
    ("perf_kEpsilon.csv", "k-ε", MARINE),
    ("perf_kOmegaSST.csv", "k-ω SST", TEAL),
    ("perf_laminar.csv", "laminaire", RUST),
]
T_TRANSIENT_SKIP = 0.001  # s -- même seuil que scripts/bilan_helice.py


def load(fname):
    t, kt, n = [], [], None
    with open(os.path.join(DATA, fname), newline="") as f:
        for row in csv.DictReader(f):
            time = float(row["time"])
            if time < T_TRANSIENT_SKIP:
                continue
            t.append(time)
            kt.append(float(row["KT"]))
            n = float(row["n"])
    return t, kt, n


def break_gaps(t, kt, factor=5):
    """Insère un trou (None) là où l'écart de temps dépasse `factor` fois l'écart médian --
    sinon matplotlib relie deux points de part et d'autre d'un trou réel par une ligne droite,
    qui ressemblerait à une mesure alors que c'est une absence de données (cas kOmegaSST, trou
    connu 0,0082->0,0220 s, incident disque du 05/09 -- LOT 0A). Trouvé à l'œil sur la première
    version de cette figure : la ligne droite entre ~0,2 et ~0,55 tour n'avait rien de physique."""
    if len(t) < 3:
        return t, kt
    diffs = [t[i + 1] - t[i] for i in range(len(t) - 1)]
    diffs_sorted = sorted(diffs)
    median = diffs_sorted[len(diffs_sorted) // 2]
    out_t, out_kt = [t[0]], [kt[0]]
    for i in range(1, len(t)):
        if t[i] - t[i - 1] > factor * median:
            out_t.append(None)
            out_kt.append(None)
        out_t.append(t[i])
        out_kt.append(kt[i])
    return out_t, out_kt


fig, ax = plt.subplots(figsize=(12.5, 5.2), dpi=200)
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

for fname, label, color in CASES:
    t, kt, n = load(fname)
    T = 1.0 / n
    tours = [x / T for x in t]
    tours, kt = break_gaps(tours, kt)
    ax.plot(tours, kt, lw=1.1, color=color, label=label)

ax.set_xlabel("Temps [tours d'hélice]", fontsize=13, color=MARINE)
ax.set_ylabel(r"$K_T$", fontsize=14, color=MARINE)
ax.set_title(
    "Coefficient de poussée $K_T$ au cours du calcul — les trois fermetures",
    fontsize=14, color=MARINE, fontweight="bold", pad=12,
)
ax.grid(True, alpha=0.3)
ax.tick_params(colors=GREY, labelsize=11)
for spine in ("top", "right"):
    ax.spines[spine].set_visible(False)
for spine in ("left", "bottom"):
    ax.spines[spine].set_color(GREY)

legend = ax.legend(loc="upper right", fontsize=12, frameon=False)
for text in legend.get_texts():
    text.set_color(MARINE)

fig.tight_layout()
fig.savefig(OUT, facecolor="white", bbox_inches="tight")
print("écrit :", OUT)
