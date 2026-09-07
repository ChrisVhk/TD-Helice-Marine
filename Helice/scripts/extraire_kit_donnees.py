#!/usr/bin/env python3
"""Produit le kit de données distribué aux étudiants (le calcul ne tourne pas en séance).

Deux sorties, indépendantes :

  --csv     data/perf_<fermeture>.csv   — séries temporelles scalaires des 3 cas.
            Colonnes : time,n,URef,J,KT,10KQ,eta0. < 1 Mo au total. VERSIONNÉ.
            Sert aux séances 1 et 2 et à l'inter-séance A.

  --champs  data/paraview_kit/          — sélection de pas de temps reconstruits pour
            ParaView (séance 3). ~750 Mo. NON versionné (gitignore) — à régénérer /
            distribuer à part. Par défaut : 5 pas du dernier tour sur case_kOmegaSST
            + 1 pas (t=0,06) sur les deux autres.

Usage :  python3 scripts/extraire_kit_donnees.py --csv
         python3 scripts/extraire_kit_donnees.py --champs
"""
import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compare_turbulence import find_performance_files, read_rows, COLUMNS  # noqa: E402

CASES = {"case_kEpsilon": "kEpsilon", "case_kOmegaSST": "kOmegaSST", "case_laminar": "laminar"}
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def make_csv() -> None:
    DATA.mkdir(exist_ok=True)
    for case, short in CASES.items():
        rows = read_rows(find_performance_files(ROOT / case))
        out = DATA / f"perf_{short}.csv"
        with open(out, "w") as f:
            f.write(",".join(COLUMNS) + "\n")
            for r in rows:
                f.write(",".join(r[c] for c in COLUMNS) + "\n")
        kb = out.stat().st_size / 1024
        print(f"  {out.relative_to(ROOT)}  ({len(rows)} lignes, {kb:.0f} Ko)")


def _reconstructed_times(case_dir: Path) -> list[str]:
    return sorted(
        (p.name for p in case_dir.iterdir() if p.is_dir() and _isfloat(p.name) and p.name != "0"),
        key=float,
    )


def _isfloat(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def make_champs(n_last: int = 5) -> None:
    kit = DATA / "paraview_kit"
    if kit.exists():
        shutil.rmtree(kit)
    for case in CASES:
        src = ROOT / case
        times = _reconstructed_times(src)
        if not times:
            print(f"  ⚠ {case} : aucun pas reconstruit — lancer reconstructPar d'abord.")
            continue
        keep = times[-n_last:] if case == "case_kOmegaSST" else times[-1:]
        dst = kit / case
        dst.mkdir(parents=True)
        for sub in ("constant", "system"):
            if (src / sub).exists():
                shutil.copytree(src / sub, dst / sub, ignore=shutil.ignore_patterns("polyMesh"))
        shutil.copytree(src / "constant" / "polyMesh", dst / "constant" / "polyMesh")
        for t in keep:
            shutil.copytree(src / t, dst / t)
        (dst / f"{case}.foam").touch()
        print(f"  {dst.relative_to(ROOT)} : pas {keep}")
    total = sum(f.stat().st_size for f in kit.rglob("*") if f.is_file()) / 1e6
    print(f"  total kit champs : {total:.0f} Mo")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", action="store_true", help="produit data/perf_*.csv (versionné)")
    ap.add_argument("--champs", action="store_true", help="produit data/paraview_kit/ (~750 Mo, non versionné)")
    ap.add_argument("--n-last", type=int, default=5, help="nb de pas du dernier tour pour case_kOmegaSST")
    a = ap.parse_args()
    if not (a.csv or a.champs):
        ap.error("préciser --csv et/ou --champs")
    if a.csv:
        print("CSV (séances 1-2) :")
        make_csv()
    if a.champs:
        print("Champs ParaView (séance 3) :")
        make_champs(a.n_last)
