#!/usr/bin/env python3
"""Compare KT, KQ, eta0 entre les 3 fermetures de turbulence (case_kEpsilon,
case_kOmegaSST, case_laminar) à partir de postProcessing/propellerInfo1/*/propellerPerformance.dat
(function object OpenFOAM natif du tutoriel propeller, colonnes : Time n URef J KT 10*KQ eta0).

**Attention (20/09, soir).** Ce script lit le BRUT du solveur : le `J` (et donc l'`eta0`) qu'il affiche est celui du
solveur, calculé avec `URef`, une vitesse mesurée à 0,17 D EN AVAL des pales (zone d'induction) -- pas une avance.
Il est étiqueté `J_solv` / `eta0_solv` pour cette raison. Les valeurs de référence du TD (J imposé 0,8743, eta0
correspondant) sont dans `data/perf_*.csv` et `scripts/comparaison_modeles.py` ; voir `scripts/avance_imposee.py`.
K_T et K_Q, eux, ne dépendent que de n et D.

KT/KQ/eta0 oscillent avec la période de rotation (T = 1/n, passage de pale) : ce script moyenne
sur le DERNIER TOUR COMPLET écoulé plutôt que de lire la dernière ligne seule (une valeur
instantanée tomberait sur un point arbitraire du cycle, cf. docs/STATUT.md).
"""
import re
import sys
from pathlib import Path

CASES = ["case_kEpsilon", "case_kOmegaSST", "case_laminar"]
COLUMNS = ["time", "n", "URef", "J", "KT", "10KQ", "eta0"]


def _cle_segment(p: Path):
    """Ordre chronologique d'écriture : (temps de démarrage du dossier, fichier normal avant fichier
    suffixé, n° du suffixe). OpenFOAM crée `propellerPerformance_<t>.dat` quand le fichier normal
    existe déjà dans le dossier de redémarrage : le suffixé est donc TOUJOURS le plus récent."""
    try:
        t = float(p.parent.name)
    except ValueError:
        t = -1.0
    if p.name == "propellerPerformance.dat":
        return (t, 0, 0.0)
    m = re.fullmatch(r"propellerPerformance_(.+)\.dat", p.name)
    try:
        suf = float(m.group(1)) if m else 0.0
    except ValueError:
        suf = 0.0
    return (t, 1, suf)


def find_performance_files(case_dir: Path) -> list[Path]:
    """TOUS les segments du cas, normaux ET suffixés, dans l'ordre d'écriture.

    Un cas repris crée un sous-dossier par temps de redémarrage (0/, 0.022/, 0.034/…) ; un
    redémarrage à un temps déjà occupé écrit un fichier SUFFIXÉ (`propellerPerformance_0.06.dat`)
    à côté du normal. Jusqu'au 20/09 seuls les fichiers normaux étaient lus : les CSV de laminar
    (suffixé jusqu'à 4,00 tours) restaient figés à 1,52 tour. Les fichiers vides et le sous-dossier
    `_archive_ambigu/` (hors `*/propellerPerformance*.dat`) sont ignorés."""
    pp = case_dir / "postProcessing" / "propellerInfo1"
    if not pp.is_dir():
        return []
    return sorted((p for p in pp.glob("*/propellerPerformance*.dat") if p.stat().st_size > 0), key=_cle_segment)


class RecollementError(ValueError):
    pass


