#!/usr/bin/env python3
"""Où les couches de prismes sont-elles perdues sur la pale ? -- essai
`case_kEpsilon_layers_test-tipfix` (consigne du 19/09, étape 4a).

La table de snappyHexMesh (« layers 3,51 / 6, 73 % ») est une MOYENNE SUR LES
FACES du patch : elle n'est pas comparable entre deux maillages de résolutions
différentes (raffiner le bout de pale a fait passer `propellerTip` de 18480 à
31010 faces, surtout dans la zone mal couverte -- la moyenne baisse même si la
couverture locale progresse). Cet outil la ventile par rayon et par nature de
face.

Proxy de « première couche présente » : épaisseur normale de la cellule
propriétaire de chaque face de pale, h = V_cellule / aire_face. Une première
couche vaut ~0,18 mm (firstLayerThickness), une cellule de cœur 0,78 mm (niveau
6) à 3,1 mm (niveau 4) : seuil h < 0,4 mm. C'est un PROXY (il ne compte pas les
couches suivantes) et il présume la première couche de 0,18 mm.
« Flanc » = face ayant une face de normale opposée à moins de 12 mm (les deux
côtés de la pale) ; « bord/calotte » = sans partenaire (bord d'attaque, de fuite,
bout).

Prérequis : les volumes de cellules, écrits par
    postProcess -func writeCellVolumes -constant       (dans CASE_DIR)
Sur le cas de PRODUCTION, faire cette étape sur une copie de constant/polyMesh
(le cas ne doit pas être modifié).

Usage :
    python3 _Setup/outils/mesurer_couches_pale.py CASE_DIR [CASE_DIR ...]
"""
import argparse
import os
import sys

import numpy as np
from scipy.spatial import cKDTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mesurer_vide_pale as mv  # noqa: E402

R = mv.R_DEFAUT
SEUIL_MM = 0.4


def lire_volumes(chemin):
    """Lit le champ V (volumes de cellules). PIEGE (19-20/09) : si le controlDict du cas a
    `writeFormat ascii;`, V est écrit en TEXTE ; le relire comme du binaire ne lève aucune erreur
    et rend des volumes absurdes (1e-67, 1e+179). D'où deux gardes : format déclaré, plausibilité."""
    d = open(chemin, "rb").read()
    entete = d[:d.find(b"}")].decode("latin-1")
    if "binary" not in entete:
        raise ValueError(f"{chemin} n'est pas binaire (writeFormat ascii ?) : recalculer V avec le "
                         "controlDict du cas source recopié tel quel (writeFormat binary;)")
    n, i = mv._liste(d, d.find(b"internalField"))
    V = np.frombuffer(d, dtype="<f8", count=n, offset=i)
    if not (np.all(np.isfinite(V)) and V.min() > 1e-15 and V.max() < 1e-2):
        raise ValueError(f"{chemin} : volumes implausibles (min {V.min():.3g}, max {V.max():.3g} m3)")
    return V


def preparer_volumes_copie(cas_source, dest):
    """Copie constant/polyMesh et TOUT system/ de cas_source dans dest, puis écrit V. Le cas source
    n'est jamais modifié. Copier system/ en entier (et non un controlDict minimal) : c'est ce qui
    garantit writeFormat binary et les #include résolus."""
    import shutil
    import subprocess
    os.makedirs(os.path.join(dest, "constant"), exist_ok=True)
    for sous in (("constant", "polyMesh"), ("system",)):
        d = os.path.join(dest, *sous)
        if not os.path.isdir(d):
            shutil.copytree(os.path.join(cas_source, *sous), d)
    subprocess.run(["bash", "-lc", "source /usr/lib/openfoam/openfoam2412/etc/bashrc >/dev/null 2>&1; "
                    f"cd '{dest}' && postProcess -func writeCellVolumes -constant >/dev/null"], check=True)
    return dest


def faces_avec_h(case, avec_aire=False):
    pm = os.path.join(case, "constant", "polyMesh")
    pts = mv.lire_points(os.path.join(pm, "points"))
    offs, flat = mv.lire_faces(os.path.join(pm, "faces"))
    patches = mv.lire_patches(os.path.join(pm, "boundary"))
    d = open(os.path.join(pm, "owner"), "rb").read()
    n, i = mv._liste(d, d.find(b"}"))
    owner = np.frombuffer(d, dtype="<i4", count=n, offset=i)
    V = lire_volumes(os.path.join(case, "constant", "V"))
    C, N, H, P, AIRE = [], [], [], [], []
    for nom in sorted(n for n in patches if n.startswith("propellerTip")):  # + zones Mid/End du cas gradient
        nf, sf = patches[nom]
        for f in range(sf, sf + nf):
            v = pts[flat[offs[f]:offs[f + 1]]]
            nn = np.zeros(3)
            for a, b in zip(v, np.roll(v, -1, axis=0)):
                nn += np.cross(a, b)
            A2 = np.linalg.norm(nn)
            C.append(v.mean(axis=0)); N.append(nn / A2); H.append(V[owner[f]] / (A2 / 2) * 1e3); P.append(nom)
            AIRE.append(A2 / 2)
    if avec_aire:
        return np.array(C), np.array(N), np.array(H), np.array(P), np.array(AIRE)
    return np.array(C), np.array(N), np.array(H), np.array(P)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cases", nargs="+")
    a = ap.parse_args()
    for case in a.cases:
        C, N, H, P = faces_avec_h(case)
        r = np.hypot(C[:, 0], C[:, 2]) / R
        tree = cKDTree(C)
        flanc = np.zeros(len(C), bool)
        for i in np.where(r >= 0.8)[0]:
            flanc[i] = any(j != i and N[j] @ N[i] < -0.5 for j in tree.query_ball_point(C[i], mv.RAYON_RECHERCHE))
        print(f"\n=== {case} : propellerTip* (couches voulues) {int((P != 'propellerTipEdge').sum())} faces, propellerTipEdge {int((P == 'propellerTipEdge').sum())} faces")
        print(" r/R        faces  1re couche présente (h<0.4 mm)   h médian (mm)")
        for lo, hi in [(0.0, 0.3), (0.3, 0.5), (0.5, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 0.95), (0.95, 1.01)]:
            s = (r >= lo) & (r < hi) & (P != "propellerTipEdge")
            if s.sum():
                print(f" {lo:.2f}-{hi:.2f} {s.sum():7d}      {100 * np.mean(H[s] < SEUIL_MM):5.1f} %                    {np.median(H[s]):6.2f}")
        print(" Pour r/R >= 0,8, propellerTip seul, flancs / bords :")
        for lo, hi in [(0.8, 0.9), (0.9, 0.95), (0.95, 1.01)]:
            for lab, m in (("flancs", flanc), ("bords/calotte", ~flanc)):
                s = (r >= lo) & (r < hi) & m & (P != "propellerTipEdge")
                if s.sum():
                    print(f"  {lo:.2f}-{hi:.2f} {lab:14s} {s.sum():6d} faces, 1re couche présente {100 * np.mean(H[s] < SEUIL_MM):5.1f} %")
        e = H[P == "propellerTipEdge"]
        if len(e):
            print(f" propellerTipEdge (0 couche voulue) : {len(e)} faces, h médian {np.median(e):.2f} mm, {100 * np.mean(e < SEUIL_MM):.1f} % < 0,4 mm")


if __name__ == "__main__":
    main()
