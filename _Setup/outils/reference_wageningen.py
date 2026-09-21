#!/usr/bin/env python3
"""Référence extérieure indépendante : polynômes de la série B de Wageningen --
LOT 2, consigne du 17/09 « Pale-série-B-réserve-et-référence-externe ».

**Référence bibliographique complète** :
Oosterveld, M.W.C. et van Oossanen, P. (1975). « Further Computer-Analyzed Data
of the Wageningen B-Screw Series ». International Shipbuilding Progress, 22(251),
p. 251-262. Régression multiple sur les essais en bassin de 120 modèles de la
série B (N.S.M.B., Wageningen), Reynolds = 2×10⁶. 39 termes pour K_T, 47 termes
pour K_Q, chacun un monôme C·J^s·(P/D)^t·(A_E/A_0)^u·Z^v.

**Coefficients SOURCÉS, pas recopiés de mémoire** : extraits le 17/09 de
`LIBRARY/modeling/utiles/WageningData.txt`, dépôt `cybergalactic/MSS` (Marine
Systems Simulator, T. Fossen, NTNU -- bibliothèque marine open-source, référence
académique établie), qui cite lui-même Oosterveld & van Oossanen (1975) et
Barnitsas, Ray & Kinley (1981) « KT, KQ and Efficiency Curves for the Wageningen
B-Series Propellers », Univ. of Michigan. URL exacte :
https://raw.githubusercontent.com/cybergalactic/MSS/master/LIBRARY/modeling/utiles/WageningData.txt
Comptage vérifié à l'extraction : exactement 39 lignes K_T et 47 lignes K_Q --
correspond au nombre de termes documenté dans la littérature (confirme qu'aucune
ligne n'a été perdue/dupliquée pendant l'extraction). Trois premiers coefficients
K_T (0,00880496 / -0,204554 / 0,166351) recoupés indépendamment par recherche web
le même jour -- cohérents avec la table publiée.

**Domaine de validité de la régression** : la série B mesurée couvre P/D ≈ 0,5 à
1,4, A_E/A_0 ≈ 0,3 à 1,05, Z = 2 à 7. **Correction du 18/09** : le P/D utilisé le
17/09 (~2,23 à 2,43) était calculé avec une formule fausse d'un facteur 2 -- la
valeur correcte (P/D=π·(r/R)·tanφ, ~1,12 à 1,21 selon le rayon) est DANS ce
domaine. Les écarts observés le 17/09 (-73 %/-60 %/-33 %) étaient donc
l'artefact de cette formule fausse, pas un signal d'extrapolation hors domaine --
on est maintenant dans les conditions où la comparaison a un sens. Voir
`mesurer_pas_pale.py` et `PARAMETRES_CAS.md` pour la correction, JOURNAL du
18/09 pour le récit.

Usage :
    python3 _Setup/outils/reference_wageningen.py
"""
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "Helice", "Images", "FIG-fon-s7-reference-wageningen.png")

# (C, s, t, u, v) -- K_T = somme C * J^s * (P/D)^t * (Ae/Ao)^u * Z^v
KT = [
    (0.00880496, 0, 0, 0, 0), (-0.204554, 1, 0, 0, 0), (0.166351, 0, 1, 0, 0),
    (0.158114, 0, 2, 0, 0), (-0.147581, 2, 0, 1, 0), (-0.481497, 1, 1, 1, 0),
    (0.415437, 0, 2, 1, 0), (0.0144043, 0, 0, 0, 1), (-0.0530054, 2, 0, 0, 1),
    (0.0143481, 0, 1, 0, 1), (0.0606826, 1, 1, 0, 1), (-0.0125894, 0, 0, 1, 1),
    (0.0109689, 1, 0, 1, 1), (-0.133698, 0, 3, 0, 0), (0.00638407, 0, 6, 0, 0),
    (-0.00132718, 2, 6, 0, 0), (0.168496, 3, 0, 1, 0), (-0.0507214, 0, 0, 2, 0),
    (0.0854559, 2, 0, 2, 0), (-0.0504475, 3, 0, 2, 0), (0.010465, 1, 6, 2, 0),
    (-0.00648272, 2, 6, 2, 0), (-0.00841728, 0, 3, 0, 1), (0.0168424, 1, 3, 0, 1),
    (-0.00102296, 3, 3, 0, 1), (-0.0317791, 0, 3, 1, 1), (0.018604, 1, 0, 2, 1),
    (-0.00410798, 0, 2, 2, 1), (-0.000606848, 0, 0, 0, 2), (-0.0049819, 1, 0, 0, 2),
    (0.0025983, 2, 0, 0, 2), (-0.000560528, 3, 0, 0, 2), (-0.00163652, 1, 2, 0, 2),
    (-0.000328787, 1, 6, 0, 2), (0.000116502, 2, 6, 0, 2), (0.000690904, 0, 0, 1, 2),
    (0.00421749, 0, 3, 1, 2), (5.65229e-05, 3, 6, 1, 2), (-0.00146564, 0, 3, 2, 2),
]

