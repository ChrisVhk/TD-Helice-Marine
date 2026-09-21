#!/usr/bin/env python3
"""Avance IMPOSÉE J = V_inlet / (n D) et rendement η₀ qui en découle -- correction du 20/09 (soir).

**Pourquoi ce module existe.** Le *function object* `propellerInfo` calcule le J qu'il affiche avec
`URef`, la vitesse MOYENNE relevée par `sampleDisk` dans le plan y = -0,1 m, à 0,17 D EN AVAL du bord
aval des pales : c'est-à-dire DANS la zone d'induction de l'hélice, pas en amont. Ce n'est pas une vitesse
d'avance. Le J affiché (0,8936) était donc plus grand que l'avance réellement imposée (0,8743), et
η₀ = J K_T / (2 π K_Q), qui en dépend linéairement, surestimé de 1,9 à 2,2 % selon le cas.
K_T = T / (rho n^2 D^4) et K_Q = Q / (rho n^2 D^5) ne font intervenir que n et D : ils ne changent pas.

**Source de la valeur.** V_inlet = |composante de `value` du patch `inlet`| dans `<cas>/0.orig/U`
(condition `fixedValue`, `uniform (0 -5 0)`), lue dans le fichier, jamais recopiée ici. n = colonne `n` du
solveur (25,15 tr/s, `system/propellerInfo`), la même valeur que celle qui a servi à K_T et K_Q ; D = diamètre
corrigé de `docs/PARAMETRES_CAS.md`.

Usage en bibliothèque : `from avance_imposee import vitesse_inlet, j_impose, eta0`.
"""
import math
import re
from pathlib import Path

_INLET_RE = re.compile(r"inlet\s*\{[^}]*?value\s+uniform\s*\(\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s*\)", re.S)


def vitesse_inlet(case_dir: Path) -> float:
    """Norme de la vitesse imposée sur le patch `inlet` (m/s), lue dans `0.orig/U` (sinon `0/U`)."""
    for sous in ("0.orig", "0"):
        f = Path(case_dir) / sous / "U"
        if f.is_file():
            m = _INLET_RE.search(f.read_text(errors="ignore"))
            if m:
                return math.sqrt(sum(float(x) ** 2 for x in m.groups()))
    raise SystemExit(f"{case_dir} : patch `inlet` fixedValue uniforme introuvable dans 0.orig/U ni 0/U.")


def j_impose(v_inlet: float, n: float, d: float) -> float:
    """J = V_inlet / (n D)."""
    return v_inlet / (n * d)


def eta0(j: float, kt: float, kq10: float) -> float:
    """η₀ = J K_T / (2 π K_Q), avec `kq10` = 10 K_Q (colonne du solveur)."""
    return j * kt / (2 * math.pi * kq10 / 10.0)
