#!/usr/bin/env python3
"""Trace K_T, 10*K_Q, eta0 en fonction des TOURS (pas des secondes) pour les trois
fermetures de turbulence superposées (LOT A5, consigne du 15/09).

Lit `Helice/data/perf_<modele>.csv` DÉJÀ AUGMENTÉ des colonnes `tours`/`angle_deg`
(`Helice/scripts/augmenter_tours_angle.py` — lancer ce script d'abord s'il n'a pas
encore tourné). Produit trois figures dans `Helice/Images/galerie/` :
  series_KT_tours.png, series_10KQ_tours.png, series_eta0_tours.png

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
OUT_DIR = ROOT / "Helice" / "Images" / "galerie"

CASES = ["kEpsilon", "kOmegaSST", "laminar"]
LABELS = {"kEpsilon": "k-epsilon (RAS)", "kOmegaSST": "k-omega SST (RAS)", "laminar": "laminaire"}
COLORS = {"kEpsilon": "#1f77b4", "kOmegaSST": "#d62728", "laminar": "#2ca02c"}

# Sourcé Helice/docs/PARAMETRES_CAS.md (15/09) -- PAS le rappel périmé de la consigne.
AMPLITUDE_CC = {"kEpsilon": 0.0176, "kOmegaSST": 0.0223, "laminar": 0.0242}

N_TR_S = 158 / (2 * 3.141592653589793)  # dynamicMeshDict:29, omega/2pi
PERIOD_S = 1.0 / N_TR_S  # 0,039767 s
T_END = 0.06
FENETRE_COMMUNE = (0.022032, T_END)  # exclut le trou kOmegaSST -- METHODO_DONNEES.md §6
DERNIER_TOUR = (T_END - PERIOD_S, T_END)  # 0,020233 -- 0,06 s

TROU_KOMEGASST = (0.00819355, 0.0220323)  # METHODO_DONNEES.md §5

# Démarrage impulsif : KT/KQ/eta0 y valent plusieurs ordres de grandeur au-dessus du
# régime établi (même filtre que Helice/scripts/bilan_helice.py, T_TRANSIENT_SKIP) --
# sans lui, le pic initial écrase l'oscillation utile à une ligne plate.
T_TRANSIENT_SKIP = 0.001

GRANDEURS = [("KT", "$K_T$", "series_KT_tours.png"),
             ("10KQ", "$10 \\cdot K_Q$", "series_10KQ_tours.png"),
             ("eta0", "$\\eta_0$", "series_eta0_tours.png")]


def read_csv(short):
    path = DATA / f"perf_{short}.csv"
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        rows = [dict(r) for r in reader]
    if "tours" not in rows[0]:
        raise SystemExit(
            f"{path} n'a pas de colonne 'tours' -- lancer d'abord "
            "Helice/scripts/augmenter_tours_angle.py"
        )
    return [r for r in rows if float(r["time"]) >= T_TRANSIENT_SKIP]


def moyenne_fenetre(rows, key, t0, t1):
    vals = [float(r[key]) for r in rows if t0 <= float(r["time"]) <= t1]
    return sum(vals) / len(vals) if vals else None


def plot_grandeur(rows_by_case, key, label, out_name):
    fig, ax = plt.subplots(figsize=(11, 5.5))

    t0_c, t1_c = FENETRE_COMMUNE
    t0_d, t1_d = DERNIER_TOUR
    ax.axvspan(t0_c * N_TR_S, t1_c * N_TR_S, color="#f0e6d2", alpha=0.6, zorder=0,
               label="fenêtre commune")
    ax.axvspan(t0_d * N_TR_S, t1_d * N_TR_S, color="#d2e6f0", alpha=0.5, zorder=0,
               label="dernier tour")
    # Trou de données kOmegaSST -- marqué VISIBLEMENT (pas seulement en légende).
    tg0, tg1 = TROU_KOMEGASST
    ax.axvspan(tg0 * N_TR_S, tg1 * N_TR_S, color="#b30000", alpha=0.25, zorder=1)

    for case in CASES:
        rows = rows_by_case[case]
        tours = [float(r["tours"]) for r in rows]
        y = [float(r[key]) for r in rows]
        ax.plot(tours, y, lw=1.0, color=COLORS[case], label=LABELS[case])
        moy = moyenne_fenetre(rows, key, *FENETRE_COMMUNE)
        if moy is not None:
            ax.axhline(moy, color=COLORS[case], lw=1.2, ls="--", alpha=0.8)

    ymin, ymax = ax.get_ylim()
    ax.text((tg0 + tg1) / 2 * N_TR_S, ymin + 0.08 * (ymax - ymin),
             "trou kOmegaSST\n(13,8 ms)", ha="center", va="bottom", fontsize=8,
             color="#8a0000")

    if key == "KT":
        for i, case in enumerate(CASES):
            amp = AMPLITUDE_CC[case]
            ax.annotate(f"{LABELS[case]} : amplitude {amp:.4f}".replace(".", ","),
                        xy=(0.02, 0.97 - i * 0.055), xycoords="axes fraction",
                        fontsize=8, color=COLORS[case])

    max_tour = max(float(r["tours"]) for rows in rows_by_case.values() for r in rows)
    ax.set_xticks(range(0, int(max_tour) + 2))
    ax.xaxis.set_major_formatter(_fr)
    ax.yaxis.set_major_formatter(_fr)
    ax.set_xlabel("Tours (n × temps, n = 25,146 tr/s)")
    ax.set_ylabel(label)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=8)
    ax.set_title(f"{label} en fonction des tours — trois fermetures de turbulence")
    fig.text(0.01, 0.01,
              "Source : Helice/data/perf_*.csv (augmenté) · fenêtre commune "
              "[0,022032 ; 0,06] s · dernier tour [0,020233 ; 0,06] s",
              fontsize=7, color="#555555")
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
