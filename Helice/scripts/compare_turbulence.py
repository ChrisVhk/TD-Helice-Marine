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


def find_performance_files(case_dir: Path) -> list[Path]:
    pp = case_dir / "postProcessing" / "propellerInfo1"
    if not pp.is_dir():
        return []
    # Un cas repris crée un sous-dossier par temps de redémarrage (0/, 0.022/, 0.034/…).
    # On les prend TOUS et on recoud la série (cf. STATUT.md) — ne pas se contenter du dernier.
    # Tri par temps de démarrage CROISSANT (numérique, pas lexical) : un segment repris
    # plus tard doit être lu après le segment d'origine pour l'écraser sur les temps communs.
    def start_time(p: Path) -> float:
        try:
            return float(p.parent.name)
        except ValueError:
            return -1.0
    return sorted(pp.glob("*/propellerPerformance.dat"), key=start_time)


def read_rows(paths: list[Path]) -> list[dict]:
    if not paths:
        raise ValueError("Aucun fichier propellerPerformance.dat")
    merged: dict[float, dict] = {}
    for path in paths:
        with open(path) as f:
            for l in f:
                if l.startswith("#") or not l.strip():
                    continue
                parts = l.split()
                if len(parts) < len(COLUMNS):
                    continue
                row = dict(zip(COLUMNS, parts))
                # un segment plus récent écrase un temps déjà vu (reprise après pas corrompu)
                merged[round(float(row["time"]), 9)] = row
    if not merged:
        raise ValueError(f"Aucune donnée dans {[str(p) for p in paths]}")
    return [merged[t] for t in sorted(merged)]


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
        perf_files = find_performance_files(case_dir)
        if not perf_files:
            missing.append(case)
            print(f"{case:<15} {'—':>8} {'—':>8} {'—':>10} {'—':>10} {'—':>8}  (non calculé)")
            continue
        rows = read_rows(perf_files)
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
