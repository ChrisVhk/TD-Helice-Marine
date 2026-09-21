#!/usr/bin/env python3
"""Géométries de pale pour les essais de maillage du 20/09 (volets B et C de la consigne).

Travaille sur `constant/triSurface/propellerTipSplit.stl` d'un cas (solids `propellerTip` et
`propellerTipEdge`, axe de rotation Y, origine (0 0 0)) et écrit un STL de même nom, prêt pour
snappyHexMesh. Deux sous-commandes :

  tronquer CASE_DIR --frac 0.97
      Coupe chaque pale par un PLAN perpendiculaire à son axe radial, à x . n_pale = frac * R
      (n_pale = direction radiale de l'apex de la pale). Plan et non cylindre : la section d'une pale
      gauchie par un cylindre est une boucle COURBE (flèche ~5,6 mm sur 70 mm de corde, plus que
      l'épaisseur de 3 mm), qu'on ne peut pas refermer proprement ; la boucle du plan est plane, la
      calotte est triangulée dans son plan (ear clipping). Près de l'apex la coupe plane et la coupe
      cylindrique diffèrent de moins de 0,1R sur la zone retirée. La calotte est ajoutée au solid
      `propellerTipEdge` (0 couche voulue, aucun nouveau patch, mêmes conditions aux limites).
      CONTRÔLE de fermeture : le nombre d'arêtes de bord doit rester celui de l'original (136, la
      couture pale/moyeu) ; sinon le script échoue plutôt que d'écrire une surface trouée.
      Écrit aussi propellerTipSplit.stl.orig (original) si absent.

  zones CASE_DIR --coupure 0.915 --coupure 0.97 --noms propellerTipMid,propellerTipEnd
      Reclasse les triangles du solid `propellerTip` (jamais ceux de `propellerTipEdge`) dont le
      rayon de centroïde dépasse chaque coupure (en fraction de R) dans de nouveaux solids, pour
      donner un nSurfaceLayers différent par zone (les couches se règlent par PATCH).

R = 0,113689 m (D = 0,227378, PARAMETRES_CAS.md).
"""
import argparse
import math
import os
import re
import shutil
from collections import defaultdict

import numpy as np

R = 0.113689
ATT_ARRONDI = 8  # décimales (10 nm) pour souder les sommets


def lire(chemin):
    txt = open(chemin, encoding="utf-8").read()
    solids = []
    for bloc in re.split(r"(?m)^solid ", txt)[1:]:
        nom = bloc.split("\n", 1)[0].strip()
        tri = []
        for m in re.finditer(r"vertex\s+(\S+)\s+(\S+)\s+(\S+)", bloc):
            tri.append([float(x) for x in m.groups()])
        v = np.array(tri).reshape(-1, 3, 3)
        solids.append((nom, v))
    return solids


def ecrire(chemin, solids):
    with open(chemin, "w", encoding="utf-8") as f:
        for nom, v in solids:
            f.write(f"solid {nom}\n")
            for t in v:
                n = np.cross(t[1] - t[0], t[2] - t[0])
                nn = np.linalg.norm(n)
                n = n / nn if nn > 0 else n
                f.write("  facet normal %.6e %.6e %.6e\n    outer loop\n" % tuple(n))
                for p in t:
                    f.write("      vertex %.9e %.9e %.9e\n" % tuple(p))
                f.write("    endloop\n  endfacet\n")
            f.write(f"endsolid {nom}\n")


def aires(v):
    return 0.5 * np.linalg.norm(np.cross(v[:, 1] - v[:, 0], v[:, 2] - v[:, 0]), axis=1)


def cle(p):
    return tuple(np.round(p, ATT_ARRONDI))


def aretes_de_bord(solids):
    cnt = defaultdict(int)
    for _, v in solids:
        for t in v:
            k = [cle(p) for p in t]
            for a, b in ((0, 1), (1, 2), (2, 0)):
                cnt[frozenset((k[a], k[b]))] += 1
    return [e for e, c in cnt.items() if c == 1]


def apex_pales(solids):
    """Un apex (sommet de rayon max) par pale : paquets d'azimut des sommets à r > 0,95 R."""
    P = np.concatenate([v.reshape(-1, 3) for _, v in solids])
    r = np.hypot(P[:, 0], P[:, 2])
    P = P[r > 0.95 * R]
    th = np.degrees(np.arctan2(P[:, 2], P[:, 0]))
    ordre = np.argsort(th)
    coupes = np.where(np.diff(th[ordre]) > 15.0)[0]
    paquets = np.split(ordre, coupes + 1)
    if len(paquets) > 1 and abs((th[ordre][0] + 360.0) - th[ordre][-1]) <= 15.0:  # paquet à cheval sur ±180°
        paquets = [np.concatenate([paquets[-1], paquets[0]])] + paquets[1:-1]
    apex = []
    for p in paquets:
        q = P[p]
        apex.append(q[np.argmax(np.hypot(q[:, 0], q[:, 2]))])
    return apex


