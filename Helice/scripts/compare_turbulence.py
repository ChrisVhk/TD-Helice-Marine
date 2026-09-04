#!/usr/bin/env python3
"""Compare KT, KQ, eta0 entre les 3 fermetures de turbulence (case_kEpsilon,
case_kOmegaSST, case_laminar) à partir de postProcessing/propellerInfo1/*/propellerPerformance.dat
(function object OpenFOAM natif du tutoriel propeller, colonnes : Time n URef J KT 10*KQ eta0).
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


def read_last_row(path: Path) -> dict:
    with open(path) as f:
        lines = [l for l in f if not l.startswith("#") and l.strip()]
    if not lines:
        raise ValueError(f"Aucune donnée dans {path}")
    values = lines[-1].split()
    return dict(zip(COLUMNS, values))


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]

    print(f"{'Modèle':<15} {'J':>8} {'KT':>10} {'10*KQ':>10} {'eta0':>8}")
    missing = []
    for case in CASES:
        case_dir = root / case
        perf_file = find_performance_file(case_dir)
        if perf_file is None:
            missing.append(case)
            print(f"{case:<15} {'—':>8} {'—':>10} {'—':>10} {'—':>8}  (non calculé)")
            continue
        row = read_last_row(perf_file)
        print(
            f"{case:<15} {row['J']:>8} {row['KT']:>10} {row['10KQ']:>10} {row['eta0']:>8}"
        )

    if missing:
        print(f"\nCas non calculés : {', '.join(missing)} — lancer 02_run.sh d'abord.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
