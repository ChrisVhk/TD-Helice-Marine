#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generer_figure_couches_epaisseurs.py — LOT 5 (14/09), corrigé LOT 2 (15/09).

Les deux rendus ParaView de l'image 06 échouaient à montrer la pale ET les couches de
prismes dans une seule vue continue : l'empilement fait environ 1,8 mm pour un diamètre
de pale de 227 mm, soit moins de 1 % -- aucune caméra ne peut cadrer les deux à la fois
sans rupture d'échelle. Cette variante (b) ne montre pas la géométrie du tout : elle
trace directement l'épaisseur de chaque couche en fonction de son rang, quantitatif, ce
qu'une image ne dit jamais.

Aucun calcul, aucun maillage : les six épaisseurs DEMANDÉES sont la progression
géométrique lue dans le dict du cas (firstLayerThickness x expansionRatio^rang) --
jamais mesurée ni relancée. La série OBTENUE (LOT 2, 15/09) trace le même calcul
tronqué à la couverture RÉELLEMENT mesurée sur propellerTip (3,71/6 couches en
moyenne, 76,8 % -- source Helice/docs/PARAMETRES_CAS.md, log.snappyHexMesh.tipedge) :
couches 1 à 3 pleines, couche 4 à 71 % de sa hauteur DEMANDÉE, couches 5 et 6 absentes
-- c'est une simplification pédagogique (la couverture réelle n'est pas uniforme
couche par couche, seule sa MOYENNE est mesurée), dite comme telle dans la légende.

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
from matplotlib.ticker import FuncFormatter

ICI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(ICI, "..", ".."))

MARINE = "#1A346D"
TEAL = "#1A9988"
RUST = "#C0522D"
GREY = "#595959"

# Couverture RÉELLEMENT mesurée sur propellerTip (log.snappyHexMesh.tipedge, voir
# Helice/docs/PARAMETRES_CAS.md) -- constante, jamais recalculée ici.
COUCHES_OBTENUES = 3.71