def couper_triangle(t, d):
    """t : 3x3 sommets ; d : 3 distances signées (garder d <= 0). Retourne une liste de triangles."""
    dedans = [i for i in range(3) if d[i] <= 0]
    if len(dedans) == 3:
        return [t]
    if len(dedans) == 0:
        return []

    def inter(i, j):
        a, b = (i, j) if cle(t[i]) < cle(t[j]) else (j, i)  # ordre canonique : mêmes points des deux côtés
        s = d[a] / (d[a] - d[b])
        return t[a] + s * (t[b] - t[a])

    if len(dedans) == 1:
        i = dedans[0]
        j, k = (i + 1) % 3, (i + 2) % 3
        return [np.array([t[i], inter(i, j), inter(i, k)])]
    o = [i for i in range(3) if d[i] > 0][0]
    i, j = (o + 1) % 3, (o + 2) % 3
    pi_, pj = inter(i, o), inter(j, o)
    return [np.array([t[i], t[j], pj]), np.array([t[i], pj, pi_])]


def triangulation_plane(pts, n):
    """Ear clipping d'un polygone simple (pts ordonnés), dans le plan de normale n. Retourne des triples d'indices."""
    n = n / np.linalg.norm(n)
    u = np.cross(n, [0.0, 1.0, 0.0])
    if np.linalg.norm(u) < 1e-9:
        u = np.cross(n, [1.0, 0.0, 0.0])
    u /= np.linalg.norm(u)
    w = np.cross(n, u)
    xy = np.array([[p @ u, p @ w] for p in pts])
    aire = 0.5 * sum(xy[i, 0] * xy[(i + 1) % len(xy), 1] - xy[(i + 1) % len(xy), 0] * xy[i, 1] for i in range(len(xy)))
    idx = list(range(len(pts)))
    if aire < 0:
        idx.reverse()
    tris = []

    def dans(p, a, b, c):
        def s(p1, p2, p3):
            return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
        d1, d2, d3 = s(p, a, b), s(p, b, c), s(p, c, a)
        return not ((d1 < 0 or d2 < 0 or d3 < 0) and (d1 > 0 or d2 > 0 or d3 > 0))

    garde = 0
    while len(idx) > 3 and garde < 10000:
        garde += 1
        oreille = False
        for k in range(len(idx)):
            a, b, c = idx[k - 1], idx[k], idx[(k + 1) % len(idx)]
            cr = (xy[b, 0] - xy[a, 0]) * (xy[c, 1] - xy[a, 1]) - (xy[b, 1] - xy[a, 1]) * (xy[c, 0] - xy[a, 0])
            if cr <= 1e-18:
                continue
            if any(dans(xy[q], xy[a], xy[b], xy[c]) for q in idx if q not in (a, b, c)):
                continue
            tris.append((a, b, c))
            idx.pop(k)
            oreille = True
            break
        if not oreille:
            raise RuntimeError("ear clipping : polygone non simple ou dégénéré")
    tris.append(tuple(idx))
    return tris, (1 if aire >= 0 else -1)