# (C, s, t, u, v) -- 10*K_Q = 10 * somme C * J^s * (P/D)^t * (Ae/Ao)^u * Z^v
KQ = [
    (0.00379368, 0, 0, 0, 0), (0.00886523, 2, 0, 0, 0), (-0.032241, 1, 1, 0, 0),
    (0.00344778, 0, 2, 0, 0), (-0.0408811, 0, 1, 1, 0), (-0.108009, 1, 1, 1, 0),
    (-0.0885381, 2, 1, 1, 0), (0.188561, 0, 2, 1, 0), (-0.00370871, 1, 0, 0, 1),
    (0.00513696, 0, 1, 0, 1), (0.0209449, 1, 1, 0, 1), (0.00474319, 2, 1, 0, 1),
    (-0.00723408, 2, 0, 1, 1), (0.00438388, 1, 1, 1, 1), (-0.0269403, 0, 2, 1, 1),
    (0.0558082, 3, 0, 1, 0), (0.0161886, 0, 3, 1, 0), (0.00318086, 1, 3, 1, 0),
    (0.015896, 0, 0, 2, 0), (0.0471729, 1, 0, 2, 0), (0.0196283, 3, 0, 2, 0),
    (-0.0502782, 0, 1, 2, 0), (-0.030055, 3, 1, 2, 0), (0.0417122, 2, 2, 2, 0),
    (-0.0397722, 0, 3, 2, 0), (-0.00350024, 0, 6, 2, 0), (-0.0106854, 3, 0, 0, 1),
    (0.00110903, 3, 3, 0, 1), (-0.000313912, 0, 6, 0, 1), (0.0035985, 3, 0, 1, 1),
    (-0.00142121, 0, 6, 1, 1), (-0.00383637, 1, 0, 2, 1), (0.0126803, 0, 2, 2, 1),
    (-0.00318278, 2, 3, 2, 1), (0.00334268, 0, 6, 2, 1), (-0.00183491, 1, 1, 0, 2),
    (0.000112451, 3, 2, 0, 2), (-2.97228e-05, 3, 6, 0, 2), (0.000269551, 1, 0, 1, 2),
    (0.00083265, 2, 0, 1, 2), (0.00155334, 0, 2, 1, 2), (0.000302683, 0, 6, 1, 2),
    (-0.0001843, 0, 0, 2, 2), (-0.000425399, 0, 3, 2, 2), (8.69243e-05, 3, 3, 2, 2),
    (-0.0004659, 0, 6, 2, 2), (5.54194e-05, 1, 6, 2, 2),
]

assert len(KT) == 39, f"table K_T incomplete : {len(KT)} termes, 39 attendus"
assert len(KQ) == 47, f"table K_Q incomplete : {len(KQ)} termes, 47 attendus"


def _poly(table, J, PD, AeAo, Z):
    return sum(C * J**s * PD**t * AeAo**u * Z**v for (C, s, t, u, v) in table)


def kt(J, PD, AeAo, Z):
    return _poly(KT, J, PD, AeAo, Z)


