#!/usr/bin/env python3
"""Six figures y+ pour la séance 3 -- LOT 5, consigne du 18/09
"Consolidee_Figures-et-variante-Vega". Toutes `licence: libre` (générées, aucune
image tierce). Écrit directement sous `Helice/Images/` (SUIVI en git).

CONSTANTES DE LA LOI LOGARITHMIQUE (GATE GÉNÉRAL DU LOT 5) -- kappa (constante de
von Kármán) et B (constante additive) : kappa=0,41, B=5,0. Source vérifiée le 18/09
par recherche web (pas de mémoire, ni celle de Claude ni celle de Cowork) :
Coles, D.E. & Hirst, E.A. (1968), "Computation of Turbulent Boundary Layers -- 1968
AFOSR-IFP-Stanford Conference, Vol. II: Compiled Data", valeurs de synthèse
kappa≈0,41 largement reprises depuis (voir aussi Wikipedia "Von Kármán constant" et
Bailey et al. 2014, Princeton, qui les citent comme référence historique). B est
parfois cité 5,0 à 5,2 selon le jeu de données (Coles 5,0 ; Brederode & Bradshaw
1974, 5,2) -- 5,0 retenu ici, valeur la plus citée, cohérence explicitement notée.
`u+ = (1/kappa)*ln(y+) + B`.

Usage :
    python3 _Setup/outils/generer_figures_yplus.py            # les six figures
    python3 _Setup/outils/generer_figures_yplus.py --figure a  # une seule (a-e)
"""
import argparse
import gzip
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_DIR = os.path.join(ROOT, "Helice", "Images")
OBJ_TIP = os.path.join(ROOT, "Helice", "case_kEpsilon", "constant", "triSurface", "propellerTip.obj.gz")

KAPPA = 0.41
B_LOG = 5.0

# ---------------------------------------------------------------------------
# Géométrie source -- même méthode que _Setup/outils/mesurer_fermeture_pale.py
# (extraction verbatim de la coupe dos/face à un rayon donné), réutilisée ici
# pour tracer une section réelle, pas un dessin.
# ---------------------------------------------------------------------------

def _read_obj(path):
    verts = []
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt") as f:
        for line in f:
            if line.startswith("v "):
                x, y, z = map(float, line.split()[1:4])
                verts.append((x, y, z))
    return np.array(verts)


def _section_a_rayon(verts, frac, tol_frac=0.02):
    """Retourne les points (s, t) dans le repère local déroulé (s=corde, t=épaisseur)
    d'UNE pale à r/R=frac, triés par s -- même PCA que mesurer_fermeture_pale.py."""
    r_all = np.hypot(verts[:, 0], verts[:, 2])
    R = r_all.max()
    th_all = np.arctan2(verts[:, 2], verts[:, 0])
    rt = frac * R
    band = np.abs(r_all - rt) < tol_frac * R
    idx = np.where(band)[0]
    th_band = th_all[idx]
    order = np.argsort(th_band)
    th_sorted = th_band[order]
    gaps = np.diff(th_sorted)
    splits = np.where(gaps > np.radians(20))[0]
    groups = np.split(order, splits + 1)
    grp = max(groups, key=len)
    pts = verts[idx][grp]
    th_pale = th_band[grp]
    y_pale = pts[:, 1]
    theta_bar = th_pale.mean()
    s_local = rt * (th_pale - theta_bar)
    t_local = y_pale - y_pale.mean()
    X = np.column_stack([s_local, t_local])
    Xc = X - X.mean(axis=0)
    cov = np.cov(Xc.T)
    w, v = np.linalg.eigh(cov)
    order_ev = np.argsort(w)[::-1]
    major, minor = v[:, order_ev[0]], v[:, order_ev[1]]
    s_proj = Xc @ major
    t_proj = Xc @ minor
    return R, s_proj, t_proj


# ---------------------------------------------------------------------------
# (a) FIG-fon-s7-maille-vs-epaisseur -- PRIORITAIRE
# ---------------------------------------------------------------------------

