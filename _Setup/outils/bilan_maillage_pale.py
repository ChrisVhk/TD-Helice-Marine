#!/usr/bin/env python3
"""Bilan d'un maillage de pale contre le critère de recevabilité -- boucle du 20/09, LOT 4.

Mesure, dans UNE passe et pour un cas donné (production comprise, jamais recopié d'une session
antérieure) :
  - qualité : `checkMesh -allTopology -allGeometry` (cellules, non-orthogonalité max, skewness max,
    cellules à déterminant < 0,001, cellules concaves, nombre de contrôles échoués) ;
  - couverture : part d'AIRE des faces de FLANC (r >= 0,3R) portant une PILE de couches, par bande de rayon,
    sur `propellerTip` seul et sur `propellerTip` + `propellerTipEdge`, et sur la bande 0,804R-0,925R.
    Test STRUCTUREL : la cellule propriétaire est mince (h1 = V/aire < 0,4 mm) ET la cellule derrière
    elle (au travers de la face opposée) a une épaisseur h2 entre 1,05 et 1,40 h1 (expansionRatio 1,2).
    Le proxy « h < 0,4 mm seul » de mesurer_couches_pale.py est gardé pour comparaison (colonne « h seul »)
    mais NE PEUT PAS servir de critère : découvert le 20/09 sur `propellerTipEdge`, qui n'a AUCUNE couche
    par construction (nSurfaceLayers 0), il compte 27 % (production) et 48 % (combo) de faces « couvertes »
    (cellules coupées par le snap). TÉMOINS imprimés à chaque passe : `propellerStem*` (couches toutes
    obtenues d'après la table de snappyHexMesh : doit valoir ~100 %) et `propellerTipEdge` quand il est
    sans couche (doit valoir ~0 %) ;
  - la table de couches de snappyHexMesh (obtenues / demandées), si le log `log.snappyHexMesh*` existe.

Le cas source n'est JAMAIS modifié : constant/polyMesh et system/ sont copiés dans `--travail`, où
checkMesh et writeCellVolumes écrivent.

Usage :
    python3 _Setup/outils/bilan_maillage_pale.py CASE_DIR [--travail DIR] [--sans-checkmesh]
"""
import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from scipy.spatial import cKDTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mesurer_couches_pale as mc  # noqa: E402
import mesurer_vide_pale as mv  # noqa: E402

BANDES = [(0.3, 0.5), (0.5, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 0.95), (0.95, 1.01)]
BANDE_EDGE = (0.804, 0.925)
BASH = "source /usr/lib/openfoam/openfoam2412/etc/bashrc >/dev/null 2>&1; "


def checkmesh(dest):
    log = os.path.join(dest, "log.checkMesh.bilan")
    subprocess.run(["bash", "-lc", BASH + f"cd '{dest}' && checkMesh -allTopology -allGeometry > log.checkMesh.bilan 2>&1"])
    t = open(log, encoding="utf-8", errors="replace").read()

    def prem(motif, cast=float):
        m = re.search(motif, t)
        return cast(m.group(1)) if m else None
    return {
        "cellules": prem(r"\n\s+cells:\s+(\d+)", int),
        "non_ortho_max": prem(r"non-orthogonality Max:\s+([\d.]+)"),
        "skewness_max": prem(r"Max skewness = ([\d.]+)"),
        "aspect_max": prem(r"Max aspect ratio = ([\d.]+)"),
        "det_faible": prem(r"small determinant \(< 0\.001\) found, number of cells:\s+(\d+)", int) or 0,
        "concaves": prem(r"Concave cells \(using face planes\) found, number of cells:\s+(\d+)", int) or 0,
        "controles_echoues": prem(r"Failed (\d+) mesh checks", int) or 0,
        "log": log,
    }


def _geom_face(pts, offs, flat, f):
    v = pts[flat[offs[f]:offs[f + 1]]]
    nn = np.zeros(3)
    for a, b in zip(v, np.roll(v, -1, axis=0)):
        nn += np.cross(a, b)
    A2 = np.linalg.norm(nn)
    return nn / A2, A2 / 2


