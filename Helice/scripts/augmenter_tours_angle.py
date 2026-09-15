#!/usr/bin/env python3
"""Ajoute deux colonnes (tours, angle_deg) à data/perf_<modele>.csv (LOT A3, consigne
du 15/09) : les étudiants raisonnent en tours de l'hélice, les CSV ne portaient que le
temps en secondes.

    tours     = time * n
    angle_deg = (360 * time * n) mod 360

n = 25,146 tr/s -- PLUS PRÉCIS que le n=25,15 arrondi de `system/propellerInfo` :
calculé depuis omega=158 rad/s (`constant/dynamicMeshDict:29`, n = omega/2π), source
indépendante de la même rotation, cf. `Helice/docs/PARAMETRES_CAS.md`.

Ne détruit aucune donnée : le CSV d'origine (sans les deux colonnes) est conservé sous
le suffixe explicite `_sans_tours.csv` avant d'écrire la version augmentée au nom
d'origine. Idempotent : relancé sur un CSV déjà augmenté, régénère la sauvegarde
`_sans_tours.csv` depuis les colonnes d'origine (les deux nouvelles colonnes sont
retirées avant sauvegarde, pas dupliquées) puis réécrit la version augmentée à
l'identique.

Usage : python3 Helice/scripts/augmenter_tours_angle.py
"""
import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

N_TR_S = 158 / (2 * math.pi)  # 25,1465 tr/s -- omega/2pi, dynamicMeshDict:29

ORIG_COLUMNS = ["time", "n", "URef", "J", "KT", "10KQ", "eta0"]
NEW_COLUMNS = ORIG_COLUMNS + ["tours", "angle_deg"]

CASES = ["kEpsilon", "kOmegaSST", "laminar"]


def process(short: str) -> None:
    csv_path = DATA / f"perf_{short}.csv"
    backup_path = DATA / f"perf_{short}_sans_tours.csv"

    if not csv_path.is_file():
        print(f"  ⚠ {csv_path.relative_to(ROOT)} introuvable, ignoré.")
        return

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        rows = [dict(r) for r in reader]

    # Toujours repartir des colonnes d'origine (idempotent) : si le fichier est déjà
    # augmenté, on ignore ses colonnes tours/angle_deg plutôt que de les recopier.
    with open(backup_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(ORIG_COLUMNS)
        for r in rows:
            w.writerow([r[c] for c in ORIG_COLUMNS])

    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(NEW_COLUMNS)
        for r in rows:
            t = float(r["time"])
            tours = t * N_TR_S
            angle_deg = (360.0 * t * N_TR_S) % 360.0
            w.writerow([r[c] for c in ORIG_COLUMNS] + [f"{tours:.6f}", f"{angle_deg:.4f}"])

    print(f"  {csv_path.relative_to(ROOT)}  ({len(rows)} lignes augmentées)")
    print(f"  {backup_path.relative_to(ROOT)}  (origine conservée, {len(rows)} lignes)")


def main() -> None:
    print(f"n = {N_TR_S:.6f} tr/s (omega=158 rad/s / 2*pi, dynamicMeshDict:29)")
    for short in CASES:
        process(short)


if __name__ == "__main__":
    main()
