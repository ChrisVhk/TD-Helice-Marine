#!/usr/bin/env python3
"""Mesure la dérive intra-dernier-tour de K_T -- LOT 3, consigne du 18/09
« Aire-developpee-et-theorie ». Remplace le verdict binaire ÉTABLI/NON ÉTABLI
du 17/09 (LOT 1, consigne « Quatre tours ») : ce verdict comparait la dérive à
l'amplitude crête-à-crête du signal, un seuil qui PÉNALISE un cas d'autant plus
qu'il est stable (petite amplitude) -- exactement le défaut qui faisait
ressortir `case_kEpsilon_layers` en « NON ÉTABLI » alors que sa dérive absolue
était minime, simplement rapportée à une amplitude elle-même petite. Leçon
(JOURNAL 18/09) : un seuil doit être rapporté à ce qu'on veut DÉCIDER, pas à
une grandeur du signal lui-même.

Rapporte TROIS nombres, SANS VERDICT -- la décision reste à l'enseignant :
  1. dérive intra-dernier-tour, en % de la moyenne ;
  2. la même, en % de l'amplitude crête-à-crête (CONTEXTE seulement -- ne
     décide plus de rien, gardée pour la comparaison avec l'ancienne règle) ;
  3. la même, en % de L'EFFET QU'ON CHERCHE À MESURER -- SEUL nombre qui
     décide de quelque chose : si la dérive résiduelle est une grosse
     fraction de l'effet qu'on veut lire sur la courbe, l'effet n'est pas
     mesurable en toute confiance ; si elle en est une fraction négligeable,
     elle importe peu même si elle paraît « grande » en % d'amplitude.

Découpe la série en demi-tours de largeur T/2, ANCRÉS EN RECULANT depuis t_end
(la dernière fenêtre est donc exactement la 2e moitié du dernier tour, la
précédente sa 1re moitié -- même découpage que `bilan_helice.py`/
`METHODO_DONNEES.md` §4). Une fenêtre qui mordrait sur le transitoire exclu
(T_TRANSIENT_SKIP, même filtre que `bilan_helice.py`) est rejetée entière.

Usage :
    python3 _Setup/outils/tester_regime_etabli.py               # les trois cas sans couches
    python3 _Setup/outils/tester_regime_etabli.py kEpsilon
    python3 _Setup/outils/tester_regime_etabli.py --fichier Helice/data/perf_kEpsilon_layers.csv --effet couches
"""
import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATA = ROOT / "Helice" / "data"

N_TR_S = 158 / (2 * 3.141592653589793)  # dynamicMeshDict, omega/2pi -- METHODO_DONNEES.md §3
PERIOD_S = 1.0 / N_TR_S  # 0,039767 s

# Démarrage impulsif : même filtre que bilan_helice.py/tracer_series_temporelles.py.
T_TRANSIENT_SKIP = 0.001

# Amplitude crête-à-crête de K_T, fenêtre commune -- sourcé PARAMETRES_CAS.md,
# jamais recalculée ici (dépend de la fenêtre de mesure, voir METHODO_DONNEES.md §6).
# CONTEXTE seulement depuis le 18/09 -- ne décide plus rien (voir docstring).
# 20/09 : amplitude crête-à-crête de K_T dans le DERNIER TOUR COMPLET à 4,00 tours ([0,1193 ; 0,1591] s,
# Helice/scripts/comparaison_modeles.py). Les valeurs antérieures (0,0176 / 0,0223 / 0,0242, fenêtre
# commune à 1,5 tour) étaient GONFLÉES par le transitoire des deux premiers tours : 4 à 5 fois trop grandes.
AMPLITUDE_CC = {"kEpsilon": 0.0039, "kOmegaSST": 0.0048, "laminar": 0.0048}

# L'EFFET cherché, celui qui décide -- deux comparaisons distinctes dans ce TD :
# (a) séance 2, les trois fermetures de turbulence entre elles : écart max-min
#     de K_T (0,2261-0,2170=0,0091 ; 0,00914 cité par la consigne du 18/09,
#     écart d'arrondi négligeable) ;
# (b) la comparaison avec/sans couches : écart K_T avec-sans, PROVISOIRE (LOT 2,
#     consigne du 18/09, mesuré sur une fenêtre commune alors qu'AUCUN des deux
#     cas n'était établi -- à refaire une fois les deux le seront).
# 20/09 : 0,0096 = K_T laminar - K_T kEpsilon, moyennes du dernier tour complet à 4,00 tours
# (0,2295 - 0,2199 ; comparaison_modeles.py). Remplace 0,00914 (fenêtre à 1,5 tour, 0,2261 - 0,2170).
EFFET_INTER_MODELES = 0.0096
EFFET_COUCHES = 0.00281


