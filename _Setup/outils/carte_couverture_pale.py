#!/usr/bin/env python3
"""Carte de couverture des couches sur UNE pale, vue « développée » -- consigne du 20/09, volet A.

Remplace les coupes trop zoomées (`rendre_couches_pale.py`, fenêtre 14 x 10 mm : on n'y voit que des
tétraèdres de fond) par une carte pleine-pale, toute la zone 0,7R-1,0R lisible d'un coup d'œil.

Par cas : les faces des patches `propellerTip` et `propellerTipEdge` d'UNE pale (celle dont l'azimut est
le plus proche de +x, même principe que `rendre_couches_pale.centre_de_coupe`), placées à
  x = r/R,   y = position tangentielle développée (mm) = (theta - theta_pale(r)) * r,
où theta_pale(r) est l'azimut médian de la pale à ce rayon (suivi de bande en bande : la pale est
gauchie, l'azimut de son milieu dérive avec r ; centrer à chaque r enlève ce gauchissement).
ATTENTION à la lecture : y est un arc autour de l'axe, PAS la corde de la pale (la corde a aussi une
composante axiale) ; deux colonnes séparent les deux flancs par le signe de la composante axiale de la
normale, sans quoi extrados et intrados se superposent en vue axiale.
Couleur : vert = 1re couche présente (épaisseur normale de la cellule voisine h < 0,4 mm), rouge sinon ;
gris = patch `propellerTipEdge`, SANS couches par décision du 13/09 (les colorer en rouge dirait
faussement « échec »). Taille du marqueur = taille réelle de la face.
Indicateur : h = V_cellule / aire_face (voir mesurer_couches_pale.py) -- il présume une première
couche de 0,18 mm et ne compte pas les couches suivantes.

Figure 2 : % de faces avec 1re couche en fonction de r/R (bandes de 0,01), une courbe par cas.

Sortie : Helice/Images/_brouillon/ (gitignoré ; à ne pas committer avant validation visuelle).

Usage :
    python3 _Setup/outils/carte_couverture_pale.py \
        --cas production=Helice/case_kEpsilon_layers --cas combo=Helice/case_kEpsilon_layers_test-combo
Un cas sans constant/V est préparé sur une COPIE (jamais le cas lui-même) dans --copies.
"""
import argparse
import math
import os
import sys
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mesurer_couches_pale as mc  # noqa: E402
import mesurer_vide_pale as mv  # noqa: E402

R = mv.R_DEFAUT
SEUIL_MM = mc.SEUIL_MM
VERT, ROUGE, GRIS = "#2e9e44", "#d62728", "#b0b0b0"
BORNES = (0.70, 1.01)
PAS = 0.01
GAP_DEG = 15.0
MIN_FACES = 20  # faces minimum par bande de 0,01R pour tracer un point de courbe


def _moy_circ(deg):
    a = np.radians(deg)
    return math.degrees(math.atan2(np.sin(a).mean(), np.cos(a).mean()))


def _ecart(a, b):
    return (a - b + 180.0) % 360.0 - 180.0


def _paquets(th):
    """Partition circulaire des azimuts (degrés) en paquets séparés par des vides > GAP_DEG."""
    idx = np.argsort(th)
    t = th[idx]
    vides = np.diff(np.concatenate([t, [t[0] + 360.0]]))
    debut = (np.argmax(vides) + 1) % len(t)  # démarrer juste après le plus grand vide
    ordre = np.roll(np.arange(len(t)), -debut)
    idx, t = idx[ordre], t[ordre]
    coupes = np.where(np.abs(_ecart(t[1:], t[:-1])) > GAP_DEG)[0]
    return np.split(idx, coupes + 1)


