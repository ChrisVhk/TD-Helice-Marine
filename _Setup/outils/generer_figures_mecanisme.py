#!/usr/bin/env python3
"""Figures du bloc « trois axes » de S03 (20/09) : décomposition pression / frottement des écarts, dernier tour complet.
Les nombres viennent de `Helice/scripts/decomposition_pression_frottement.py` (rien n'est saisi à la main).
Chaque barre est une contribution à l'écart, exprimée en % du total de la grandeur de RÉFÉRENCE de la comparaison.
Sorties : Helice/Images/FIG-fon-s7-compensation.png, FIG-fon-s7-deux-causes.png
"""
import contextlib
import io
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RACINE, "Helice", "scripts"))
import decomposition_pression_frottement as dpf  # noqa: E402

TEAL, MARINE, CORAIL = "#1A9988", "#1A346D", "#EB5600"
with contextlib.redirect_stdout(io.StringIO()):
    RES = dpf.main()


def parts(nom, grandeur):
    x = RES[nom][grandeur]
    s = 1 if grandeur == "poussee" else -1
    return s * x["total"], s * x["pression"], s * x["visqueux"]


def ecart(a, b, grandeur):
    ta, pa, va = parts(a, grandeur)
    tb, pb, vb = parts(b, grandeur)
    return 100 * (pa - pb) / tb, 100 * (va - vb) / tb, 100 * (ta - tb) / tb  # % du total de référence b


def panneau(ax, titre, valeurs):
    noms = ["pression", "frottement", "total"]
    couleurs = [MARINE, CORAIL, TEAL]
    barres = ax.bar(noms, valeurs, color=couleurs, width=0.6)
    ax.axhline(0, color="#595959", lw=1)
    for b, v in zip(barres, valeurs):
        ax.text(b.get_x() + b.get_width() / 2, v + (0.08 if v >= 0 else -0.08), f"{v:+.2f} %".replace(".", ",").replace("-", "−"),
                ha="center", va="bottom" if v >= 0 else "top", fontsize=12, fontweight="bold")
    ax.set_title(titre, fontsize=11.5)
    ax.tick_params(labelsize=11)
    ax.set_ylabel("% du total de référence", fontsize=11)
    lim = max(abs(v) for v in valeurs) * 1.45
    ax.set_ylim(-lim, lim)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def figure(sortie, panneaux, suptitre):
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 5.4))
    for ax, (titre, vals) in zip(axes, panneaux):
        panneau(ax, titre, vals)
    fig.tight_layout()
    chemin = os.path.join(RACINE, "Helice", "Images", sortie)
    fig.savefig(chemin, dpi=150)
    plt.close(fig)
    print("OK ->", chemin)


if __name__ == "__main__":
    figure("FIG-fon-s7-compensation.png",
           [("Couple : SST − laminaire\n(deux modèles)", ecart("kOmegaSST", "laminar", "couple")),
            ("Poussée : avec − sans couches\n(deux maillages)", ecart("kEpsilon_layers", "kEpsilon", "poussee"))],
           "Un écart net peut cacher deux grands effets contraires")
    figure("FIG-fon-s7-deux-causes.png",
           [("Changer de modèle\nCouple : k-ε − laminaire", ecart("kEpsilon", "laminar", "couple")),
            ("Changer de maillage de paroi\nCouple : avec − sans couches", ecart("kEpsilon_layers", "kEpsilon", "couple"))],
           "Même grandeur, deux causes, deux chemins")