def pile_de_couches(dest, patches_voulus):
    """Pour chaque face des patches demandés : (patch, h1, h2, pile ?, rayon, aire). Voir l'en-tête."""
    pm = os.path.join(dest, "constant", "polyMesh")
    pts = mv.lire_points(os.path.join(pm, "points"))
    offs, flat = mv.lire_faces(os.path.join(pm, "faces"))
    patches = mv.lire_patches(os.path.join(pm, "boundary"))
    d = open(os.path.join(pm, "owner"), "rb").read()
    n, i = mv._liste(d, d.find(b"}"))
    owner = np.frombuffer(d, dtype="<i4", count=n, offset=i)
    d = open(os.path.join(pm, "neighbour"), "rb").read()
    n, i = mv._liste(d, d.find(b"}"))
    neigh = np.frombuffer(d, dtype="<i4", count=n, offset=i)
    V = mc.lire_volumes(os.path.join(dest, "constant", "V"))
    ord_o = np.argsort(owner, kind="stable")
    ord_n = np.argsort(neigh, kind="stable")
    so, sn = owner[ord_o], neigh[ord_n]
    sortie = []
    for nom in patches_voulus:
        if nom not in patches:
            continue
        nf, sf = patches[nom]
        for f in range(sf, sf + nf):
            c = owner[f]
            nf_, A1 = _geom_face(pts, offs, flat, f)
            h1 = V[c] / A1
            fo = ord_o[np.searchsorted(so, c, "left"):np.searchsorted(so, c, "right")]
            fn = ord_n[np.searchsorted(sn, c, "left"):np.searchsorted(sn, c, "right")]
            best, bd = None, -0.7
            for g, sgn in [(g, 1.0) for g in fo if g != f and g < len(neigh)] + [(g, -1.0) for g in fn]:
                ng, Ag = _geom_face(pts, offs, flat, g)
                if (sgn * ng) @ nf_ < bd:
                    bd, best = (sgn * ng) @ nf_, (g, Ag)
            h2 = None
            pile = False
            if best is not None:
                g, Ag = best
                c2 = neigh[g] if owner[g] == c else owner[g]
                h2 = V[c2] / Ag
                pile = bool(h1 * 1e3 < mc.SEUIL_MM and 1.05 * h1 <= h2 <= 1.4 * h1)  # SEUIL_MM en mm, h1 en m (bug corrigé le 20/09 : comparé sans l'unité, le seuil ne filtrait rien)
            cen = pts[flat[offs[f]:offs[f + 1]]].mean(axis=0)
            sortie.append((nom, h1 * 1e3, None if h2 is None else h2 * 1e3, pile, np.hypot(cen[0], cen[2]) / mc.R, A1))
    return sortie


def couverture(dest):
    C, N, H, P, A = mc.faces_avec_h(dest, avec_aire=True)
    noms = sorted(set(P))  # même ordre que faces_avec_h : patches triés, faces croissantes
    pile = np.array([x[3] for x in pile_de_couches(dest, noms)])
    assert len(pile) == len(C), "ordre des faces incohérent entre les deux lectures"
    r = np.hypot(C[:, 0], C[:, 2]) / mc.R
    tree = cKDTree(C)
    flanc = np.zeros(len(C), bool)
    for i in np.where(r >= 0.3)[0]:
        flanc[i] = any(j != i and N[j] @ N[i] < -0.5 for j in tree.query_ball_point(C[i], mv.RAYON_RECHERCHE))
    hseul = H < mc.SEUIL_MM

    def part(masque, test):
        a = A[masque].sum()
        return (100 * A[masque & test].sum() / a, int(masque.sum()), a * 1e6) if a > 0 else (float("nan"), 0, 0.0)

    hors_edge = P != "propellerTipEdge"
    res = {"bandes": [], "edge_faces": int((P == "propellerTipEdge").sum())}
    for lo, hi in BANDES:
        s = flanc & (r >= lo) & (r < hi)
        res["bandes"].append(((lo, hi), part(s & hors_edge, pile), part(s, pile), part(s, hseul)))
    s = flanc & (r >= BANDE_EDGE[0]) & (r < BANDE_EDGE[1])
    res["bande_edge"] = part(s, pile)
    res["bande_edge_hseul"] = part(s, hseul)
    res["global_tip"] = part(flanc & hors_edge, pile)
    res["global_tip_edge"] = part(flanc, pile)
    res["global_tip_edge_hseul"] = part(flanc, hseul)
    # témoins : toutes les faces du patch (pas seulement les flancs)
    tous = np.ones(len(C), bool)
    res["temoin_edge"] = part(P == "propellerTipEdge", pile) if res["edge_faces"] else None
    res["temoin_edge_hseul"] = part(P == "propellerTipEdge", hseul) if res["edge_faces"] else None
    res["temoin_stem"] = None
    st = [x for x in pile_de_couches(dest, ["propellerStem1", "propellerStem2", "propellerStem3"])]
    if st:
        aa = np.array([x[5] for x in st]); pp = np.array([x[3] for x in st])
        res["temoin_stem"] = (100 * aa[pp].sum() / aa.sum(), len(st), aa.sum() * 1e6)
    return res


