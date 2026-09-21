#!/usr/bin/env python3
"""La pale est-elle maillée comme un VRAI VOLUME ou comme un baffle ? -- essai
`case_kEpsilon_layers_test-tipfix` (consigne du 19/09, étape 4b).

Refait la question de l'analyse indépendante du 15/09 (écart angulaire entre
centres de cellules fluides, script disparu du dépôt) par une mesure plus
directe et INDÉPENDANTE de la taille de maille, donc comparable entre maillages
de résolutions différentes :

  Sur les faces des patches `propellerTip` et `propellerTipEdge` (normales
  sortantes du domaine fluide, donc dirigées DANS la pale), on cherche pour
  chaque face la face voisine de normale opposée la plus proche (dans un rayon
  de 12 mm), et on mesure le DÉCALAGE NORMAL s = (c_g - c_f) . n_f.
    - baffle : les deux jeux de faces sont coïncidents -> s ~ 0
    - vrai volume : les deux faces sont séparées par la pale -> s ~ épaisseur
      locale (3 à 10 mm selon le rayon, mesurée par mesurer_fermeture_pale.py).
  Résultat par bande de rayon r/R. Les faces sans partenaire (bord d'attaque,
  bord de fuite, calotte de bout) sont comptées à part, pas forcées.

Lecture seule : ne modifie aucun cas. Lit constant/polyMesh (points, faces
binaires `faceCompactList`, boundary ASCII).

Usage :
    python3 _Setup/outils/mesurer_vide_pale.py CASE_DIR [CASE_DIR ...] [--R 0.113689]
"""
import argparse
import os
import re
import sys

import numpy as np
from scipy.spatial import cKDTree

R_DEFAUT = 0.113689  # D = 0,227378 m, PARAMETRES_CAS.md
BANDES = [(0.30, 0.50), (0.50, 0.70), (0.70, 0.80), (0.80, 0.90), (0.90, 0.95), (0.95, 1.01)]
PATCHES = ("propellerTip", "propellerTipEdge")
RAYON_RECHERCHE = 0.012  # m


def _liste(data, debut):
    m = re.compile(rb"\n(\d+)\n\(").search(data, debut)
    return int(m.group(1)), m.end()


def lire_points(chemin):
    d = open(chemin, "rb").read()
    n, i = _liste(d, d.find(b"}"))
    return np.frombuffer(d, dtype="<f8", count=3 * n, offset=i).reshape(n, 3)


def lire_faces(chemin):
    d = open(chemin, "rb").read()
    n1, i1 = _liste(d, d.find(b"}"))
    offs = np.frombuffer(d, dtype="<i4", count=n1, offset=i1)
    n2, i2 = _liste(d, i1 + 4 * n1)
    flat = np.frombuffer(d, dtype="<i4", count=n2, offset=i2)
    return offs, flat


def lire_patches(chemin):
    t = open(chemin, encoding="utf-8", errors="replace").read()
    out = {}
    for m in re.finditer(r"(\w+)\s*\{[^}]*?nFaces\s+(\d+);[^}]*?startFace\s+(\d+);", t):
        out[m.group(1)] = (int(m.group(2)), int(m.group(3)))
    return out


def faces_de_patch(case_dir, noms=None):
    """noms=None : tous les patches propellerTip* du cas (propellerTip, propellerTipEdge, et les zones
    propellerTipMid/End du cas gradient s'il y en a)."""
    pm = os.path.join(case_dir, "constant", "polyMesh")
    pts = lire_points(os.path.join(pm, "points"))
    offs, flat = lire_faces(os.path.join(pm, "faces"))
    patches = lire_patches(os.path.join(pm, "boundary"))
    if noms is None:
        noms = sorted(n for n in patches if n.startswith("propellerTip"))
    C, N = [], []
    for nom in noms:
        if nom not in patches:
            continue
        nf, sf = patches[nom]
        for f in range(sf, sf + nf):
            v = pts[flat[offs[f]:offs[f + 1]]]
            c = v.mean(axis=0)
            # Newell : normale sortante (convention OpenFOAM des faces de bord)
            nn = np.zeros(3)
            for a, b in zip(v, np.roll(v, -1, axis=0)):
                nn += np.cross(a, b)
            nrm = np.linalg.norm(nn)
            C.append(c)
            N.append(nn / nrm if nrm > 0 else nn)
    return np.array(C), np.array(N)


def analyser(case_dir, R):
    C, N = faces_de_patch(case_dir)
    r = np.hypot(C[:, 0], C[:, 2]) / R
    tree = cKDTree(C)
    partenaire = np.full(len(C), -1)
    for i in range(len(C)):
        if not (0.30 <= r[i] < 1.01):
            continue
        idx = tree.query_ball_point(C[i], RAYON_RECHERCHE)
        idx = [j for j in idx if j != i and N[j] @ N[i] < -0.5]
        if idx:
            j = min(idx, key=lambda k: np.linalg.norm(C[k] - C[i]))
            partenaire[i] = j
    lignes = []
    for lo, hi in BANDES:
        sel = np.where((r >= lo) & (r < hi))[0]
        avec = [i for i in sel if partenaire[i] >= 0]
        if avec:
            s = np.array([(C[partenaire[i]] - C[i]) @ N[i] for i in avec])
            d = np.array([np.linalg.norm(C[partenaire[i]] - C[i]) for i in avec])
            lignes.append((lo, hi, len(sel), len(avec) / len(sel), np.median(s) * 1e3,
                           np.percentile(s, 10) * 1e3, np.percentile(s, 90) * 1e3, np.median(d) * 1e3))
        else:
            lignes.append((lo, hi, len(sel), 0.0, float("nan"), float("nan"), float("nan"), float("nan")))
    return len(C), lignes


def epaisseurs_reference():
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, here)
        import mesurer_fermeture_pale as m
        verts, _ = m.read_obj(m.DEFAULT_OBJ)
        return {f: m.epaisseur_a_rayon(verts, f, 0.11372)["ep_mi_corde_mm"] for f in (0.3, 0.5, 0.7, 0.8, 0.9, 0.95)}
    except Exception:
        return {}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cases", nargs="+")
    ap.add_argument("--R", type=float, default=R_DEFAUT)
    a = ap.parse_args()
    ref = epaisseurs_reference()
    print("Épaisseur mi-corde mesurée sur la géométrie source (mm) :",
          {k: round(v, 2) for k, v in ref.items()} or "(non disponible)")
    for cd in a.cases:
        n, lignes = analyser(cd, a.R)
        print(f"\n=== {cd}  ({n} faces sur {'+'.join(PATCHES)})")
        print(" r/R          faces  avec partenaire   décalage normal s (mm) : médiane [p10 ; p90]   dist. médiane (mm)")
        for lo, hi, nf, fr, med, p10, p90, dm in lignes:
            print(f" {lo:.2f}-{hi:.2f}  {nf:7d}   {100*fr:5.1f} %          {med:7.2f}  [{p10:6.2f} ; {p90:6.2f}]            {dm:6.2f}")


if __name__ == "__main__":
    main()
