#!/usr/bin/env python3
"""
bilan_helice.py
----------------
Post-traitement graphique du TD hélice marine (3 fermetures de turbulence).
Adapté de `PerfNav/Propulseur/tp_propulseur_eau_libre_v2412/post/bilan_propulseur.py`
(parsing résidus/log + propellerInfo) et de la convention `Results/` des scripts
Poiseuille (`TD-TP/FON-S7_MecaFluides-Hydro/Poiseuille/scripts/`).

Produit dans Results/ :
  - convergence_residus.png   : résidus p (log) des 3 cas, un panneau par cas
  - comparaison_performance.png : KT, 10*KQ, eta0 vs temps, 3 cas superposés
  - bilan_helice.txt          : tableau de synthèse (moyenne dernier tour, cf. compare_turbulence.py)

**Lit `data/perf_<modèle>.csv` (LOT 1, décision enseignant du 15/09, INV-19) — PLUS le
brut `postProcessing/propellerInfo1/`.** Le brut porte encore radius=0,1 (D=0,2 m) : on
ne le réécrit jamais, la correction D vit dans `scripts/extraire_kit_donnees.py`. Lire le
brut ici referait exactement l'erreur qui a produit des bilans périmés — voir
`docs/METHODO_DONNEES.md`. Lancer `extraire_kit_donnees.py --csv` d'abord si les CSV
n'existent pas encore.

Usage :
    python3 scripts/bilan_helice.py
"""
import csv
import re
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")  # headless, cf. bilan_propulseur.py
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "Results"
OUTPUT_DIR.mkdir(exist_ok=True)
DATA_DIR = BASE_DIR / "data"

CASES = ["case_kEpsilon", "case_kOmegaSST", "case_laminar"]
CASE_TO_SHORT = {"case_kEpsilon": "kEpsilon", "case_kOmegaSST": "kOmegaSST", "case_laminar": "laminar"}
COLORS = {"case_kEpsilon": "#1f77b4", "case_kOmegaSST": "#d62728", "case_laminar": "#2ca02c"}
LABELS = {
    "case_kEpsilon": "k-epsilon (RAS)",
    "case_kOmegaSST": "k-omega SST (RAS)",
    "case_laminar": "laminaire",
}

RE_TIME = re.compile(r"^Time\s*=\s*([\d.eE+\-]+)")
RE_RES_P = re.compile(r"Solving for p,\s+Initial residual\s*=\s*([\d.eE+\-]+)")

PERF_COLUMNS = ["time", "n", "URef", "J", "KT", "10KQ", "eta0"]


def parse_residuals(case_dir: Path):
    """Résidus de pression au cours du temps, depuis log.pimpleFoam (cf. bilan_propulseur.py)."""
    log = case_dir / "log.pimpleFoam"
    if not log.exists():
        return np.empty((0, 2))
    times, res = [], []
    t = None
    with open(log, errors="ignore") as f:
        for line in f:
            m = RE_TIME.match(line)
            if m:
                t = float(m.group(1))
                continue
            m = RE_RES_P.search(line)
            if m and t is not None:
                times.append(t)
                res.append(float(m.group(1)))
    return np.array(list(zip(times, res))) if times else np.empty((0, 2))


def read_performance_csv(case: str):
    """Lit data/perf_<modèle>.csv (rééchelonné D, colonnes tours/angle_deg incluses) --
    PLUS le brut. Renvoie [] si le CSV n'existe pas (lancer extraire_kit_donnees.py --csv
    d'abord), jamais un repli silencieux sur le brut périmé."""
    path = DATA_DIR / f"perf_{CASE_TO_SHORT[case]}.csv"
    if not path.is_file():
        return []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        return [{c: row[c] for c in PERF_COLUMNS} for row in reader]


def average_last_revolution(rows):
    if not rows:
        return None
    n = float(rows[-1]["n"])
    period = 1.0 / n
    t_end = float(rows[-1]["time"])
    window = [r for r in rows if float(r["time"]) >= t_end - period]
    if len(window) < 2:
        window = rows
    avg = {k: sum(float(r[k]) for r in window) / len(window) for k in ("J", "KT", "10KQ", "eta0")}
    avg["t_end"] = t_end
    avg["period_covered"] = t_end >= period
    return avg