def kq(J, PD, AeAo, Z):
    return _poly(KQ, J, PD, AeAo, Z)


def eta0(J, KTv, KQv):
    return (J / (2 * math.pi)) * (KTv / KQv) if KQv else float("nan")


# --- Notre pale : P/D mesuré au LOT 1 (formule de la consigne, r/R=0,7) ---
PD_MESURE = 1.1483  # _Setup/outils/mesurer_pas_pale.py, phi=-27,57 deg, r/R=0,7 -- corrige le 18/09 (P/D=pi*(r/R)*tanphi, pas 2pi)
Z_NOTRE_PALE = 4


def _moyennes_dernier_tour(modele):
    """Moyennes pondérées par le temps (trapèzes) de J, K_T, 10K_Q, eta0 sur le DERNIER TOUR COMPLET (T = 2π/158),
    lues dans `Helice/data/perf_<modele>.csv` -- rien n'est recopié à la main (correction du 20/09, soir).
    `J` du CSV = avance IMPOSÉE V_inlet/(nD) (0,8743, la même pour les trois cas) ; `eta0` est calculé avec elle."""
    import csv
    with open(os.path.join(ROOT, "Helice", "data", f"perf_{modele}.csv")) as f:
        rows = [{k: float(v) for k, v in r.items()} for r in csv.DictReader(f)]
    t1 = rows[-1]["time"]
    t0 = t1 - 2 * math.pi / 158
    pts = [r for r in rows if t0 - 1e-12 <= r["time"] <= t1 + 1e-12]

    def moy(c):
        s_ = sum(0.5 * (pts[i]["time"] - pts[i - 1]["time"]) * (pts[i][c] + pts[i - 1][c]) for i in range(1, len(pts)))
        return s_ / (pts[-1]["time"] - pts[0]["time"])
    return {"J": moy("J"), "KT": moy("KT"), "10KQ": moy("10KQ"), "eta0": moy("eta0")}


# Nos trois points : moyenne du dernier tour complet (4,00 tours), lue dans les CSV du kit. Le J est l'avance IMPOSÉE,
# identique pour les trois cas ; le J « mesuré » du solveur (0,8936 / 0,8936 / 0,8912) reposait sur URef, vitesse
# relevée à 0,17 D en aval des pales, dans l'induction : ce n'était pas une avance (voir avance_imposee.py).
NOS_POINTS = {
    nom: {**_moyennes_dernier_tour(nom), "color": couleur}
    for nom, couleur in (("kEpsilon", "#1f77b4"), ("kOmegaSST", "#d62728"), ("laminar", "#2ca02c"))
}

AEAO_VALEURS = [0.55, 0.70]
J_RANGE = [i * 0.01 for i in range(20, 141)]  # 0,20 a 1,40, pas 0,01