def choisir_pale(C):
    """Masque des faces (parmi C) appartenant à UNE pale, suivie de bande en bande, et azimut médian."""
    r = np.hypot(C[:, 0], C[:, 2]) / R
    th = np.degrees(np.arctan2(C[:, 2], C[:, 0]))
    centres = np.arange(BORNES[0] + PAS / 2, BORNES[1], PAS)
    ref = min(range(len(centres)), key=lambda i: abs(centres[i] - 0.90))
    masque = np.zeros(len(C), bool)
    th_med = np.full(len(centres), np.nan)

    def bande(i):
        return np.where((r >= centres[i] - PAS / 2) & (r < centres[i] + PAS / 2))[0]

    def choisir(sel, cible):
        if len(sel) == 0:
            return None
        pq = _paquets(th[sel])
        meds = [_moy_circ(th[sel][p]) for p in pq]
        k = min(range(len(pq)), key=lambda j: abs(_ecart(meds[j], cible)))
        return sel[pq[k]], meds[k]

    sel0 = bande(ref)
    pq = _paquets(th[sel0])
    meds = [_moy_circ(th[sel0][p]) for p in pq]
    k = min(range(len(pq)), key=lambda j: abs(meds[j]))
    prev = meds[k]
    for ordre in (range(ref, len(centres)), range(ref - 1, -1, -1)):
        cible = meds[k]
        for i in ordre:
            sel = bande(i)
            res = choisir(sel, cible)
            if res is None:
                continue
            sub, cible = res
            masque[sub] = True
            th_med[i] = cible
    return masque, th_med, centres, r, th


def charger(label, chemin, copies):
    if not os.path.isfile(os.path.join(chemin, "constant", "V")):
        dest = os.path.join(copies, label)
        print(f"  [{label}] constant/V absent : préparation sur une copie -> {dest}")
        chemin = mc.preparer_volumes_copie(chemin, dest)
    C, N, H, P, A = mc.faces_avec_h(chemin, avec_aire=True)
    return C, N, H, P, A


def preparer_cas(label, chemin, copies):
    C, N, H, P, A = charger(label, chemin, copies)
    masque, th_med, centres, r, th = choisir_pale(C)
    ib = np.clip(((r - (centres[0] - PAS / 2)) / PAS).astype(int), 0, len(centres) - 1)
    y = np.array([_ecart(th[i], th_med[ib[i]]) if masque[i] and not np.isnan(th_med[ib[i]]) else np.nan
                  for i in range(len(C))])
    y = np.radians(y) * r * R * 1e3  # arc en mm
    return dict(label=label, C=C, N=N, H=H, P=P, A=A, r=r, y=y, masque=masque)


def couleurs(d, idx):
    c = np.where(d["H"][idx] < SEUIL_MM, VERT, ROUGE).astype(object)
    c[d["P"][idx] == "propellerTipEdge"] = GRIS
    return c


def figure_carte(cas, out):
    ny = len(cas)
    fig, axes = plt.subplots(ny, 2, figsize=(17, 6.0 * ny), sharex=True, sharey=True, squeeze=False)
    collections = []  # (axe, collection, sqrt(aire) en mm)
    for row, d in enumerate(cas):
        sel = np.where(d["masque"] & (d["r"] >= BORNES[0]) & (d["r"] < BORNES[1]) & ~np.isnan(d["y"]))[0]
        ny_ax = d["N"][sel, 1]
        bords = np.abs(ny_ax) <= 0.3
        for col, (lab, m) in enumerate((("flanc A (normale axiale > 0)", ny_ax > 0.3),
                                        ("flanc B (normale axiale < 0)", ny_ax < -0.3))):
            ax = axes[row, col]
            for masque_pts in (bords, m):  # bords/calotte montrés sur les DEUX panneaux
                ii = sel[masque_pts]
                coll = ax.scatter(d["r"][ii], d["y"][ii], s=4, c=couleurs(d, ii).tolist(), marker="s",
                                  linewidths=0, alpha=0.95)
                collections.append((ax, coll, np.sqrt(d["A"][ii]) * 1e3))
            visibles = sel[m | bords]
            tip = visibles[d["P"][visibles] != "propellerTipEdge"]
            frac = 100 * np.mean(d["H"][tip] < SEUIL_MM) if len(tip) else float("nan")
            ax.set_title(f"{d['label']} — {lab} — {len(tip)} faces propellerTip, {frac:.0f} % avec 1re couche",
                         fontsize=10)
            ax.axvspan(0.818, 0.915, color="#dddddd", alpha=0.25, zorder=0)
            ax.grid(alpha=0.25)
            if col == 0:
                ax.set_ylabel("position tangentielle développée (mm)\n(arc, pas la corde)")
            if row == ny - 1:
                ax.set_xlabel("r/R")
    axes[0, 0].set_xlim(BORNES[0], 1.005)
    from matplotlib.lines import Line2D
    leg = [Line2D([], [], marker="s", ls="", color=VERT, label=f"1re couche présente (h < {SEUIL_MM} mm)"),
           Line2D([], [], marker="s", ls="", color=ROUGE, label="pas de 1re couche"),
           Line2D([], [], marker="s", ls="", color=GRIS, label="propellerTipEdge : sans couches par décision (13/09)")]
    fig.legend(handles=leg, loc="lower center", ncol=3, fontsize=10, frameon=False)
    fig.suptitle("Couverture des couches de prismes sur une pale — même échelle pour tous les cas — "
                 "diagnostic, non validé", fontsize=12)
    fig.tight_layout(rect=(0, 0.04, 1, 0.97))
    fig.canvas.draw()
    # Taille des marqueurs = taille RÉELLE des faces, avec l'échelle géométrique moyenne des deux axes
    # (les axes sont très anisotropes : ~15 pt/mm en x, ~3 pt/mm en y).
    for ax, coll, cote_mm in collections:
        bb = ax.get_window_extent()
        x0, x1 = ax.get_xlim()
        y0, y1 = ax.get_ylim()
        pt_par_mm_x = bb.width * 72 / fig.dpi / ((x1 - x0) * R * 1e3)
        pt_par_mm_y = bb.height * 72 / fig.dpi / (y1 - y0)
        k = math.sqrt(pt_par_mm_x * pt_par_mm_y)
        coll.set_sizes((cote_mm * k) ** 2)
    fig.savefig(out, dpi=110, facecolor="white")
    plt.close(fig)
    print(f"  écrit : {out}")


