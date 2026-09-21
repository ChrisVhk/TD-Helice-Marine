#!/usr/bin/env python3
"""Mesure la fermeture de la nappe, l'épaisseur de la pale et A_E/A_0 sur une
seule face -- LOT 1-3, consigne du 18/09 « URGENT_136-aretes ». EN LECTURE
SEULE sur `constant/triSurface/propellerTip.obj.gz` -- ne touche à aucun cas,
ne relance aucun maillage.

**Correction du 18/09** : Cowork avait mal lu la sortie de `surfaceCheck` --
« 50216 » (mesuré, confirmé ici par extraction directe ET par la formule
d'Euler pour un maillage triangulé, B = 2E - 3F) est le nombre TOTAL
d'arêtes, PAS le nombre d'arêtes libres. Le nombre réel d'arêtes à une seule
face (donc de bord de la nappe) est **136** -- la surface est fermée à
99,7 %. L'hypothèse « la pale n'a pas d'épaisseur » (03_BASE_THEORIQUE.md,
§« La pale est un baffle ») était donc probablement fausse : LOT 2 mesure
une épaisseur réelle, non nulle et décroissante du pied au bout, ce qui
l'infirme définitivement.

Méthode LOT 1 (localiser les 136 arêtes) : reconstruit la liste des arêtes du
maillage (chaque arête = paire de sommets d'un côté d'un triangle), compte
combien de triangles portent chaque arête -- une arête à un seul triangle est
une arête de bord. Regroupe ces arêtes de bord en composantes connexes
(boucles fermées) via un parcours de graphe simple.

Méthode LOT 2 (épaisseur) : à un rayon donné, isole les points d'UNE pale
(même découpage par saut d'angle que `mesurer_pas_pale.py`), ajuste par PCA
la direction de corde locale (axe majeur) et la direction d'épaisseur (axe
mineur, perpendiculaire), puis mesure l'écart entre les deux nappes (dos/face)
à une position de corde donnée -- l'écart sur l'axe mineur entre points
voisins sur l'axe majeur.

Méthode LOT 3 (A_E/A_0 sur une face) : classe chaque triangle « dos » ou
« face » par le signe de la composante de sa normale le long de la tangente
locale de rotation (perpendiculaire au rayon, dans le plan de rotation) --
les deux faces d'une pale mince ont des normales quasi opposées dans cette
direction. Une bande « ambiguë » (bords, arrondis de bout/bord de fuite) reste
non classée -- rapportée séparément, jamais forcée dans un côté ou l'autre.

Usage :
    python3 _Setup/outils/mesurer_fermeture_pale.py
"""
import argparse
import gzip
import math
import os
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_OBJ = os.path.join(ROOT, "Helice", "case_kEpsilon", "constant", "triSurface", "propellerTip.obj.gz")

D_REFERENCE = 0.227378  # PARAMETRES_CAS.md -- D, mesure geometrique du 14/09
GAP_CLUSTER_DEG = 20.0


def read_obj(path):
    opener = gzip.open if path.endswith(".gz") else open
    verts, faces = [], []
    with opener(path, "rt") as f:
        for line in f:
            if line.startswith("v "):
                _, x, y, z = line.split()[:4]
                verts.append((float(x), float(y), float(z)))
            elif line.startswith("f "):
                idx = [int(tok.split("/")[0]) for tok in line.split()[1:]]
                faces.append(idx)
    return verts, faces


def r_of(x, z):
    return math.hypot(x, z)


# --- LOT 1 : localiser les aretes de bord ---------------------------------

def aretes_de_bord(faces):
    edge_count = defaultdict(int)
    for f in faces:
        n = len(f)
        for i in range(n):
            a, b = f[i], f[(i + 1) % n]
            edge_count[(min(a, b), max(a, b))] += 1
    return [e for e, c in edge_count.items() if c == 1], len(edge_count)


def boucles(bord, verts, R):
    adj = defaultdict(set)
    for a, b in bord:
        adj[a].add(b)
        adj[b].add(a)
    visited = set()
    comps = []
    for start in adj:
        if start in visited:
            continue
        stack, comp = [start], []
        while stack:
            n = stack.pop()
            if n in visited:
                continue
            visited.add(n)
            comp.append(n)
            stack.extend(adj[n] - visited)
        comps.append(comp)
    out = []
    for comp in comps:
        pts = [verts[v - 1] for v in comp]
        rs = [r_of(p[0], p[2]) for p in pts]
        ys = [p[1] for p in pts]
        degres = {len(adj[v]) for v in comp}
        out.append({
            "n_sommets": len(comp), "degres": degres,
            "r_min": min(rs), "r_max": max(rs), "y_min": min(ys), "y_max": max(ys),
            "rR_min": min(rs) / R, "rR_max": max(rs) / R,
        })
    return out


