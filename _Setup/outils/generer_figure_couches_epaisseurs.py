#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generer_figure_couches_epaisseurs.py — LOT 5, consigne du 15/09, variante (b) de
l'image 06 ("troisième tentative").

Les deux rendus ParaView précédents de l'image 06 ont échoué à montrer la pale ET les
couches de prismes dans une seule vue continue : l'empilement fait environ 1,8 mm pour
un diamètre de pale de 227 mm, soit moins de 1 % — aucune caméra ne peut cadrer les
deux à la fois sans rupture d'échelle. Le rendu 3D (variante a, rendre_vues_helice.py
image_06) rompt l'échelle par DEUX panneaux + un facteur de grossissement écrit.
Cette variante (b) ne montre pas la géométrie du tout : elle trace directement
l'épaisseur de chaque couche en fonction de son rang, quantitatif, ce qu'une image ne
dit jamais.

Aucun calcul, aucun maillage : les six épaisseurs sont la progression géométrique
DEMANDÉE à snappyHexMesh (firstLayerThickness x expansionRatio^rang), lue dans le
dict du cas -- jamais mesurée ni relancée. La couverture RÉELLEMENT obtenue (moyenne
3,71/6 sur propellerTip, 76,8 %) est distincte et sourcée dans
Helice/docs/PARAMETRES_CAS.md -- annotée ici pour contexte, pas recalculée.

Usage : python3 _Setup/outils/generer_figure_couches_epaisseurs.py [--cas case_kEpsilon]
Sortie : Helice/Images/galerie/06b_couches_epaisseurs.png (gitignoré, comme le reste de
la galerie -- régénérable par ce script, jamais à la main).
"""
import argparse
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ICI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(ICI, "..", ".."))

MARINE = "#1A346D"
TEAL = "#1A9988"
RUST = "#C0522D"
GREY = "#595959"


def read_layer_params(case_dir):
    path = os.path.join(case_dir, "system", "snappyHexMeshDict")
    with open(path, encoding="utf-8", errors="ignore") as fh:
        text = fh.read()
    first = float(re.search(r"\bfirstLayerThickness\s+([0-9.eE+-]+)\s*;", text).group(1))
    ratio = float(re.search(r"\bexpansionRatio\s+([0-9.eE+-]+)\s*;", text).group(1))
    n = int(re.search(r'"propeller\.\*"\s*\{\s*nSurfaceLayers\s+(\d+)\s*;', text).group(1))
    return first, ratio, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cas", default="case_kEpsilon")
    args = ap.parse_args()
    case_dir = os.path.join(REPO, "Helice", f"{args.cas}_layers")
    first, ratio, n = read_layer_params(case_dir)

    ranks = list(range(1, n + 1))
    thickness_mm = [first * (ratio ** (i - 1)) * 1000.0 for i in ranks]
    total_mm = sum(thickness_mm)
    cumul_mm = [sum(thickness_mm[:i]) for i in ranks]

    fig, ax = plt.subplots(figsize=(9.0, 5.5), dpi=200)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ax.bar(ranks, thickness_mm, color=TEAL, width=0.55, label="épaisseur de la couche (rang $i$)")
    ax.plot(ranks, cumul_mm, color=MARINE, marker="o", lw=1.6, label="épaisseur cumulée")

    for i, (t, c) in enumerate(zip(thickness_mm, cumul_mm), start=1):
        ax.annotate(f"{t:.3f}", (i, t), textcoords="offset points", xytext=(0, 6),
                    ha="center", fontsize=9, color=MARINE)

    ax.set_xlabel("Rang de la couche (depuis la paroi)", fontsize=12, color=MARINE)
    ax.set_ylabel("Épaisseur [mm]", fontsize=12, color=MARINE)
    ax.set_xticks(ranks)
    ax.set_title(
        f"Couches de prismes DEMANDÉES — {n} couches, ratio d'expansion {ratio:g},\n"
        f"épaisseur totale visée {total_mm:.3f} mm (première couche {first*1000:.3g} mm)",
        fontsize=12.5, color=MARINE, fontweight="bold", pad=14,
    )
    ax.grid(True, axis="y", alpha=0.3)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(GREY)
    ax.tick_params(colors=GREY, labelsize=10)

    legend = ax.legend(loc="upper left", fontsize=10, frameon=False)
    for text in legend.get_texts():
        text.set_color(MARINE)

    fig.tight_layout(rect=(0, 0.09, 1, 1))
    fig.text(
        0.02, 0.01,
        "Obtenu réellement sur propellerTip : 3,71/6 couches, 76,8 % — voir "
        "Helice/docs/PARAMETRES_CAS.md (source : log.snappyHexMesh.tipedge). "
        "Ci-dessus : progression DEMANDÉE, pas la couverture obtenue.",
        fontsize=8.5, color=RUST, va="bottom", ha="left", wrap=True,
    )
    out = os.path.join(REPO, "Helice", "Images", "galerie", "06b_couches_epaisseurs.png")
    fig.savefig(out, facecolor="white", bbox_inches="tight")
    print("écrit :", out)


if __name__ == "__main__":
    main()
