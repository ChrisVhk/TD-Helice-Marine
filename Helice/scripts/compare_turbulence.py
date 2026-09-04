#!/usr/bin/env python3
"""Compare KT, KQ, eta0 entre les 3 fermetures de turbulence (case_kEpsilon,
case_kOmegaSST, case_laminar) à partir de postProcessing/propellerInfo1/*/propellerPerformance.dat
(function object OpenFOAM natif du tutoriel propeller, colonnes : Time n URef J KT 10*KQ eta0).

KT/KQ/eta0 oscillent avec la période de rotation (T = 1/n, passage de pale) : ce script moyenne
sur le DERNIER TOUR COMPLET écoulé plutôt que de lire la dernière ligne seule (une valeur
instantanée tomberait sur un point arbitraire du cycle, cf. docs/STATUT.md).
"""
import sys
from pathlib import Path

CASES = ["case_kEpsilon", "case_kOmegaSST", "case_laminar"]
COLUMNS = ["time", "n", "URef", "J", "KT", "10KQ", "eta0"]


def find_performance_file(case_dir: Path) -> Path | None:
    pp = case_dir / "postProcessing" / "propellerInfo1"
    if not pp.is_dir():
        return None
    # Le sous-dossier est nommé par le temps de démarrage de la fonction (souvent "0")
    candidates = sorted(pp.glob("*/propellerPerformance.dat"))
    return candidates[-1] if candidates else None


def read_rows(path: Path) -> list[dict]:
    with open(path) as f:
        lines = [l for l in f if not l.startswith("#") and l.strip()]
    if not lines:
        raise ValueError(f"Aucune donnée dans {path}")
    return [dict(zip(COLUMNS, l.split())) for l in lines]


def average_last_revolution(rows: list[dict]) -> dict:
    n = float(rows[-1]["n"])  # tr/s, constant sur le cas
    period = 1.0 / n
    t_end = float(rows[-1]["time"])
    window = [r for r in rows if float(r["time"]) >= t_end - period]
    if len(window) < 2:
        window = rows  # dernier tour pas encore écoulé : on prend tout ce qu'il y a
    avg = {}
    for key in ("J", "KT", "10KQ", "eta0"):
        avg[key] = sum(float(r[key]) for r in window) / len(window)
    avg["n_samples"] = len(window)
    avg["t_end"] = t_end
    avg["period_covered"] = t_end >= period
    return avg


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]

    print(f"{'Modèle':<15} {'t_end':>8} {'J':>8} {'KT':>10} {'10*KQ':>10} {'eta0':>8}  (moyenne dernier tour, n échantillons)")
    missing = []
    for case in CASES:
        case_dir = root / case
        perf_file = find_performance_file(case_dir)
        if perf_file is None:
            missing.append(case)
            print(f"{case:<15} {'—':>8} {'—':>8} {'—':>10} {'—':>10} {'—':>8}  (non calculé)")
            continue
        rows = read_rows(perf_file)
        avg = average_last_revolution(rows)
        flag = "" if avg["period_covered"] else "  ⚠ < 1 tour écoulé, moyenne partielle"
        print(
            f"{case:<15} {avg['t_end']:>8.4f} {avg['J']:>8.4f} {avg['KT']:>10.4f} "
            f"{avg['10KQ']:>10.4f} {avg['eta0']:>8.4f}  ({avg['n_samples']} ech.){flag}"
        )

    if missing:
        print(f"\nCas non calculés : {', '.join(missing)} — lancer 02_run.sh d'abord.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