# --- LOT 2 : epaisseur --------------------------------------------------

def _cluster_par_pale(pts, gap_deg=GAP_CLUSTER_DEG):
    pts = sorted(pts, key=lambda t: t[1])
    thetas = [p[1] for p in pts]
    clusters, cur = [], [pts[0]]
    for i in range(1, len(pts)):
        if thetas[i] - thetas[i - 1] > math.radians(gap_deg):
            clusters.append(cur)
            cur = []
        cur.append(pts[i])
    clusters.append(cur)
    if len(clusters) > 1:
        gap_wrap = (thetas[0] + 2 * math.pi) - thetas[-1]
        if gap_wrap <= math.radians(gap_deg):
            clusters[0] = clusters[-1] + clusters[0]
            clusters.pop()
    return clusters


def epaisseur_a_rayon(verts, frac, R, tol_frac=0.02):
    target = frac * R
    tol = tol_frac * R
    pts = []
    for (x, y, z) in verts:
        r = r_of(x, z)
        if abs(r - target) <= tol:
            pts.append((r, math.atan2(z, x), y))
    clusters = [c for c in _cluster_par_pale(pts) if len(c) >= 20]
    if not clusters:
        return None
    c = clusters[0]
    r_mean = sum(p[0] for p in c) / len(c)
    th_mean = sum(p[1] for p in c) / len(c)
    y_mean = sum(p[2] for p in c) / len(c)
    xs = [r_mean * (th - th_mean) for (_, th, _) in c]
    ys = [y - y_mean for (_, _, y) in c]
    sxx = sum(a * a for a in xs)
    syy = sum(b * b for b in ys)
    sxy = sum(a * b for a, b in zip(xs, ys))
    theta_pca = 0.5 * math.atan2(2 * sxy, sxx - syy)
    ct, st = math.cos(theta_pca), math.sin(theta_pca)
    proj = [(x * ct + y * st, -x * st + y * ct) for x, y in zip(xs, ys)]
    s_vals = [p[0] for p in proj]
    s_min, s_max = min(s_vals), max(s_vals)
    chord = s_max - s_min

    def thickness_at(s_target, width_frac=0.03):
        w = width_frac * chord
        ts = [t for s, t in proj if abs(s - s_target) <= w]
        return (max(ts) - min(ts), len(ts)) if len(ts) >= 2 else (None, len(ts))

    s_mid = (s_min + s_max) / 2
    th_mid, n_mid = thickness_at(s_mid)
    th_c1, n_c1 = thickness_at(s_max - 0.05 * chord)
    th_c2, n_c2 = thickness_at(s_min + 0.05 * chord)
    return {"corde_mm": chord * 1000, "ep_mi_corde_mm": th_mid * 1000 if th_mid else None,
            "n_mi_corde": n_mid, "ep_5pct_cote1_mm": th_c1 * 1000 if th_c1 else None,
            "n_5pct_cote1": n_c1, "ep_5pct_cote2_mm": th_c2 * 1000 if th_c2 else None,
            "n_5pct_cote2": n_c2}


# --- LOT 3 : A_E/A_0 sur une face ---------------------------------------

def _tri_normal_area_centroid(verts, f):
    p0, p1, p2 = [verts[i - 1] for i in f]
    v1 = tuple(p1[k] - p0[k] for k in range(3))
    v2 = tuple(p2[k] - p0[k] for k in range(3))
    cx = v1[1] * v2[2] - v1[2] * v2[1]
    cy = v1[2] * v2[0] - v1[0] * v2[2]
    cz = v1[0] * v2[1] - v1[1] * v2[0]
    area = 0.5 * math.sqrt(cx * cx + cy * cy + cz * cz)
    if area == 0:
        return 0.0, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)
    n = (cx / (2 * area), cy / (2 * area), cz / (2 * area))
    c = tuple(sum(p[k] for p in (p0, p1, p2)) / 3 for k in range(3))
    return area, n, c