def tronquer(case, frac):
    src = os.path.join(case, "constant", "triSurface", "propellerTipSplit.stl")
    orig = src + ".orig"
    if not os.path.exists(orig):
        shutil.copy2(src, orig)
    solids = lire(orig)
    nb0 = len(aretes_de_bord(solids))
    apex = apex_pales(solids)
    axes = [np.array([a[0], 0.0, a[2]]) / math.hypot(a[0], a[2]) for a in apex]
    th_b = [math.degrees(math.atan2(a[2], a[0])) for a in apex]
    rc = frac * R
    print(f"{len(apex)} pales, azimuts des apex {np.round(th_b, 1)} deg, coupe x.n = {rc:.5f} m ({frac} R)")
    aire_tot = sum(aires(v)[np.hypot(*(v.mean(axis=1)[:, [0, 2]]).T) >= 0.3 * R].sum() for _, v in solids)
    nouveaux, aire_ret = [], 0.0
    for nom, v in solids:
        garde = []
        for t in v:
            c = t.mean(axis=0)
            rr = math.hypot(c[0], c[2])
            if rr < 0.85 * R:
                garde.append(t)
                continue
            thc = math.degrees(math.atan2(c[2], c[0]))
            b = min(range(len(th_b)), key=lambda i: abs((thc - th_b[i] + 180) % 360 - 180))
            d = [float(p @ axes[b] - rc) for p in t]
            morceaux = couper_triangle(t, d)
            a0 = aires(np.array([t]))[0]
            a1 = sum(aires(np.array([m]))[0] for m in morceaux)
            aire_ret += a0 - a1 if rr >= 0.3 * R else 0.0
            garde.extend(morceaux)
        nouveaux.append([nom, np.array(garde)])
    # arêtes de bord créées par la coupe : celles dont les deux extrémités sont dans un plan de coupe
    bord = aretes_de_bord([(n, v) for n, v in nouveaux])
    sur_plan = []
    for e in bord:
        p, q = [np.array(x) for x in e]
        for i, ax in enumerate(axes):
            if abs(p @ ax - rc) < 1e-6 and abs(q @ ax - rc) < 1e-6 and math.hypot(*p[[0, 2]]) > 0.85 * R:
                sur_plan.append((i, e))
                break
    caps = []
    for i, ax in enumerate(axes):
        aretes = [e for (j, e) in sur_plan if j == i]
        if not aretes:
            print(f"  pale {i} : rien coupé (frac trop grand ?)")
            continue
        adj = defaultdict(list)
        for e in aretes:
            a, b = tuple(e)
            adj[a].append(b)
            adj[b].append(a)
        depart = next(iter(adj))
        boucle, prev, cur = [depart], None, depart
        while True:
            suiv = [x for x in adj[cur] if x != prev]
            nxt = suiv[0] if suiv else None
            if nxt is None or nxt == depart:
                break
            boucle.append(nxt)
            prev, cur = cur, nxt
        if len(boucle) != len(adj):
            raise RuntimeError(f"pale {i} : boucle de coupe non simple ({len(boucle)} sur {len(adj)} sommets)")
        pts = np.array(boucle)
        tris, sens = triangulation_plane(pts, ax)
        # orientation : normale de la calotte dirigée vers l'extérieur (+ax)
        for (a, b, c) in tris:
            tri = np.array([pts[a], pts[b], pts[c]])
            if np.cross(tri[1] - tri[0], tri[2] - tri[0]) @ ax < 0:
                tri = tri[[0, 2, 1]]
            caps.append(tri)
    for nv in nouveaux:
        if nv[0] == "propellerTipEdge":
            nv[1] = np.concatenate([nv[1], np.array(caps)]) if caps else nv[1]
    final = [(n, v) for n, v in nouveaux]
    nb1 = len(aretes_de_bord(final))
    print(f"arêtes de bord : original {nb0}, après coupe+calotte {nb1}")
    if nb1 != nb0:
        raise SystemExit(f"ÉCHEC : la surface n'est pas refermée ({nb1} arêtes de bord, {nb0} attendues)")
    ecrire(src, final)
    ap = sum(aires(v).sum() for _, v in final[:0])
    print(f"triangles : {sum(len(v) for _, v in solids)} -> {sum(len(v) for _, v in final)} (dont {len(caps)} de calotte)")
    print(f"aire de pale retirée (r >= 0,3R, les deux flancs) : {aire_ret * 1e6:.1f} mm2 sur {aire_tot * 1e6:.0f} mm2 "
          f"= {100 * aire_ret / aire_tot:.2f} %  (calotte ajoutée : {sum(aires(c[None])[0] for c in caps) * 1e6:.1f} mm2)")
    print(f"écrit : {src}")


def zones(case, coupures, noms):
    src = os.path.join(case, "constant", "triSurface", "propellerTipSplit.stl")
    orig = src + ".orig"
    if not os.path.exists(orig):
        shutil.copy2(src, orig)
    solids = lire(orig)
    seuils = sorted(c * R for c in coupures)
    assert len(noms) == len(seuils)
    sortie = []
    for nom, v in solids:
        if nom != "propellerTip":
            sortie.append((nom, v))
            continue
        rr = np.hypot(v.mean(axis=1)[:, 0], v.mean(axis=1)[:, 2])
        zone = np.searchsorted(seuils, rr, side="right")  # 0 = en dessous de la 1re coupure
        sortie.append((nom, v[zone == 0]))
        for k, n in enumerate(noms):
            sortie.append((n, v[zone == k + 1]))
    for n, v in sortie:
        print(f"  solid {n:18s} {len(v):6d} triangles, aire {aires(v).sum() * 1e6:9.1f} mm2")
    ecrire(src, sortie)
    print(f"écrit : {src}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("tronquer")
    a.add_argument("case_dir")
    a.add_argument("--frac", type=float, required=True)
    b = sp.add_parser("zones")
    b.add_argument("case_dir")
    b.add_argument("--coupure", type=float, action="append", required=True)
    b.add_argument("--noms", required=True)
    x = ap.parse_args()
    if x.cmd == "tronquer":
        tronquer(x.case_dir, x.frac)
    else:
        zones(x.case_dir, x.coupure, x.noms.split(","))


if __name__ == "__main__":
    main()