def figure_courbes(cas, out):
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.2), sharey=True)
    bords = np.arange(BORNES[0], BORNES[1] + 1e-9, PAS)
    for d in cas:
        tip = d["P"] != "propellerTipEdge"
        flanc = tip & (np.abs(d["N"][:, 1]) > 0.3)
        for ax, masque in ((axes[0], tip), (axes[1], flanc)):
            xs, ys = [], []
            for lo in bords[:-1]:
                s = masque & (d["r"] >= lo) & (d["r"] < lo + PAS)
                xs.append(lo + PAS / 2)
                # bande trop pauvre (îlots de propellerTip dans la zone Edge) : NaN, la courbe se coupe
                ys.append(100 * np.mean(d["H"][s] < SEUIL_MM) if s.sum() >= MIN_FACES else np.nan)
            ax.plot(xs, ys, marker="o", ms=3, lw=1.6, label=d["label"])
    for ax, t in zip(axes, ("toutes les faces de propellerTip", "flancs seulement (|normale axiale| > 0,3)")):
        ax.axvspan(0.818, 0.915, color="#dddddd", alpha=0.4)
        ax.text(0.866, 3, "propellerTipEdge\n(sans couches)", ha="center", fontsize=8, color="#555555")
        ax.set_title(t)
        ax.set_xlabel(f"r/R (bandes de 0,01, >= {MIN_FACES} faces ; les 4 pales)")
        ax.grid(alpha=0.3)
        ax.set_ylim(0, 102)
    axes[0].set_ylabel("% de faces avec 1re couche (h < 0,4 mm)")
    axes[0].legend()
    fig.suptitle("Couverture par rayon — proxy « première couche présente » — diagnostic, non validé")
    fig.tight_layout()
    fig.savefig(out, dpi=110, facecolor="white")
    plt.close(fig)
    print(f"  écrit : {out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cas", action="append", required=True, help="LABEL=CASE_DIR")
    ap.add_argument("--out", default="Helice/Images/_brouillon")
    ap.add_argument("--copies", default=os.path.join(tempfile.gettempdir(), "carte_couverture_copies"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    cas = []
    for spec in a.cas:
        label, chemin = spec.split("=", 1)
        cas.append(preparer_cas(label, chemin, a.copies))
    nom = "_vs_".join(d["label"] for d in cas)
    figure_carte(cas, os.path.join(a.out, f"carte_couverture_pale_{nom}.png"))
    figure_courbes(cas, os.path.join(a.out, f"courbe_couverture_pale_{nom}.png"))


if __name__ == "__main__":
    main()
