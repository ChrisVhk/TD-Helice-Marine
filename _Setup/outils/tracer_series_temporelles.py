#!/usr/bin/env python3
"""Trace K_T, 10*K_Q, eta0 en fonction des TOURS (pas des secondes) pour les trois
fermetures de turbulence superposées (LOT A5, consigne du 15/09 ; unifié le 17/09,
LOT 2 -- remplace `generer_figure_KT_series.py`, qui produisait la même figure K_T
depuis les mêmes CSV avec sa propre reconversion tours = t/T interne).

Lit `Helice/data/perf_<modele>.csv`, colonnes `tours`/`angle_deg` déjà présentes
(`Helice/scripts/extraire_kit_donnees.py`, colonnes ajoutées dans la même passe que le
rééchelonnement D -- lancer ce script d'abord si les colonnes manquent). Produit trois
figures dans `Helice/Images/` (convention `FIG-fon-s7-*`, PAS `galerie/` -- ces figures
sont du matériel de cours, pas la galerie d'introduction régénérable) :
  FIG-fon-s7-KT-series-tours.png, FIG-fon-s7-10KQ-series-tours.png,
  FIG-fon-s7-eta0-series-tours.png

**Diff avec l'ancien script avant suppression (17/09)** : mêmes données, même n
(25,146 vs 25,15 tr/s lu directement dans le CSV -- écart relatif 0,014 %, invisible à
l'échelle du tracé), courbes visuellement identiques. Seule différence réelle :
l'ancien coupait franchement la ligne au niveau du trou de données `kOmegaSST`
(`break_gaps()`, aucun segment tracé) ; celui-ci reliait les deux bords du trou par un
segment droit dans le fond ombré -- moins honnête (une droite suggère une donnée
interpolée qui n'existe pas). Repris ici : la ligne est coupée, pas reliée.

**Réserve amplitude (15/09)** : la consigne de cette boucle rappelait les amplitudes
crête-à-crête 0,0404 / 0,0373 / 0,0294 -- ce sont les valeurs PRÉ-rééchelonnement du
13/09 (D=0,2 m), explicitement PÉRIMÉES dans `Helice/docs/PARAMETRES_CAS.md` depuis le
15/09 (remplacées par 0,0176 / 0,0223 / 0,0242, D=0,227378 m). Ce script annote les
valeurs COURANTES, sourcées, jamais le rappel périmé -- voir JOURNAL 15/09.
"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

_fr = FuncFormatter(lambda v, _pos: f"{v:g}".replace(".", ","))

HERE = Path(__file__).resolve().parent
# _Setup/outils/tracer_series_temporelles.py -> repo root est deux niveaux au-dessus
ROOT = HERE.parent.parent
DATA = ROOT / "Helice" / "data"
OUT_DIR = ROOT / "Helice" / "Images"

CASES = ["kEpsilon", "kOmegaSST", "laminar"]
LABELS = {"kEpsilon": "k-epsilon (RAS)", "kOmegaSST": "k-omega SST (RAS)", "laminar": "laminaire"}
COLORS = {"kEpsilon": "#1f77b4", "kOmegaSST": "#d62728", "laminar": "#2ca02c"}

# 20/09 : les fenêtres, les moyennes et l'amplitude de K_T sont DÉDUITES des données (fin commune des
# trois séries, dernier tour complet), plus des constantes du jeu à 1,5 tour. Ces constantes
# (T_END = 0,06 ; amplitudes 0,0176 / 0,0223 / 0,0242) étaient valides pour des séries arrêtées à 0,06 s ;
# leurs amplitudes étaient gonflées par le transitoire des deux premiers tours (à 4 tours, l'amplitude
# crête-à-crête du dernier tour est 4 à 5 fois plus petite).
N_TR_S = 158 / (2 * 3.141592653589793)  # dynamicMeshDict:29, omega/2pi
PERIOD_S = 1.0 / N_TR_S  # 0,039767 s
T_DEBUT_COMMUN = 0.022032  # exclut le trou kOmegaSST -- METHODO_DONNEES.md §6

TROU_KOMEGASST = (0.00819355, 0.0220323)  # METHODO_DONNEES.md §5

# Démarrage impulsif : KT/KQ/eta0 y valent plusieurs ordres de grandeur au-dessus du
# régime établi (même filtre que Helice/scripts/bilan_helice.py, T_TRANSIENT_SKIP) --
# sans lui, le pic initial écrase l'oscillation utile à une ligne plate.
T_TRANSIENT_SKIP = 0.001

GRANDEURS = [("KT", "$K_T$", "FIG-fon-s7-KT-series-tours.png"),
             ("10KQ", "$10 \\cdot K_Q$", "FIG-fon-s7-10KQ-series-tours.png"),
             ("eta0", "$\\eta_0$", "FIG-fon-s7-eta0-series-tours.png")]


def read_csv(short):
    path = DATA / f"perf_{short}.csv"
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        rows = [dict(r) for r in reader]
    if "tours" not in rows[0]:
        raise SystemExit(
            f"{path} n'a pas de colonne 'tours' -- lancer d'abord "
            "Helice/scripts/extraire_kit_donnees.py"
        )
    return [r for r in rows if float(r["time"]) >= T_TRANSIENT_SKIP]


def casser_trous(temps, tours, y, facteur=5):
    """Insère un `None` partout où l'écart de temps dépasse `facteur` fois l'écart
    médian -- repris de l'ancien `generer_figure_KT_series.py` (break_gaps) : sans ça,
    matplotlib relie les deux bords du trou kOmegaSST par une droite qui ne correspond
    à aucune donnée réelle (trouvé à l'œil sur une première version de cette figure).
    """
    if len(temps) < 3:
        return tours, y
    ecarts = sorted(temps[i + 1] - temps[i] for i in range(len(temps) - 1))
    mediane = ecarts[len(ecarts) // 2]
    tours_c, y_c = [tours[0]], [y[0]]
    for i in range(1, len(temps)):
        if temps[i] - temps[i - 1] > facteur * mediane:
            tours_c.append(None)
            y_c.append(None)
        tours_c.append(tours[i])
        y_c.append(y[i])
    return tours_c, y_c


def moyenne_fenetre(rows, key, t0, t1):
    """Moyenne TEMPORELLE (trapèzes) sur [t0, t1] -- même définition que Helice/scripts/comparaison_modeles.py
    (le pas de kOmegaSST est adaptatif : une moyenne sur les lignes n'est pas une moyenne temporelle)."""
    pts = [(float(r["time"]), float(r[key])) for r in rows if t0 - 1e-12 <= float(r["time"]) <= t1 + 1e-12]
    if len(pts) < 3:
        return None
    s = sum(0.5 * (pts[i][0] - pts[i - 1][0]) * (pts[i][1] + pts[i - 1][1]) for i in range(1, len(pts)))
    return s / (pts[-1][0] - pts[0][0])


def crete_a_crete(rows, key, t0, t1):
    vals = [float(r[key]) for r in rows if t0 - 1e-12 <= float(r["time"]) <= t1 + 1e-12]
    return max(vals) - min(vals) if vals else None


def plot_grandeur(rows_by_case, key, label, out_name):
    fig, ax = plt.subplots(figsize=(9, 5.4))

    t_end = min(float(rows[-1]["time"]) for rows in rows_by_case.values())  # fin COMMUNE des trois séries
    t0_c, t1_c = T_DEBUT_COMMUN, t_end
    t0_d, t1_d = t_end - PERIOD_S, t_end  # dernier tour complet
    ax.axvspan(t0_c * N_TR_S, t1_c * N_TR_S, color="#f0e6d2", alpha=0.6, zorder=0,
               label="fenêtre commune")
    ax.axvspan(t0_d * N_TR_S, t1_d * N_TR_S, color="#d2e6f0", alpha=0.5, zorder=0,
               label="dernier tour")
    # Trou de données kOmegaSST -- marqué VISIBLEMENT (pas seulement en légende).
    tg0, tg1 = TROU_KOMEGASST
    ax.axvspan(tg0 * N_TR_S, tg1 * N_TR_S, color="#b30000", alpha=0.25, zorder=1)

    for case in CASES:
        rows = rows_by_case[case]
        temps = [float(r["time"]) for r in rows]
        tours = [float(r["tours"]) for r in rows]
        y = [float(r[key]) for r in rows]
        tours, y = casser_trous(temps, tours, y)
        ax.plot(tours, y, lw=1.0, color=COLORS[case], label=LABELS[case])
        moy = moyenne_fenetre(rows, key, t0_d, t1_d)  # moyenne du dernier tour complet
        if moy is not None:
            ax.axhline(moy, color=COLORS[case], lw=1.2, ls="--", alpha=0.8)

    ymin, ymax = ax.get_ylim()
    ax.text((tg0 + tg1) / 2 * N_TR_S, ymin + 0.08 * (ymax - ymin),
             "trou kOmegaSST\n(13,8 ms)", ha="center", va="bottom", fontsize=10,
             color="#8a0000")

    if key == "KT":
        for i, case in enumerate(CASES):
            amp = crete_a_crete(rows_by_case[case], key, t0_d, t1_d)
            ax.annotate(f"{LABELS[case]} : amplitude crête à crête, dernier tour, {amp:.4f}".replace(".", ","),
                        xy=(0.02, 0.97 - i * 0.055), xycoords="axes fraction",
                        fontsize=10.5, color=COLORS[case])

    max_tour = max(float(r["tours"]) for rows in rows_by_case.values() for r in rows)
    ax.set_xticks(range(0, int(max_tour) + 2))
    ax.xaxis.set_major_formatter(_fr)
    ax.yaxis.set_major_formatter(_fr)
    ax.set_xlabel("Tours (n × temps, n = 25,146 tr/s)")
    ax.set_ylabel(label)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=10)
    ax.set_title(f"{label} en fonction des tours — trois fermetures de turbulence")
    fig.text(0.01, 0.01,
              f"Source : Helice/data/perf_*.csv · fenêtre commune [{t0_c:.6f} ; {t1_c:.6f}] s · "
              f"dernier tour complet [{t0_d:.6f} ; {t1_d:.6f}] s (traits pointillés : moyenne de ce dernier tour)".replace(".", ","),
              fontsize=8, color="#555555")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    out = OUT_DIR / out_name
    fig.savefig(out, dpi=140)
    plt.close(fig)
    return out


def main():
    rows_by_case = {c: read_csv(c) for c in CASES}
    for key, label, out_name in GRANDEURS:
        out = plot_grandeur(rows_by_case, key, label, out_name)
        print(f"OK -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