def fr(x, nd=3):
    """Formatage décimal français (virgule) -- cohérence typographique (LOT 2, 15/09)."""
    return f"{x:.{nd}f}".replace(".", ",")


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
    demande_mm = [first * (ratio ** (i - 1)) * 1000.0 for i in ranks]
    total_demande_mm = sum(demande_mm)
    cumul_mm = [sum(demande_mm[:i]) for i in ranks]

    # Série OBTENUE : couches pleines jusqu'à floor(COUCHES_OBTENUES), une couche
    # partielle (fraction), le reste absent -- voir docstring.
    obtenu_mm = []
    reste = COUCHES_OBTENUES
    for t in demande_mm:
        if reste <= 0:
            obtenu_mm.append(0.0)
        elif reste >= 1:
            obtenu_mm.append(t)
            reste -= 1
        else:
            obtenu_mm.append(t * reste)
            reste = 0.0
    total_obtenu_mm = sum(obtenu_mm)

    # Aspect ~2,68:1 choisi le 15/09 pour correspondre au placeholder PICTURE réel de
    # la disposition Figure (11,93 x 4,45 in dans TEMPLATE_ENSM_cours.pptx) --
    # python-pptx recadre (crop-to-fill) une image dont l'aspect ne correspond pas,
    # un premier essai plus carre (9,5x5,8, aspect 1,64) perdait le titre et la
    # légende, coupés en haut.
    fig, ax = plt.subplots(figsize=(13.4, 5.0), dpi=200)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    width = 0.38
    ax.bar([i - width / 2 for i in ranks], demande_mm, width=width, color=TEAL,
           label="épaisseur DEMANDÉE (rang $i$)")
    ax.bar([i + width / 2 for i in ranks], obtenu_mm, width=width, color=RUST,
           label=f"épaisseur OBTENUE (moyenne {fr(COUCHES_OBTENUES, 2)}/{n} couches)")
    ax.plot(ranks, cumul_mm, color=MARINE, marker="o", lw=1.6,
            label="épaisseur cumulée DEMANDÉE")

    for i, t in zip(ranks, demande_mm):
        ax.annotate(fr(t), (i - width / 2, t), textcoords="offset points", xytext=(0, 5),
                    ha="center", fontsize=8.5, color=TEAL)
    for i, t in zip(ranks, obtenu_mm):
        if t > 0:
            ax.annotate(fr(t), (i + width / 2, t), textcoords="offset points", xytext=(0, 5),
                        ha="center", fontsize=8.5, color=RUST)

    ax.set_xlabel("Rang de la couche (depuis la paroi)", fontsize=12, color=MARINE)
    ax.set_ylabel("Épaisseur [mm]", fontsize=12, color=MARINE)
    ax.set_xticks(ranks)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _pos: fr(v, 2)))
    # ATTENTION (trouve en verifiant avant livraison, LOT 2 du 15/09) : la somme des
    # barres "obtenue" (total_obtenu_mm, {fr(total_obtenu_mm)} mm ici) est un ARTEFACT
    # de la troncature schematique ci-dessous, PAS la mesure reelle -- elle ne doit
    # jamais apparaitre dans le titre comme si elle en etait une. La seule epaisseur
    # obtenue REELLEMENT mesuree est 76,8% de la totale visee (voir legende du bas),
    # et les deux ne se recoupent pas exactement (la couverture n'est pas uniforme
    # couche par couche ; seule sa moyenne globale est mesuree).
    ax.set_title(
        f"Couches de prismes : DEMANDÉ contre OBTENU (propellerTip)",
        fontsize=15, color=MARINE, fontweight="bold", pad=14, loc="center",
    )
    ax.grid(True, axis="y", alpha=0.3)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(GREY)
    ax.tick_params(colors=GREY, labelsize=10)

    legend = ax.legend(loc="upper left", fontsize=9.5, frameon=False)
    for text in legend.get_texts():
        text.set_color(MARINE)

    # Marge de securite gauche/droite (le crop-to-fill de python-pptx grignote un
    # peu les bords meme a aspect quasi identique -- constate le 15/09, le titre
    # perdait son "C" initial et sa derniere decimale sans cette marge).
    fig.tight_layout(rect=(0.02, 0.17, 0.98, 1))
    caption = (
        f"{n} couches visées, ratio d'expansion {fr(ratio, 1)}, épaisseur totale visée {fr(total_demande_mm)} mm.\n"
        f"Mesuré (seule valeur réelle) : {fr(COUCHES_OBTENUES, 2)}/{n} couches en moyenne, 76,8 % de l'épaisseur totale visée (source : Helice/docs/PARAMETRES_CAS.md, log.snappyHexMesh.tipedge).\n"
        f"La série « obtenue » ci-dessus (troncature couches 1-3 pleines, 4 à 71 %, 5-6 absentes) est une ILLUSTRATION schématique du compte de couches, pas une reconstruction d'épaisseur —\n"
        f"sa somme ne vaut PAS 76,8 % de la totale visée (la couverture réelle n'est pas uniforme couche par couche, seule sa moyenne globale est mesurée)."
    )
    fig.text(0.02, 0.01, caption, fontsize=9.5, color=RUST, va="bottom", ha="left")
    # PAS de bbox_inches="tight" : ça recadre au contenu reel et change l'aspect
    # (constate le 15/09 -- l'aspect obtenu, 2,89, derivait du 2,68 vise, a cause de
    # ce recadrage). La taille de figure EXACTE (13,4x5,0 = 2,68) doit survivre
    # telle quelle pour correspondre au placeholder PICTURE du gabarit.
    out = os.path.join(REPO, "Helice", "Images", "galerie", "06b_couches_epaisseurs.png")
    fig.savefig(out, facecolor="white")
    print("écrit :", out)


if __name__ == "__main__":
    main()