def fig_a_maille_vs_epaisseur():
    verts = _read_obj(OBJ_TIP)
    R, s_proj, t_proj = _section_a_rayon(verts, 0.9)
    # tri par s, dos = t max localement, face = t min -- même convention que
    # mesurer_fermeture_pale.py
    order = np.argsort(s_proj)
    s_sorted, t_sorted = s_proj[order], t_proj[order]

    # enveloppe dos/face par bandes de s (pour tracer deux courbes propres à partir
    # d'un nuage de points de surface, pas d'un maillage triangulé)
    n_bins = 40
    s_min, s_max = s_sorted.min(), s_sorted.max()
    bins = np.linspace(s_min, s_max, n_bins + 1)
    s_dos, t_dos, s_face, t_face = [], [], [], []
    for i in range(n_bins):
        m = (s_sorted >= bins[i]) & (s_sorted < bins[i + 1])
        if m.sum() < 2:
            continue
        tb = t_sorted[m]
        sc = (bins[i] + bins[i + 1]) / 2
        s_dos.append(sc); t_dos.append(tb.max())
        s_face.append(sc); t_face.append(tb.min())
    s_dos, t_dos = np.array(s_dos), np.array(t_dos)
    s_face, t_face = np.array(s_face), np.array(t_face)

    # Épaisseur locale à mi-corde -- ANCRÉE sur le CENTRE GÉOMÉTRIQUE réel de la corde
    # (s_min+s_max)/2, jamais sur un index de tableau (les bandes vides sont retirées,
    # un index médian de tableau ne tombe alors plus sur le vrai mi-corde -- bug trouvé
    # le 18/09 en le testant : donnait 0,13 mm au lieu de ~3,5 mm à 0,9R). Fenêtre de
    # quelques bandes autour du centre, MÉDIANE (robuste aux bandes proches du bord
    # d'attaque/de fuite qui se glissent parfois dans la fenêtre avec une épaisseur
    # quasi nulle -- bruit de triangulation, pas la section elle-même).
    s_mid_target = (s_sorted.min() + s_sorted.max()) / 2
    dist_to_mid = np.abs(s_dos - s_mid_target)
    fenetre = np.argsort(dist_to_mid)[:5]
    epaisseurs_fenetre = t_dos[fenetre] - t_face[fenetre]
    epaisseur_mi_corde_mm = float(np.median(epaisseurs_fenetre) * 1000)
    mid = fenetre[np.argmin(dist_to_mid[fenetre])]

    cellule_mm = 3.125  # niveau 4, snappyHexMeshDict propellerTip -- base 50mm/2^4, sourcé PARAMETRES_CAS.md/system/snappyHexMeshDict
    ratio = epaisseur_mi_corde_mm / cellule_mm

    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.plot(np.array(s_dos) * 1000, np.array(t_dos) * 1000, color="#1A9988", lw=2, label="dos (mesuré)")
    ax.plot(np.array(s_face) * 1000, np.array(t_face) * 1000, color="#1A346D", lw=2, label="face (mesuré)")
    ax.fill_between(np.array(s_dos) * 1000, np.array(t_face)[:len(s_dos)] * 1000, np.array(t_dos) * 1000,
                     color="#E8F4F2", alpha=0.6, zorder=0)

    # grille de cellules a l'echelle (niveau 4, 3,125 mm), superposee sur la zone mi-corde
    s_mid = s_dos[mid] * 1000
    half = 4 * cellule_mm
    x0 = s_mid - half
    y0 = (t_face[mid] * 1000) - cellule_mm
    for i in range(int(2 * half / cellule_mm) + 2):
        x = x0 + i * cellule_mm
        ax.plot([x, x], [y0, y0 + 4 * cellule_mm], color="#999999", lw=0.6, zorder=1)
    for j in range(5):
        y = y0 + j * cellule_mm
        ax.plot([x0, x0 + int(2 * half / cellule_mm + 1) * cellule_mm], [y, y], color="#999999", lw=0.6, zorder=1)

    ax.annotate(f"épaisseur ≈ {epaisseur_mi_corde_mm:.2f} mm",
                xy=(s_mid, (t_dos[mid] + t_face[mid]) / 2 * 1000), xytext=(s_mid + 6, (t_dos[mid] * 1000) + 3),
                arrowprops=dict(arrowstyle="-", color="#EB5600"), color="#EB5600", fontsize=10, fontweight="bold")
    ax.set_xlabel("corde locale s [mm]")
    ax.set_ylabel("épaisseur locale t [mm]")
    ax.set_title("Section de pale à 0,9R vs taille de cellule (niveau 4) — à l'échelle")
    ax.legend(loc="upper right", fontsize=9)
    ax.set_ylim(-8, 8)
    ax.set_aspect("equal", adjustable="datalim")
    caption = (f"Section réelle à 0,9R (géométrie source, propellerTip.obj.gz) — épaisseur locale mesurée "
               f"{epaisseur_mi_corde_mm:.2f} mm ;\ncellule niveau 4 = {cellule_mm:.3f} mm (snappyHexMeshDict) "
               f"— ratio ≈ {ratio:.2f}.")
    fig.tight_layout(rect=(0, 0.10, 1, 1))
    fig.text(0.5, 0.01, caption, ha="center", va="bottom", fontsize=8, color="#595959")
    out = os.path.join(OUT_DIR, "FIG-fon-s7-maille-vs-epaisseur.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"OK -> {out}  (épaisseur mi-corde mesurée {epaisseur_mi_corde_mm:.3f} mm, "
          f"cellule niveau 4 = {cellule_mm} mm, ratio = {ratio:.2f})")


# ---------------------------------------------------------------------------
# (b) FIG-fon-s7-loi-paroi-deux-vues
# ---------------------------------------------------------------------------

def fig_b_loi_paroi_deux_vues():
    nu = 1e-6  # m^2/s, transportProperties -- meme valeur que le reste du depot
    u_tau = 0.05  # m/s, ordre de grandeur representatif pour l'illustration (pas mesure sur ce cas)
    y_plus = np.logspace(-1, 3.3, 400)
    y_phys_mm = y_plus * nu / u_tau * 1000

    u_plus_visc = y_plus  # sous-couche visqueuse u+ = y+
    u_plus_log = (1 / KAPPA) * np.log(y_plus) + B_LOG
    u_plus = np.where(y_plus < 5, u_plus_visc, np.where(y_plus > 30, u_plus_log, np.nan))
    # zone tampon : interpolation lisse juste pour la continuite visuelle (non physique, signale)
    mask_tampon = (y_plus >= 5) & (y_plus <= 30)
    u5 = 5.0
    u30 = (1 / KAPPA) * math.log(30) + B_LOG
    u_plus[mask_tampon] = np.interp(np.log(y_plus[mask_tampon]), [math.log(5), math.log(30)], [u5, u30])
    u_phys = u_plus * u_tau

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(11, 4.5))
    axL.plot(y_phys_mm, u_phys, color="#1A346D", lw=2)
    axL.set_xlabel("y [mm]")
    axL.set_ylabel("u [m/s]")
    axL.set_title("Vue physique — u(y)")
    axL.set_xlim(0, y_phys_mm[np.searchsorted(y_plus, 300)])

    axR.plot(y_plus, u_plus, color="#1A9988", lw=2)
    axR.set_xscale("log")
    axR.axvspan(5, 30, color="#E8F4F2", alpha=0.8, label="zone tampon (ni l'un ni l'autre)")
    axR.set_xlabel("y⁺ (échelle log)")
    axR.set_ylabel("u⁺")
    axR.set_title(f"Vue universelle — u⁺(y⁺) = (1/κ)ln(y⁺)+B, κ={KAPPA}, B={B_LOG}")
    axR.legend(fontsize=8, loc="upper left")

    fig.suptitle("Même couche limite, deux vues — le changement de variable la rend universelle",
                 fontsize=11)
    fig.text(0.5, 0.01,
              f"u_tau={u_tau} m/s, nu={nu} m²/s : valeurs D'ILLUSTRATION pour tracer la vue physique à "
              f"l'échelle — pas une mesure sur ce cas. κ/B sourcés Coles & Hirst (1968), voir en-tête "
              f"du script.", fontsize=7, color="#595959", ha="center")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    out = os.path.join(OUT_DIR, "FIG-fon-s7-loi-paroi-deux-vues.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"OK -> {out}")


# ---------------------------------------------------------------------------
# (c) FIG-fon-s7-trois-regions
# ---------------------------------------------------------------------------

def fig_c_trois_regions():
    y_plus = np.logspace(-1, 3.3, 400)
    u_visc = y_plus
    u_log = (1 / KAPPA) * np.log(y_plus) + B_LOG

    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.plot(y_plus[y_plus <= 5], u_visc[y_plus <= 5], color="#1A346D", lw=2, label="sous-couche visqueuse : u⁺=y⁺")
    ax.plot(y_plus[y_plus >= 30], u_log[y_plus >= 30], color="#1A9988", lw=2,
            label=f"zone logarithmique : u⁺=(1/κ)ln(y⁺)+B (κ={KAPPA}, B={B_LOG})")
    ax.axvspan(5, 30, color="#E8F4F2", alpha=0.8, label="zone tampon [5;30] — aucune loi simple valide")
    ax.set_xscale("log")
    ax.set_xlabel("y⁺ (échelle log)")
    ax.set_ylabel("u⁺")
    ax.set_title("Les trois régions de la couche limite turbulente")

    ax.axvspan(0.1, 1, color="#EB5600", alpha=0.12)
    ax.text(0.3, 2, "RÉSOUDRE\ny⁺<1\n(1re cellule)", fontsize=8, color="#EB5600", ha="center")
    ax.axvspan(30, 300, color="#1A9988", alpha=0.08)
    ax.text(90, 2, "MODÉLISER\n30<y⁺<300\n(loi de paroi)", fontsize=8, color="#1A9988", ha="center")
    ax.legend(fontsize=8, loc="upper left")
    fig.text(0.5, 0.005,
              "L'entre-deux (1<y⁺<30, hors sous-couche visqueuse) n'est valide pour AUCUNE des deux "
              "stratégies -- ni résoudre, ni modéliser.",
              ha="center", fontsize=8, color="#595959")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    out = os.path.join(OUT_DIR, "FIG-fon-s7-trois-regions.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"OK -> {out}")


# ---------------------------------------------------------------------------
# (d) FIG-fon-s7-premiere-maille
# ---------------------------------------------------------------------------

def fig_d_premiere_maille():
    # Relevés à 4 tours (t = 0,158 s), cas à couches, patch propellerTip : moyenne 87,3 ; max 1051,6 ; min 12,3 (log.yPlus.4tours_20sept).
    cas = [
        (0.8, "y⁺=0,8 : ILLUSTRATION (aucun\nrelevé de ce dépôt sous 12).\nLa 1re cellule serait dans la\nsous-couche visqueuse : le code\nsupposerait une résolution\ndirecte, VRAI dans ce cas."),
        (87, "y⁺=87 : la 1re cellule est\ndans la zone log [30;300].\nLe code suppose une loi de\nparoi valide : VRAI ici (notre\ncas, propellerTip, moyenne)."),
        (1052, "y⁺=1052 : bien AU-DESSUS\nde 300 (max mesuré,\npropellerTip). Le code applique\nquand même la loi de paroi :\nSUPPOSÉ, mais FAUX ici."),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(12, 5.6))
    for ax, (yplus, texte) in zip(axes, cas):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axhspan(0, 0.08, color="#1A346D")
        h_cell = min(0.75, 0.05 + 0.30 * math.log10(max(yplus, 0.5) + 1))
        ax.plot([0.5], [0.08 + h_cell], marker="o", color="#EB5600", markersize=10, zorder=3)
        ax.plot([0.5, 0.5], [0.08, 0.08 + h_cell], color="#999999", lw=1, ls="--")
        ax.text(0.5, 0.08 + h_cell + 0.04, f"y⁺={yplus:g}", ha="center", fontsize=11, fontweight="bold")
        ax.text(0.5, -0.06, texte, ha="center", va="top", fontsize=10.5, transform=ax.transAxes)
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
    fig.suptitle("Où tombe la première cellule — deux relevés de ce dépôt et une illustration", fontsize=13)
    fig.subplots_adjust(wspace=0.4)
    fig.tight_layout(rect=(0, 0.30, 1, 0.95))
    fig.subplots_adjust(wspace=0.4)
    out = os.path.join(OUT_DIR, "FIG-fon-s7-premiere-maille.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"OK -> {out}")


# ---------------------------------------------------------------------------
# (e) FIG-fon-s7-yplus-histogramme -- PAS un histogramme (voir avertissement)
# ---------------------------------------------------------------------------

def fig_e_yplus_repartition():
    """Répartition RÉELLE du y⁺ sur `propellerTip`, pondérée par l'AIRE des faces, à 4 tours : sans couches (`case_kEpsilon`, t = 0,159 s)
    et avec couches (`case_kEpsilon_layers`, t = 0,158 s). Champ yPlus par face reconstruit par
    `pimpleFoam -postProcess -func yPlus -latestTime` puis `reconstructPar` (20/09) ; lecture par `verifier_yplus_pondere_aire.py`."""
    import numpy as np
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import verifier_yplus_pondere_aire as vy
    racine = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    jeux = [("sans couches, t = 0,159 s", "Helice/case_kEpsilon", "0.159", "#1A346D"),
            ("avec couches, t = 0,158 s", "Helice/case_kEpsilon_layers", "0.158", "#EB5600")]
    bornes = np.logspace(np.log10(10), np.log10(2000), 41)
    fig, ax = plt.subplots(figsize=(9, 4.4))
    ax.axvspan(30, 300, color="#E8F4F2", alpha=0.9)
    for etiq, cas, t, col in jeux:
        cas = os.path.join(racine, cas)
        debut, n = vy._lire_patch_range(cas, "propellerTip")
        pts = vy._lire_points(cas); off, idx = vy._lire_faces(cas)
        aires = np.array([vy._aire_polygone(pts[idx[off[debut + i]:off[debut + i + 1]]]) for i in range(n)])
        val = vy._lire_champ_patch(cas, t, "yPlus", "propellerTip")
        h, _ = np.histogram(val, bins=bornes, weights=aires)
        part = 100 * aires[(val >= 30) & (val <= 300)].sum() / aires.sum()
        ax.stairs(100 * h / aires.sum(), bornes, color=col, lw=2, label=f"{etiq} — {part:.1f} % de l'aire dans [30;300]")
    ax.set_xscale("log"); ax.set_xlim(10, 2000)
    ax.set_xlabel("y⁺ (échelle log)"); ax.set_ylabel("part de l'aire de propellerTip (%) par classe")
    ax.set_title("Répartition du y⁺ sur propellerTip, à 4 tours (zone [30;300] : loi de paroi valide)")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    out = os.path.join(OUT_DIR, "FIG-fon-s7-yplus-histogramme.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"OK -> {out}  (répartition réelle pondérée par l'aire, deux cas à 4 tours)")


FIGURES = {"a": fig_a_maille_vs_epaisseur, "b": fig_b_loi_paroi_deux_vues,
           "c": fig_c_trois_regions, "d": fig_d_premiere_maille, "e": fig_e_yplus_repartition}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--figure", choices=sorted(FIGURES), help="une seule figure (a-e) ; défaut : toutes")
    a = ap.parse_args()
    cles = [a.figure] if a.figure else sorted(FIGURES)
    for c in cles:
        FIGURES[c]()


if __name__ == "__main__":
    main()
