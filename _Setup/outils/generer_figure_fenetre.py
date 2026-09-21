#!/usr/bin/env python3
"""Deux figures pour la séance 2 : l'écart entre modèles contre l'amplitude de l'oscillation de K_T, selon la FENÊTRE de lecture.

  FIG-fon-s7-ecart-amplitude-dernier-tour.png     : K_T des trois fermetures sur le dernier tour complet, ordonnée de largeur fixée.
  FIG-fon-s7-ecart-amplitude-deux-fenetres.png    : le même calcul lu sur deux fenêtres (de 0,5 à 1,5 tour, puis dernier tour), MÊME largeur d'ordonnée.

Lit `Helice/data/perf_<modele>.csv` (colonnes `tours`, `KT`) ; aucun chiffre n'est recopié : amplitudes (maximum moins minimum) et écart entre
modèles (moyennes pondérées par le temps, dernier tour complet) sont calculés ici, et imprimés pour être comparés à `PARAMETRES_CAS.md`.
Usage : python3 _Setup/outils/generer_figure_fenetre.py
"""
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "Helice" / "Images"
MODELES = [("kEpsilon", "k-ε", "#1f77b4"), ("kOmegaSST", "k-ω SST", "#d62728"), ("laminar", "laminaire", "#2ca02c")]
T = 2 * math.pi / 158
N = 158 / (2 * math.pi)
LARGEUR_Y = 0.04  # même largeur d'ordonnée dans tous les panneaux : les amplitudes se comparent à l'oeil
plt.rcParams.update({"font.size": 15, "axes.titlesize": 15, "axes.labelsize": 15, "legend.fontsize": 13})

donnees = {}
for m, _, _ in MODELES:
    d = pd.read_csv(ROOT / "Helice" / "data" / f"perf_{m}.csv")
    donnees[m] = d[d.time >= 0.001]
t_fin = min(d.time.iloc[-1] for d in donnees.values())


def fenetre(d, a, b):
    return d[(d.time >= a - 1e-12) & (d.time <= b + 1e-12)]


def moyenne_temps(w):
    return np.trapz(w.KT, w.time) / (w.time.iloc[-1] - w.time.iloc[0])


def virgule(x, nd):
    return f"{x:.{nd}f}".replace(".", ",")


def panneau(ax, a, b, titre):
    ws = {m: fenetre(d, a, b) for m, d in donnees.items()}
    milieu = np.mean([w.KT.mean() for w in ws.values()])
    for m, nom, c in MODELES:
        ax.plot(ws[m].time * N, ws[m].KT, color=c, lw=1.1, label=nom)
    ax.set_ylim(milieu - LARGEUR_Y / 2, milieu + LARGEUR_Y / 2)
    ax.set_xlim(a * N, b * N)
    ax.set_xlabel("Tours")
    ax.grid(True, alpha=0.3)
    virg = FuncFormatter(lambda x, _: f"{x:g}".replace(".", ","))
    ax.xaxis.set_major_formatter(virg); ax.yaxis.set_major_formatter(virg)
    amp = [w.KT.max() - w.KT.min() for w in ws.values()]
    ax.set_title(titre + f"\namplitude de $K_T$ : {virgule(min(amp), 4 if min(amp) < 0.01 else 3)} à {virgule(max(amp), 4 if max(amp) < 0.01 else 3)}", loc="left")
    return ws, amp


t0d = t_fin - T
w_dernier = {m: fenetre(d, t0d, t_fin) for m, d in donnees.items()}
moy = {m: moyenne_temps(w) for m, w in w_dernier.items()}
ecart = max(moy.values()) - min(moy.values())
amp_dernier = [w.KT.max() - w.KT.min() for w in w_dernier.values()]
print(f"dernier tour [{t0d:.6f} ; {t_fin:.6f}] : K_T moyens {', '.join(f'{v:.4f}' for v in moy.values())} ; écart {ecart:.4f} ; amplitudes {', '.join(f'{v:.4f}' for v in amp_dernier)}")

# --- figure 1 : dernier tour
fig, ax = plt.subplots(figsize=(7.4, 5.4))
panneau(ax, t0d, t_fin, "Dernier tour complet")
ax.set_ylabel("$K_T$")
ax.text(0.98, 0.04, f"écart entre les moyennes des trois fermetures : {virgule(ecart, 4)}", transform=ax.transAxes, ha="right", fontsize=13)
ax.legend(loc="upper left")
fig.tight_layout()
fig.savefig(OUT / "FIG-fon-s7-ecart-amplitude-dernier-tour.png", dpi=150, facecolor="white")
plt.close(fig)

# --- figure 2 : deux fenêtres, même largeur d'ordonnée
fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.4))
_, amp_a = panneau(axes[0], 0.5 * T, 1.5 * T, "Du demi-tour au tour et demi")
_, amp_b = panneau(axes[1], t0d, t_fin, "Dernier tour complet")
axes[0].set_ylabel("$K_T$")
axes[0].legend(loc="upper right")
axes[1].text(0.98, 0.04, f"écart entre modèles : {virgule(ecart, 4)}", transform=axes[1].transAxes, ha="right", fontsize=13)
axes[0].text(0.98, 0.04, f"écart entre modèles : {virgule(ecart, 4)}", transform=axes[0].transAxes, ha="right", fontsize=13)
fig.text(0.01, 0.005, "Même largeur d'ordonnée (0,04) dans les deux panneaux.", fontsize=11, color="#555555", va="bottom")
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(OUT / "FIG-fon-s7-ecart-amplitude-deux-fenetres.png", dpi=150, facecolor="white")
plt.close(fig)
print(f"fenêtre A [{0.5 * T:.6f} ; {1.5 * T:.6f}] : amplitudes {', '.join(f'{v:.4f}' for v in amp_a)}")
print("écrit : FIG-fon-s7-ecart-amplitude-dernier-tour.png, FIG-fon-s7-ecart-amplitude-deux-fenetres.png")