def read_csv_case(case):
    path = DATA / f"perf_{case}.csv"
    return read_csv_fichier(path)


def read_csv_fichier(path):
    with open(path, newline="") as f:
        rows = [dict(r) for r in csv.DictReader(f)]
    return [r for r in rows if float(r["time"]) >= T_TRANSIENT_SKIP]


def demi_tours(rows, t_end, half):
    """Découpe en fenêtres de largeur `half`, ancrées en reculant depuis
    `t_end`. Rejette entière la fenêtre la plus ancienne si elle mordrait sur
    le transitoire exclu. Retourne [(t0, t1, moyenne_KT), ...] en ordre
    chronologique."""
    times = [float(r["time"]) for r in rows]
    t_min = min(times)
    fenetres = []
    t1 = t_end
    while True:
        t0 = t1 - half
        if t0 < t_min - 1e-9:
            break
        vals = [float(r["KT"]) for r in rows if t0 - 1e-9 <= float(r["time"]) <= t1 + 1e-9]
        if not vals:
            break
        fenetres.append((t0, t1, sum(vals) / len(vals)))
        t1 = t0
    fenetres.reverse()
    return fenetres


def tester(rows, nom, amp=None, effet=None, effet_label=""):
    t_end = max(float(r["time"]) for r in rows)
    half = PERIOD_S / 2
    fenetres = demi_tours(rows, t_end, half)

    print(f"\n=== {nom} ===")
    print(f"t_end = {t_end:.6f} s -- période T = {PERIOD_S:.6f} s -- demi-tour = {half:.6f} s")
    print(f"{'fenêtre (s)':<24}{'K_T moyen':>12}  {'dérive vs préc.':>16}")
    prec = None
    for (t0, t1, moy) in fenetres:
        derive_str = "--" if prec is None else f"{(moy - prec) / prec * 100:+.2f} %"
        print(f"[{t0:.5f};{t1:.5f}]{'':<3}{moy:12.5f}  {derive_str:>16}")
        prec = moy

    if len(fenetres) < 2:
        print("Pas assez de demi-tours complets pour mesurer la dérive du dernier tour.")
        return None

    (_, _, m1), (_, _, m2) = fenetres[-2], fenetres[-1]
    derive_abs = m2 - m1
    derive_pct_moyenne = derive_abs / m1 * 100
    derive_pct_amplitude = derive_abs / amp * 100 if amp else None
    derive_pct_effet = derive_abs / effet * 100 if effet else None

    print(f"\nDérive intra-dernier-tour (1re moitié -> 2e), valeur absolue : {derive_abs:+.5f}")
    print(f"  1. en % de la moyenne                 : {derive_pct_moyenne:+.2f} %")
    if derive_pct_amplitude is not None:
        print(f"  2. en % de l'amplitude crête-à-crête   : {derive_pct_amplitude:+.1f} %  (contexte seulement, amplitude={amp})")
    else:
        print(f"  2. en % de l'amplitude crête-à-crête   : amplitude inconnue pour ce cas")
    if derive_pct_effet is not None:
        print(f"  3. en % de l'effet cherché ({effet_label}) : {derive_pct_effet:+.1f} %  (effet={effet}) -- CELUI QUI DÉCIDE")
    else:
        print(f"  3. en % de l'effet cherché              : effet non fourni (--effet)")
    print("Aucun verdict : la décision (l'effet est-il mesurable avec confiance) revient à l'enseignant.")
    return derive_pct_moyenne, derive_pct_amplitude, derive_pct_effet


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cases", nargs="*", help="noms de cas (kEpsilon, kOmegaSST, laminar) -- défaut : les trois")
    ap.add_argument("--fichier", help="chemin direct vers un CSV (pour un cas hors des trois standards, ex. couches)")
    ap.add_argument("--effet", choices=["modeles", "couches"], help="quel EFFET utiliser pour le nombre 3 avec --fichier")
    a = ap.parse_args()

    if a.fichier:
        rows = read_csv_fichier(Path(a.fichier))
        effet, label = (EFFET_COUCHES, "avec-sans couches, provisoire") if a.effet == "couches" else (EFFET_INTER_MODELES, "inter-modèles")
        tester(rows, Path(a.fichier).stem, amp=None, effet=effet, effet_label=label)
        return

    cases = a.cases or ["kEpsilon", "kOmegaSST", "laminar"]
    for case in cases:
        rows = read_csv_case(case)
        amp = AMPLITUDE_CC.get(case)
        tester(rows, case, amp=amp, effet=EFFET_INTER_MODELES, effet_label="inter-modèles (max-min K_T sans couches)")


if __name__ == "__main__":
    main()