def table_snappy(case):
    for nom in sorted(glob.glob(os.path.join(case, "log.snappyHexMesh*")), key=os.path.getmtime, reverse=True):
        t = open(nom, encoding="utf-8", errors="replace").read()
        i = t.rfind("patch")
        lignes = re.findall(r"^(propeller\w+)\s+(\d+)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+(\d+)?", t[i:] if i >= 0 else t, re.M)
        if lignes:
            return nom, lignes[-6:]
    return None, []


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("case")
    ap.add_argument("--travail", help="dossier de travail (défaut : temporaire, supprimé)")
    ap.add_argument("--sans-checkmesh", action="store_true")
    a = ap.parse_args()
    case = os.path.abspath(a.case)
    travail = a.travail or tempfile.mkdtemp(prefix="bilan_maillage_")
    print(f"=== {os.path.basename(case)}  (travail : {travail})")
    mc.preparer_volumes_copie(case, travail)
    if not a.sans_checkmesh:
        q = checkmesh(travail)
        print("Qualité (checkMesh -allTopology -allGeometry) : " + " ; ".join(
            f"{k} {v}" for k, v in q.items() if k != "log"))
    c = couverture(travail)
    print("Couverture par PILE de couches (critère), part d'AIRE des flancs (r >= 0,3R), % [faces ; mm²] ; « h seul » = ancien proxy :")
    print(" r/R        Tip seul (pile)          Tip + Edge (pile)        Tip + Edge (h seul)")
    for (lo, hi), (p1, n1, a1), (p2, n2, a2), (p3, n3, a3) in c["bandes"]:
        print(f" {lo:.2f}-{hi:.2f}  {p1:6.1f} % [{n1:5d} ; {a1:6.0f}]  {p2:6.1f} % [{n2:5d} ; {a2:6.0f}]  {p3:6.1f} %")
    for lib, cle in (("GLOBAL Tip seul", "global_tip"), ("GLOBAL Tip + Edge", "global_tip_edge"),
                     (f"Bande {BANDE_EDGE[0]}R-{BANDE_EDGE[1]}R, Edge compris", "bande_edge")):
        p, n, ar = c[cle]
        print(f" {lib:44s} {p:6.1f} % [{n} faces ; {ar:.0f} mm²]")
    print(f" (h seul) GLOBAL Tip + Edge {c['global_tip_edge_hseul'][0]:.1f} % ; bande Edge {c['bande_edge_hseul'][0]:.1f} %")
    ts = c["temoin_stem"]
    print(" TÉMOIN positif propellerStem1-3 (attendu ~100 %, table snappy) : " + (f"{ts[0]:.1f} % [{ts[1]} faces]" if ts else "absent"))
    te, teh = c["temoin_edge"], c["temoin_edge_hseul"]
    print(" TÉMOIN négatif propellerTipEdge (toutes faces ; attendu ~0 % s'il est sans couche) : "
          + (f"pile {te[0]:.1f} % ; h seul {teh[0]:.1f} % [{te[1]} faces]" if te else "sans objet"))
    print("LIMITE du test de pile (à lire avec chaque pourcentage ci-dessus) : validé sur DEUX témoins seulement (propellerStem : 100 %, propellerTipEdge sans couche : 0 %) ; "
          "ratio h2/h1 dans [1,05 ; 1,4] calé sur le Stem (expansion 1,2) ; h = V/aire suppose des cellules prismatiques ; sous-estime là où une seule couche existe.")
    nom, lignes = table_snappy(case)
    if lignes:
        print(f"Table snappyHexMesh ({os.path.basename(nom)}) : patch, faces, demandées, obtenues (moy.), épaisseur, couverture %")
        for l in lignes:
            print("  ", " ".join(x for x in l if x))
    if not a.travail:
        shutil.rmtree(travail, ignore_errors=True)


if __name__ == "__main__":
    main()
