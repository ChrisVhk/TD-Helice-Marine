#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generer_figure_spectre.py — Correctif A3 (deck V2, 07/09).

Spectre de K_T (dernier tour complet) pour les deux cas sains distribués en séance 1
(kEpsilon, laminaire — PAS kOmegaSST, exclu de toute mesure de fréquence depuis le LOT 0A du
06/09), avec les harmoniques n/2n/3n/4n repérées et la case de résolution FFT matérialisée
(largeur = 1/durée de la fenêtre). Rend visuel le calcul attendu en question (b) de la diapo
« Les trois pales » : ne PAS résoudre la question à l'avance -- cette figure est une diapo de
REVEAL, à montrer seulement après que les binômes ont proposé leur propre calcul, jamais avant
(cf. notes d'orateur de la diapo qui la porte).

Méthode identique à celle du diagnostic LOT 0A (STATUT.md, 06/09) : ré-échantillonnage sur le
pas de temps natif du dernier tour, fenêtre de Hann, FFT réelle -- pas une FFT brute sur un
signal à pas adaptatif (biaiserait la position des raies).

Usage : python3 generer_figure_spectre.py
Sortie : Helice/Images/FIG-fon-s7-spectre-KT.png
"""
import os
import csv
import math

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ICI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(ICI, "..", ".."))
HELICE = os.path.join(REPO, "Helice")
DATA = os.path.join(HELICE, "data")
OUT = os.path.join(HELICE, "Images", "FIG-fon-s7-spectre-KT.png")

MARINE = "#1A346D"
TEAL = "#1A9988"
RUST = "#C0522D"
GREY = "#595959"
PALE = "#A9D5E2"

CASES = [
    ("perf_kEpsilon.csv", "k-ε", MARINE),
    ("perf_laminar.csv", "laminaire", RUST),
]


def load(fname):
    t, kt, n = [], [], None
    with open(os.path.join(DATA, fname), newline="") as f:
        for row in csv.DictReader(f):
            t.append(float(row["time"]))
            kt.append(float(row["KT"]))
            n = float(row["n"])
    return np.array(t), np.array(kt), n


def spectrum_last_revolution(t, kt, n):
    T = 1.0 / n
    t_end = t[-1]
    mask = t >= (t_end - T)
    tw, ktw = t[mask], kt[mask]
    dt_native = np.median(np.diff(t[t < t[0] + 0.005]))
    tu = np.arange(tw[0], tw[-1], dt_native)
    ktu = np.interp(tu, tw, ktw)
    ktu = ktu - ktu.mean()
    win = np.hanning(len(ktu))
    spec = np.abs(np.fft.rfft(ktu * win))
    freqs = np.fft.rfftfreq(len(ktu), d=dt_native)
    window_duration = tw[-1] - tw[0]
    return freqs, spec, window_duration


fig, ax = plt.subplots(figsize=(12.5, 5.6), dpi=200)
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

n_ref = None
resolution = None
n_cases = len(CASES)
for idx, (fname, label, color) in enumerate(CASES):
    t, kt, n = load(fname)
    n_ref = n
    freqs, spec, window_duration = spectrum_last_revolution(t, kt, n)
    resolution = 1.0 / window_duration
    keep = freqs <= 130
    # Bâtons, pas une ligne continue : avec ~25 Hz d'écart entre bins FFT, relier les points
    # par des droites (essayé en premier -- trouvé trompeur à l'œil, règle de la boucle 10 sur
    # une figure) suggère une résolution en fréquence qui n'existe pas. Un bâton par bin réel,
    # décalé horizontalement entre cas pour rester lisible, est la représentation honnête d'un
    # spectre aussi grossièrement échantillonné.
    offset = (idx - (n_cases - 1) / 2) * 1.2
    ax.vlines(freqs[keep] + offset, 0, spec[keep], color=color, lw=3, alpha=0.85, label=label)
    ax.plot(freqs[keep] + offset, spec[keep], "o", color=color, ms=4)

# harmoniques n, 2n, 3n, 4n
for k in range(1, 5):
    f = k * n_ref
    ax.axvline(f, color=GREY, lw=0.9, ls="--", alpha=0.6)
    ax.annotate(f"{k}n\n{f:.1f} Hz", xy=(f, ax.get_ylim()[1]), xytext=(f, 0),
                textcoords="data", ha="center", va="bottom", fontsize=9.5, color=GREY)

# case de resolution : bande grisee de largeur = resolution, centree sur 3n (75,44 Hz)
f3n = 3 * n_ref
ax.axvspan(f3n - resolution / 2, f3n + resolution / 2, color=PALE, alpha=0.6, zorder=0)
ax.annotate(
    f"case de résolution\n1/(durée fenêtre) ≈ {resolution:.1f} Hz",
    xy=(f3n, 0), xytext=(f3n + 18, ax.get_ylim()[1] * 0.55 if ax.get_ylim()[1] else 1),
    fontsize=10, color=MARINE, ha="left",
    arrowprops=dict(arrowstyle="->", color=MARINE, lw=1),
)

ax.set_xlim(0, 130)
ax.set_xlabel("Fréquence [Hz]", fontsize=13, color=MARINE)
ax.set_ylabel(r"Amplitude $|\widehat{K_T}|$ (u.a.)", fontsize=13, color=MARINE)
ax.set_title(
    "Spectre de $K_T$ — dernier tour complet (kit séance 1)",
    fontsize=14, color=MARINE, fontweight="bold", pad=32,
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
print(f"résolution = {resolution:.3f} Hz, 3n = {f3n:.3f} Hz")