def plot_residuals(data_by_case):
    fig, axes = plt.subplots(1, 3, figsize=(15, 4), sharey=True)
    for ax, case in zip(axes, CASES):
        r = data_by_case.get(case, np.empty((0, 2)))
        if r.shape[0] > 0:
            ax.semilogy(r[:, 0], r[:, 1], lw=0.6, color=COLORS[case])
        ax.set_title(LABELS[case])
        ax.set_xlabel("Temps [s]")
        ax.grid(True, which="both", alpha=0.3)
    axes[0].set_ylabel("Résidu initial (p)")
    fig.suptitle("Convergence — TD hélice marine (3 fermetures de turbulence)")
    fig.tight_layout()
    out = OUTPUT_DIR / "convergence_residus.png"
    fig.savefig(out, dpi=140)
    plt.close(fig)
    return out


def plot_performance(rows_by_case):
    """Le tout premier instant (démarrage impulsif) produit un pic de KT/KQ de plusieurs
    ordres de grandeur au-dessus du régime établi (cf. docs/03_BASE_THEORIQUE.md) — on
    l'exclut de l'affichage (t < T_TRANSIENT_SKIP) pour ne pas écraser l'échelle utile."""
    T_TRANSIENT_SKIP = 0.001

    fig, axes = plt.subplots(3, 1, figsize=(9, 9), sharex=True)
    labels = {"KT": "$K_T$", "10KQ": "$10 \\cdot K_Q$", "eta0": "$\\eta_0$"}
    for ax, key in zip(axes, ("KT", "10KQ", "eta0")):
        for case in CASES:
            rows = rows_by_case.get(case)
            if not rows:
                continue
            filtered = [r for r in rows if float(r["time"]) >= T_TRANSIENT_SKIP]
            if not filtered:
                continue
            t = [float(r["time"]) for r in filtered]
            y = [float(r[key]) for r in filtered]
            ax.plot(t, y, lw=1.0, color=COLORS[case], label=LABELS[case])
        ax.set_ylabel(labels[key])
        ax.grid(True, alpha=0.3)
    axes[0].legend(loc="upper right")
    axes[-1].set_xlabel("Temps [s]")
    fig.suptitle(f"Performance hélice — comparaison des fermetures de turbulence (t ≥ {T_TRANSIENT_SKIP} s)")
    fig.tight_layout()
    out = OUTPUT_DIR / "comparaison_performance.png"
    fig.savefig(out, dpi=140)
    plt.close(fig)
    return out


def main() -> int:
    residuals = {}
    rows_by_case = {}
    summary_lines = [f"{'Modèle':<15} {'t_end':>8} {'J':>8} {'KT':>10} {'10*KQ':>10} {'eta0':>8}"]
    missing = []

    for case in CASES:
        case_dir = BASE_DIR / case
        residuals[case] = parse_residuals(case_dir)

        rows = read_performance_csv(case)
        if not rows:
            missing.append(case)
            summary_lines.append(f"{case:<15} {'—':>8} {'—':>8} {'—':>10} {'—':>10} {'—':>8}  (non calculé)")
            continue
        rows_by_case[case] = rows
        avg = average_last_revolution(rows)
        flag = "" if avg["period_covered"] else "  ⚠ < 1 tour écoulé"
        summary_lines.append(
            f"{case:<15} {avg['t_end']:>8.4f} {avg['J']:>8.4f} {avg['KT']:>10.4f} "
            f"{avg['10KQ']:>10.4f} {avg['eta0']:>8.4f}{flag}"
        )

    residuals_png = plot_residuals(residuals)
    perf_png = plot_performance(rows_by_case) if rows_by_case else None

    summary_txt = "\n".join(summary_lines) + "\n"
    (OUTPUT_DIR / "bilan_helice.txt").write_text(summary_txt)

    print(summary_txt)
    print(f"Figures : {residuals_png}" + (f", {perf_png}" if perf_png else ""))

    if missing:
        print(f"\nCSV manquants : {', '.join(missing)} — lancer "
              "'python3 scripts/extraire_kit_donnees.py --csv' d'abord.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
