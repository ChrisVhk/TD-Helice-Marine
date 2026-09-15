#!/usr/bin/env python3
"""Produit le kit de données distribué aux étudiants (le calcul ne tourne pas en séance).

Deux sorties, indépendantes :

  --csv     data/perf_<fermeture>.csv   — séries temporelles scalaires des 3 cas.
            Colonnes : time,n,URef,J,KT,10KQ,eta0,tours,angle_deg. < 1 Mo au total.
            VERSIONNÉ. Sert aux séances 1 et 2 et à l'inter-séance A.

  --champs  data/paraview_kit/          — sélection de pas de temps reconstruits pour
            ParaView (séance 3). ~750 Mo. NON versionné (gitignore) — à régénérer /
            distribuer à part. Par défaut : 5 pas du dernier tour sur case_kOmegaSST
            + 1 pas (t=0,06) sur les deux autres.

## Le rééchelonnement (décision enseignant du 15/09, INV-19)

`postProcessing/propellerInfo1/*/propellerPerformance.dat` est le BRUT produit par le
solveur -- l'enregistrement de ce qui a réellement tourné, avec `radius 0.1` (D=0,2 m).
**On ne réécrit jamais une mesure** : le brut reste intact, pour toujours faux au sens
où D=0,2 m n'a jamais été la géométrie réelle (corrigée le 14/09 à D=0,227378 m). La
correction vit ICI, dans ce script, PAS dans le brut :

    J     × (D_hist/D_correct)^1
    K_T   × (D_hist/D_correct)^4
    10K_Q × (D_hist/D_correct)^5
    eta0  inchangé (invariant par construction : eta0 = J·KT/(KQ·2π), D s'annule)

**Aucun facteur codé en dur** : `D_hist` est lu dans l'en-tête `# Radius` du brut
lui-même (auto-documenté par le solveur qui l'a produit) ; `D_correct` est lu dans
`Helice/docs/PARAMETRES_CAS.md` (source unique de vérité du cas). Si l'un des deux
change, le facteur se recalcule seul -- rien à retoucher ici.

Voir `Helice/docs/METHODO_DONNEES.md` pour la chaîne complète et le détail de ce
qui a changé le 15/09 (avant cette date, le rééchelonnement était fait À LA MAIN sur
les CSV, jamais capturé en code -- irreproductible, cf. JOURNAL du 15/09).

Usage :  python3 scripts/extraire_kit_donnees.py --csv
         python3 scripts/extraire_kit_donnees.py --champs
"""
import argparse
import csv
import math
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compare_turbulence import find_performance_files, read_rows, COLUMNS  # noqa: E402

CASES = {"case_kEpsilon": "kEpsilon", "case_kOmegaSST": "kOmegaSST", "case_laminar": "laminar"}
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PARAMETRES_CAS = ROOT / "docs" / "PARAMETRES_CAS.md"

OUT_COLUMNS = COLUMNS + ["tours", "angle_deg"]

_RADIUS_RE = re.compile(r"#\s*Radius\s*:\s*([\d.eE+-]+)")
_D_CORRECT_RE = re.compile(r"\|\s*D \(diamètre\)\s*\|\s*([\d,]+)\s*\|\s*m\s*\|")


def _d_historique(paths: list[Path]) -> float:
    """Lit le radius historique dans l'en-tête du brut (n'importe quel segment,
    tous identiques -- vérifié le 15/09 sur les trois cas)."""
    with open(paths[0]) as f:
        for line in f:
            m = _RADIUS_RE.match(line)
            if m:
                return 2.0 * float(m.group(1))
    raise SystemExit(f"En-tête '# Radius' introuvable dans {paths[0]} -- brut inattendu.")


def _d_correct() -> float:
    """Lit le D établi dans PARAMETRES_CAS.md -- source unique de vérité, jamais recopié."""
    text = PARAMETRES_CAS.read_text(encoding="utf-8")
    m = _D_CORRECT_RE.search(text)
    if not m:
        raise SystemExit(f"Ligne 'D (diamètre)' introuvable dans {PARAMETRES_CAS}.")
    return float(m.group(1).replace(",", "."))


def _rescale(row: dict, ratio: float) -> dict:
    """ratio = D_historique / D_correct -- multiplie J^1, K_T^4, 10K_Q^5 ; eta0 inchangé."""
    out = dict(row)
    out["J"] = f"{float(row['J']) * ratio:.6e}"
    out["KT"] = f"{float(row['KT']) * ratio**4:.6e}"
    out["10KQ"] = f"{float(row['10KQ']) * ratio**5:.6e}"
    return out


def make_csv() -> None:
    DATA.mkdir(exist_ok=True)
    d_correct = _d_correct()
    n_tr_s = 158 / (2 * math.pi)  # dynamicMeshDict:29, omega/2pi -- même valeur que le BLOC A

    for case, short in CASES.items():
        perf_files = find_performance_files(ROOT / case)
        rows = read_rows(perf_files)
        d_hist = _d_historique(perf_files)
        ratio = d_hist / d_correct

        out = DATA / f"perf_{short}.csv"
        with open(out, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(OUT_COLUMNS)
            for r in rows:
                r = _rescale(r, ratio)
                t = float(r["time"])
                tours = t * n_tr_s
                angle_deg = (360.0 * t * n_tr_s) % 360.0
                w.writerow([r[c] for c in COLUMNS] + [f"{tours:.6f}", f"{angle_deg:.4f}"])
        kb = out.stat().st_size / 1024
        print(f"  {out.relative_to(ROOT)}  ({len(rows)} lignes, {kb:.0f} Ko, "
              f"D_hist={d_hist:.6f} m -> D_correct={d_correct:.6f} m, ratio={ratio:.6f})")


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