def main():
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.5))
    ax_kt, ax_kq, ax_eta = axes

    for AeAo in AEAO_VALEURS:
        ls = "-" if AeAo == 0.55 else "--"
        label_suffix = f"Aₑ/A₀={AeAo}"
        kts = [kt(J, PD_MESURE, AeAo, Z_NOTRE_PALE) for J in J_RANGE]
        kqs = [kq(J, PD_MESURE, AeAo, Z_NOTRE_PALE) for J in J_RANGE]
        etas = [eta0(J, kt(J, PD_MESURE, AeAo, Z_NOTRE_PALE), kq(J, PD_MESURE, AeAo, Z_NOTRE_PALE)) for J in J_RANGE]
        ax_kt.plot(J_RANGE, kts, ls, color="black", lw=1.3, label=f"série B, {label_suffix}")
        ax_kq.plot(J_RANGE, [10 * v for v in kqs], ls, color="black", lw=1.3, label=f"série B, {label_suffix}")
        ax_eta.plot(J_RANGE, etas, ls, color="black", lw=1.3, label=f"série B, {label_suffix}")

    for nom, d in NOS_POINTS.items():
        ax_kt.scatter([d["J"]], [d["KT"]], color=d["color"], zorder=5, s=60, label=nom)
        ax_kq.scatter([d["J"]], [d["10KQ"]], color=d["color"], zorder=5, s=60, label=nom)
        ax_eta.scatter([d["J"]], [d["eta0"]], color=d["color"], zorder=5, s=60, label=nom)

    ax_kt.set_xlabel("J"); ax_kt.set_ylabel("$K_T$"); ax_kt.set_title("$K_T(J)$")
    ax_kq.set_xlabel("J"); ax_kq.set_ylabel("$10K_Q$"); ax_kq.set_title("$10K_Q(J)$")
    ax_eta.set_xlabel("J"); ax_eta.set_ylabel(r"$\eta_0$"); ax_eta.set_title(r"$\eta_0(J)$")
    # η0 = J K_T / (2π K_Q) a un pôle là où K_Q polynomial s'annule (J ≈ 1,28) : sans borne, il écrase l'axe et
    # cache les points de calcul (figure jugée illisible le 20/09). On borne à la plage physique.
    ax_eta.set_ylim(0.0, 1.0)
    ax_eta.set_xlim(0.2, 1.25)
    for ax in axes:
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=7)

    fig.suptitle(f"Série B de Wageningen, Z={Z_NOTRE_PALE}, P/D={PD_MESURE:.3f} (mesuré, r/R=0,7) -- "
                 f"Oosterveld & van Oossanen (1975)", fontsize=10)
    fig.text(0.5, 0.01,
              "Notre pale n'est pas une série B. Cette comparaison teste la vraisemblance, elle ne valide rien.",
              ha="center", fontsize=10, weight="bold", color="#8a0000")
    fig.tight_layout(rect=(0, 0.04, 1, 0.95))
    fig.savefig(OUT, dpi=150, facecolor="white")
    print(f"écrit : {OUT}")

    print(f"\n=== Écarts chiffrés, chaque cas à son J (avance imposée, commune) (moyenne des deux Ae/Ao={AEAO_VALEURS}) ===")
    for nom, d in NOS_POINTS.items():
        kts_ref = [kt(d['J'], PD_MESURE, a, Z_NOTRE_PALE) for a in AEAO_VALEURS]
        kqs_ref = [kq(d['J'], PD_MESURE, a, Z_NOTRE_PALE) for a in AEAO_VALEURS]
        etas_ref = [eta0(d['J'], k, q) for k, q in zip(kts_ref, kqs_ref)]
        kt_ref_mean = sum(kts_ref) / len(kts_ref)
        kq_ref_mean = sum(kqs_ref) / len(kqs_ref)
        eta_ref_mean = sum(etas_ref) / len(etas_ref)
        ecart_kt = (d["KT"] - kt_ref_mean) / kt_ref_mean * 100 if kt_ref_mean else float("nan")
        ecart_kq = (d["10KQ"] - 10 * kq_ref_mean) / (10 * kq_ref_mean) * 100 if kq_ref_mean else float("nan")
        ecart_eta = (d["eta0"] - eta_ref_mean) / eta_ref_mean * 100 if eta_ref_mean else float("nan")
        print(f"{nom:12s} (J={d['J']}) : K_T ref={kt_ref_mean:+.4f} (nous {d['KT']:.4f}, écart {ecart_kt:+.1f}%)  "
              f"10K_Q ref={10*kq_ref_mean:+.4f} (nous {d['10KQ']:.4f}, écart {ecart_kq:+.1f}%)  "
              f"eta0 ref={eta_ref_mean:+.4f} (nous {d['eta0']:.4f}, écart {ecart_eta:+.1f}%)")
        if abs(ecart_kq) > 50:
            print(f"   ALERTE : écart K_Q > 50% -- NE PAS CONCLURE. P/D est désormais DANS le domaine "
                  f"de la régression (corrigé le 18/09) : l'écart n'est plus un artefact d'extrapolation, "
                  f"et sa cause reste ouverte (A_E/A_0 réel inconnu, pale non-série-B, autre). Rapporter "
                  f"le chiffre, ne pas l'expliquer ici.")


if __name__ == "__main__":
    main()