def aire_e_par_face(verts, faces, D):
    dos = face = ambigu = 0.0
    for f in faces:
        area, n, c = _tri_normal_area_centroid(verts, f)
        if area == 0:
            continue
        x, y, z = c
        r = r_of(x, z)
        t = (-z / r, 0.0, x / r) if r > 1e-9 else (0.0, 0.0, 0.0)
        dp = n[0] * t[0] + n[1] * t[1] + n[2] * t[2]
        if dp > 0.05:
            dos += area
        elif dp < -0.05:
            face += area
        else:
            ambigu += area
    A0 = math.pi * D ** 2 / 4
    return {"dos_m2": dos, "face_m2": face, "ambigu_m2": ambigu,
            "AE_A0_dos": dos / A0, "AE_A0_face": face / A0,
            "AE_A0_moyenne": (dos + face) / 2 / A0}


def rapport_boucles(path, R, label):
    verts, faces = read_obj(path)
    bord, E_total = aretes_de_bord(faces)
    B_formule = 2 * E_total - 3 * len(faces)
    print(f"\n--- {label} ({path}) ---")
    print(f"V={len(verts)} F={len(faces)} E={E_total} B=2E-3F={B_formule} "
          f"(extraction directe : {len(bord)})")
    bls = boucles(bord, verts, R)
    for i, bl in enumerate(bls):
        print(f"  boucle {i+1} : {bl['n_sommets']} sommets, degres={bl['degres']}, "
              f"r/R={bl['rR_min']:.4f}-{bl['rR_max']:.4f}, y={bl['y_min']:.5f}-{bl['y_max']:.5f}")
    return verts, faces, bls


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--obj", default=DEFAULT_OBJ)
    ap.add_argument("--stems-dir", default=os.path.dirname(DEFAULT_OBJ))
    a = ap.parse_args()

    verts, faces = read_obj(a.obj)
    R = max(r_of(x, z) for (x, y, z) in verts)
    print(f"Source : {a.obj}")
    print(f"V={len(verts)}  F={len(faces)}  R={R:.5f} m")

    print("\n=== LOT 1 -- localisation des aretes de bord (constat, sans interpretation) ===")
    bord, E_total = aretes_de_bord(faces)
    B_formule = 2 * E_total - 3 * len(faces)
    print(f"E (aretes distinctes) = {E_total}  (Cowork/surfaceCheck citait ce nombre : {E_total})")
    print(f"B = 2E - 3F = {B_formule}")
    print(f"B (extraction directe, aretes a une seule face) = {len(bord)}")
    boucles_pale = boucles(bord, verts, R)
    for i, bl in enumerate(boucles_pale):
        print(f"  boucle {i+1} : {bl['n_sommets']} sommets, degres={bl['degres']}, "
              f"r/R={bl['rR_min']:.4f}-{bl['rR_max']:.4f}, y={bl['y_min']:.5f}-{bl['y_max']:.5f}")

    for stem in ("propellerStem1", "propellerStem2", "propellerStem3"):
        p = os.path.join(a.stems_dir, f"{stem}.obj.gz")
        if os.path.isfile(p):
            rapport_boucles(p, R, stem)
        else:
            print(f"\n--- {stem} : fichier introuvable ({p}) ---")

    print("\n=== LOT 2 -- epaisseur (mi-corde ET bord de fuite) ===")
    for frac in (0.3, 0.5, 0.7, 0.9):
        r = epaisseur_a_rayon(verts, frac, R)
        if r is None:
            print(f"r/R={frac} : mesure impossible")
            continue
        print(f"r/R={frac} : corde={r['corde_mm']:.2f}mm  "
              f"ep. mi-corde={r['ep_mi_corde_mm']:.3f}mm (n={r['n_mi_corde']}, t/D={r['ep_mi_corde_mm']/1000/D_REFERENCE:.5f})  "
              f"ep. pres bord1={r['ep_5pct_cote1_mm']:.3f}mm (n={r['n_5pct_cote1']})  "
              f"ep. pres bord2={r['ep_5pct_cote2_mm']:.3f}mm (n={r['n_5pct_cote2']})")

    print("\n=== (info, hors perimetre du 18/09 v2) A_E/A_0 sur une face ===")
    res = aire_e_par_face(verts, faces, D_REFERENCE)
    print(f"aire dos={res['dos_m2']:.6f} m2 (A_E/A0={res['AE_A0_dos']:.4f})  "
          f"aire face={res['face_m2']:.6f} m2 (A_E/A0={res['AE_A0_face']:.4f})  "
          f"ambigu={res['ambigu_m2']:.6f} m2  moyenne A_E/A0={res['AE_A0_moyenne']:.4f}")


if __name__ == "__main__":
    main()