def recoller(segments: list[dict], tol: float = 1e-6):
    """Recolle des segments d'un même cas (ordre d'écriture croissant) en UNE série sans doublon.

    Règle : un redémarrage RÉÉCRIT tout ce qui suit son début. Le segment le plus récent remplace donc
    tout ce que les segments précédents contenaient à t >= son premier temps -- pas seulement les temps
    exactement identiques (si les pas de temps diffèrent, une fusion par temps égal laisserait deux
    séries entrelacées). Chaque segment est un dict {path, brut, sortie} : `brut` (lignes telles
    qu'écrites par le solveur), `sortie` (mêmes lignes rééchelonnées au D correct, ou identiques au brut).
    Contrôles, qui REFUSENT plutôt que de corriger (RecollementError) :
      - aux temps exactement communs, les valeurs (KT, 10KQ, eta0) doivent coïncider à `tol` près,
        comparées dans la MÊME UNITÉ : sortie contre sortie. Jamais une valeur rééchelonnée contre une
        valeur brute (faux positif constaté le 20/09 : 0,2219 contre 0,3707 sur kOmegaSST, écart nul en
        réalité), et jamais brut contre brut entre deux segments de rayon d'en-tête différent (le
        segment de reprise post-14/09 est écrit au rayon corrigé : ses valeurs brutes valent ~0,6 fois
        celles d'avant, à raison) ;
      - un segment plus récent qui s'arrête AVANT la fin du précédent ferait perdre la queue de celui-ci.
    Retourne (lignes de sortie, lignes de rapport)."""
    rapport = []
    courant: list[tuple[float, dict, dict, Path]] = []  # (t, brut, sortie, path)
    for seg in segments:
        if not seg["brut"]:
            continue
        t0 = round(float(seg["brut"][0]["time"]), 9)
        t1 = round(float(seg["brut"][-1]["time"]), 9)
        ancien = [e for e in courant if e[0] >= t0]
        if ancien:
            fin_ancien = max(e[0] for e in ancien)
            if fin_ancien > t1 + 1e-12:
                raise RecollementError(
                    f"{seg['path']} (t={t0}..{t1}) est plus récent mais s'arrête AVANT la fin du segment "
                    f"précédent ({fin_ancien}) : sa queue serait perdue -- à trancher, pas en silence.")
            par_temps = {round(float(r["time"]), 9): r for r in seg["sortie"]}
            communs = [e for e in ancien if e[0] in par_temps]
            ecart = 0.0
            for (t, _brut, sortie, path) in communs:
                for col in ("KT", "10KQ", "eta0"):
                    a, b = float(sortie[col]), float(par_temps[t][col])
                    if a and abs(a - b) / abs(a) > tol:
                        raise RecollementError(
                            f"t={t} couvert par {path} ET {seg['path']} avec des valeurs {col} différentes "
                            f"à D égal ({a} vs {b}) -- recouvrement incohérent, pas un redémarrage déterministe.")
                    if a:
                        ecart = max(ecart, abs(a - b) / abs(a))
            rapport.append(f"  {Path(seg['path']).parent.name}/{Path(seg['path']).name} (dès t={t0}) remplace "
                           f"{len(ancien)} ligne(s) antérieure(s) dont {len(communs)} à temps identique "
                           f"(écart max, D égal : {ecart:.1e})")
        courant = [e for e in courant if e[0] < t0]
        for brut, sortie in zip(seg["brut"], seg["sortie"]):
            courant.append((round(float(brut["time"]), 9), brut, sortie, seg["path"]))
    if not courant:
        raise RecollementError("aucune donnée dans les segments fournis")
    courant.sort(key=lambda e: e[0])
    return [e[2] for e in courant], rapport


def read_rows(paths: list[Path]) -> list[dict]:
    if not paths:
        raise ValueError("Aucun fichier propellerPerformance*.dat")
    segments = []
    for path in paths:
        rows = []
        with open(path) as f:
            for l in f:
                if l.startswith("#") or not l.strip():
                    continue
                parts = l.split()
                if len(parts) < len(COLUMNS):
                    continue
                rows.append(dict(zip(COLUMNS, parts)))
        segments.append({"path": path, "brut": rows, "sortie": rows})
    return recoller(segments)[0]


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

    print(f"{'Modèle':<15} {'t_end':>8} {'J_solv':>8} {'KT':>10} {'10*KQ':>10} {'eta0_solv':>9}  (moyenne dernier tour, n échantillons ; J_solv et eta0_solv : voir l'en-tête du script)")
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
            f"{avg['10KQ']:>10.4f} {avg['eta0']:>9.4f}  ({avg['n_samples']} ech.){flag}"
        )

    if missing:
        print(f"\nCas non calculés : {', '.join(missing)} — lancer 02_run.sh d'abord.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
