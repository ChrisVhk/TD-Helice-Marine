#!/usr/bin/env python3
"""Reproduit la fraction d'aire de y+ dans [30;300] sur un patch -- LOT 1, consigne
du 18/09 "Cloture-et-passation". Le chiffre 83,7 % (propellerTip, case_kEpsilon,
14/09, PARAMETRES_CAS.md:36) était sourcé comme "ParaView CellSize + tri par aire
cumulée" sans commande rejouable -- ce script REFAIT le calcul directement sur les
fichiers du cas (aucun calcul CFD relancé, lecture seule sur un champ déjà écrit par
`postProcess -func yPlus` le 14/09), pour qu'il soit vérifiable sans ParaView.

Lit `constant/polyMesh/{points,faces,boundary}` (binaire OpenFOAM, faceCompactList)
pour l'aire réelle de chaque face du patch, et `<time>/<champ>` pour sa valeur par
face -- fraction pondérée par l'aire = somme des aires où la valeur est dans la
plage, divisée par l'aire totale du patch.

Usage :
    python3 _Setup/outils/verifier_yplus_pondere_aire.py \\
        --cas Helice/case_kEpsilon --time 0.06 --patch propellerTip \\
        --champ yPlus --min 30 --max 300
"""
import argparse
import re

import numpy as np


def _lire_liste_binaire(chemin, dtype, itemsize):
    with open(chemin, "rb") as f:
        data = f.read()
    m = re.search(rb"\n(\d+)\s*\n\(", data)
    n = int(m.group(1))
    start = m.end()
    return np.frombuffer(data[start:start + n * itemsize], dtype=dtype)


def _lire_points(cas):
    pts = _lire_liste_binaire(f"{cas}/constant/polyMesh/points", "<f8", 24)
    return pts.reshape(-1, 3)


def _lire_faces(cas):
    with open(f"{cas}/constant/polyMesh/faces", "rb") as f:
        data = f.read()
    blocs = list(re.finditer(rb"(\d+)\s*\n\(", data))
    m1 = blocs[0]
    n1 = int(m1.group(1))
    start1 = m1.end()
    offsets = np.frombuffer(data[start1:start1 + n1 * 4], dtype="<i4")
    after1 = start1 + n1 * 4
    m2 = next(m for m in blocs[1:] if m.start() >= after1)
    n2 = int(m2.group(1))
    start2 = m2.end()
    indices = np.frombuffer(data[start2:start2 + n2 * 4], dtype="<i4")
    return offsets, indices


def _lire_patch_range(cas, patch):
    with open(f"{cas}/constant/polyMesh/boundary") as f:
        txt = f.read()
    m = re.search(rf"{patch}\s*\{{[^}}]*nFaces\s+(\d+);[^}}]*startFace\s+(\d+);", txt)
    if not m:
        raise SystemExit(f"Patch {patch} introuvable dans constant/polyMesh/boundary")
    return int(m.group(2)), int(m.group(1))  # startFace, nFaces


def _aire_polygone(pts_face):
    n = len(pts_face)
    normal = np.zeros(3)
    for i in range(n):
        normal += np.cross(pts_face[i], pts_face[(i + 1) % n])
    return 0.5 * np.linalg.norm(normal)


def _lire_champ_patch(cas, temps, champ, patch):
    chemin = f"{cas}/{temps}/{champ}"
    with open(chemin, "rb") as f:
        data = f.read()
    idx = data.index(patch.encode())
    sous = data[idx:idx + 4000]
    m = re.search(rb"nonuniform List<scalar>\s*\n(\d+)\s*\n\(", sous)
    if not m:
        raise SystemExit(f"Patch {patch} : pas de valeur nonuniform dans {chemin} "
                          f"(uniform, ou champ vide -- postProcess a-t-il vraiment tourné ?)")
    n = int(m.group(1))
    start = idx + m.end()
    return np.frombuffer(data[start:start + n * 8], dtype="<f8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cas", required=True)
    ap.add_argument("--time", required=True)
    ap.add_argument("--patch", required=True)
    ap.add_argument("--champ", default="yPlus")
    ap.add_argument("--min", type=float, default=30)
    ap.add_argument("--max", type=float, default=300)
    a = ap.parse_args()

    start_face, n_faces = _lire_patch_range(a.cas, a.patch)
    pts = _lire_points(a.cas)
    offsets, indices = _lire_faces(a.cas)

    aires = np.zeros(n_faces)
    for i in range(n_faces):
        fidx = start_face + i
        s, e = offsets[fidx], offsets[fidx + 1]
        aires[i] = _aire_polygone(pts[indices[s:e]])

    valeurs = _lire_champ_patch(a.cas, a.time, a.champ, a.patch)
    if len(valeurs) != n_faces:
        raise SystemExit(f"Désaccord de taille : {n_faces} faces sur le patch, "
                          f"{len(valeurs)} valeurs dans le champ -- pas le même maillage ?")

    aire_totale = aires.sum()
    masque = (valeurs >= a.min) & (valeurs <= a.max)
    aire_dans = aires[masque].sum()
    fraction = 100 * aire_dans / aire_totale

    ordre = np.argsort(valeurs)
    cum = np.cumsum(aires[ordre])
    med = valeurs[ordre][np.searchsorted(cum, aire_totale / 2)]

    print(f"Patch {a.patch} ({n_faces} faces, aire totale {aire_totale*1e4:.2f} cm²), "
          f"champ {a.champ} à t={a.time} :")
    print(f"  min={valeurs.min():.4f}  max={valeurs.max():.4f}  "
          f"médiane pondérée par l'aire={med:.2f}")
    print(f"  fraction de l'AIRE dans [{a.min:g};{a.max:g}] : {fraction:.4f} %  "
          f"(fraction du NOMBRE de faces, pour contexte : {100*masque.sum()/n_faces:.4f} %)")


if __name__ == "__main__":
    main()
