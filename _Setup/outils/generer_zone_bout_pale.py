#!/usr/bin/env python3
"""Géométrie de raffinement « bout de pale » pour snappyHexMesh -- essai
`case_kEpsilon_layers_test-tipfix` (consigne du 19/09, « maillage seul »).

Extrait de `constant/triSurface/propellerTipSplit.stl` (les deux solids
`propellerTip` et `propellerTipEdge`) les triangles dont le centroïde est à un
rayon r >= FRAC * R de l'axe (axe Y, origine (0 0 0), cf. dynamicMeshDict :
r = hypot(x, z)), et les écrit en UN seul solid `propellerTipOuter`.

Pourquoi une géométrie dédiée et pas `propellerTipEdge` : `refinementRegions`
de snappyHexMesh est indexé par GÉOMÉTRIE, pas par région, et la bande
`propellerTipEdge` ne couvre que r = 0,0914 à 0,1052 m (0,80R à 0,925R) : le
vrai bout de pale (0,925R à R, R = 0,11372 m), où la pale est la plus mince,
est resté dans `propellerTip`. Cette géométrie n'est utilisée QUE dans
`refinementRegions` (mode distance) : elle ne figure ni dans
`refinementSurfaces` ni dans `layers`, donc ne crée aucun patch.

Usage :
    python3 _Setup/outils/generer_zone_bout_pale.py CASE_DIR [--frac 0.8] [--R 0.113689]
Écrit CASE_DIR/constant/triSurface/propellerTipOuter.stl (gitignoré : régénérable
depuis le STL source par cette commande).
"""
import argparse
import math
import os
import re

R_DEFAUT = 0.113689  # D = 0,227378 m, PARAMETRES_CAS.md


def lire_triangles(chemin):
    txt = open(chemin, encoding="utf-8").read()
    tris = []
    for bloc in re.split(r"(?m)^solid ", txt)[1:]:
        for m in re.finditer(
            r"facet normal\s+(\S+)\s+(\S+)\s+(\S+)\s+outer loop\s+"
            r"vertex\s+(\S+)\s+(\S+)\s+(\S+)\s+vertex\s+(\S+)\s+(\S+)\s+(\S+)\s+"
            r"vertex\s+(\S+)\s+(\S+)\s+(\S+)", bloc):
            v = [float(x) for x in m.groups()]
            tris.append((v[0:3], [v[3:6], v[6:9], v[9:12]]))
    return tris


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("case_dir")
    ap.add_argument("--frac", type=float, default=0.8, help="fraction de R (défaut 0,8)")
    ap.add_argument("--R", type=float, default=R_DEFAUT)
    a = ap.parse_args()
    src = os.path.join(a.case_dir, "constant", "triSurface", "propellerTipSplit.stl")
    dst = os.path.join(a.case_dir, "constant", "triSurface", "propellerTipOuter.stl")
    seuil = a.frac * a.R
    tris = lire_triangles(src)
    gardes = []
    for n, vs in tris:
        cx = sum(v[0] for v in vs) / 3.0
        cz = sum(v[2] for v in vs) / 3.0
        if math.hypot(cx, cz) >= seuil:
            gardes.append((n, vs))
    with open(dst, "w", encoding="utf-8") as f:
        f.write("solid propellerTipOuter\n")
        for n, vs in gardes:
            f.write("  facet normal %.6e %.6e %.6e\n    outer loop\n" % tuple(n))
            for v in vs:
                f.write("      vertex %.6e %.6e %.6e\n" % tuple(v))
            f.write("    endloop\n  endfacet\n")
        f.write("endsolid propellerTipOuter\n")
    print(f"{len(tris)} triangles lus, {len(gardes)} gardés (r_centroïde >= {seuil:.5f} m = {a.frac} R) -> {dst}")


if __name__ == "__main__":
    main()
