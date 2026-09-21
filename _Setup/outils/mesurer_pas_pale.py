#!/usr/bin/env python3
"""Mesure le rayon réel et le pas réduit P/D de la pale à partir de la géométrie
source, EN LECTURE SEULE -- LOT 1, consigne du 17/09 « Pale-série-B-réserve-et-
référence-externe ».

Contexte : `surfaceCheck` établit que `propellerTip` (patch qui, malgré son nom,
porte toute la surface de pale du moyeu au bout -- vérifié ici, rayon min ≈0,
rayon max ≈ D/2) est une nappe OUVERTE (50216 arêtes à une seule face, mesuré par
Cowork). L'épaisseur n'existe pas dans la source : aucune réparation possible,
seulement un remplacement (voir LOT 3, pale B4 de réserve). Ce script ne touche
à AUCUN fichier de cas -- il lit `constant/triSurface/propellerTip.obj.gz`
(identique sur les quatre cas, vérifié par taille de fichier) et n'écrit rien
dans l'arborescence du cas.

Méthode : pour chaque fraction de rayon r/R demandée, sélectionne les centroïdes
de triangle dans une bande radiale étroite (±1 % de R par défaut) autour de
r = (r/R)·R, les regroupe par pale (coupure sur un saut d'angle > 20°, pas un
nombre de pales supposé à l'avance), puis ajuste par PCA la direction moyenne de
chaque groupe déroulé en coordonnées (r·(θ-θ̄), y-ȳ) -- la pente de l'axe
principal EST tan(φ), l'angle de calage local. La dispersion de φ ENTRE pales
(pas la sensibilité à la largeur de bande, mesurée séparément) est le test de
fiabilité exigé par la consigne : > 5° = mesure non fiable, ne rien publier.

**Correction du 18/09** : la formule d'origine (2π·(r/R)·tan φ) était fausse d'un
facteur 2 -- confusion r/R (rayon réduit) et r/D dans sa dérivation. La relation
correcte : tan φ = P/(2πr), donc **P/D = π·(r/R)·tan φ** (D=2R, donc
2πr/D = 2π(r/R)R/(2R) = π(r/R)). Toutes les valeurs P/D publiées avant cette
date (2,4287 / 2,2967 / 2,2312) étaient donc le double des valeurs réelles
(1,214 / 1,148 / 1,116) -- voir `PARAMETRES_CAS.md` et JOURNAL du 18/09.

Usage :
    python3 _Setup/outils/mesurer_pas_pale.py
    python3 _Setup/outils/mesurer_pas_pale.py --obj Helice/case_kEpsilon/constant/triSurface/propellerTip.obj.gz
"""
import argparse
import gzip
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_OBJ = os.path.join(ROOT, "Helice", "case_kEpsilon", "constant", "triSurface", "propellerTip.obj.gz")

D_REFERENCE = 0.227378  # PARAMETRES_CAS.md -- D (diametre), mesure geometrique du 14/09
SEUIL_DISPERSION_DEG = 5.0
GAP_CLUSTER_DEG = 20.0
TOL_FRAC_DEFAULT = 0.01


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


def centroids_of(verts, faces):
    out = []
    for f in faces:
        pts = [verts[i - 1] for i in f]
        cx = sum(p[0] for p in pts) / 3
        cy = sum(p[1] for p in pts) / 3
        cz = sum(p[2] for p in pts) / 3
        out.append((cx, cy, cz))
    return out


def cluster_par_pale(points, gap_deg=GAP_CLUSTER_DEG):
    """points : liste de (r, theta, y). Regroupe par saut d'angle > gap_deg,
    fusionne le premier et le dernier groupe si le saut de retour (au-dessus de
    +pi vers -pi) est lui aussi petit -- sans supposer Z=4 a priori."""
    pts = sorted(points, key=lambda t: t[1])
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


def phi_par_pca(cluster):
    """Ajuste la direction moyenne d'un groupe de points (r, theta, y) deroule
    en (r*(theta-theta_moy), y-y_moy) -- l'angle de l'axe principal EST phi."""
    rs = [p[0] for p in cluster]
    ths = [p[1] for p in cluster]
    ys = [p[2] for p in cluster]
    r_mean = sum(rs) / len(rs)
    th_mean = sum(ths) / len(ths)
    y_mean = sum(ys) / len(ys)
    xs = [r_mean * (th - th_mean) for th in ths]
    ycs = [y - y_mean for y in ys]
    sxx = sum(a * a for a in xs)
    syy = sum(b * b for b in ycs)
    sxy = sum(a * b for a, b in zip(xs, ycs))
    theta_pca = 0.5 * math.atan2(2 * sxy, sxx - syy)
    return math.degrees(theta_pca)


def mesurer(centroids, frac, R, tol_frac=TOL_FRAC_DEFAULT, min_pts=8):
    target_r = frac * R
    tol = tol_frac * R
    pts = []
    for (x, y, z) in centroids:
        r = r_of(x, z)
        if abs(r - target_r) <= tol:
            pts.append((r, math.atan2(z, x), y))
    clusters = cluster_par_pale(pts)
    phis = [phi_par_pca(c) for c in clusters if len(c) >= min_pts]
    n_rejetes = len(clusters) - len(phis)
    return {
        "frac": frac, "target_r": target_r, "n_pts": len(pts),
        "n_clusters": len(phis), "n_clusters_rejetes": n_rejetes,
        "phis": phis,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--obj", default=DEFAULT_OBJ, help="chemin du propellerTip.obj(.gz) a lire")
    ap.add_argument("--tol-frac", type=float, default=TOL_FRAC_DEFAULT, help="largeur de bande radiale, fraction de R")
    args = ap.parse_args()

    if not os.path.isfile(args.obj):
        sys.exit(f"Fichier introuvable : {args.obj}")

    verts, faces = read_obj(args.obj)
    R = max(r_of(x, z) for (x, y, z) in verts)
    centroids = centroids_of(verts, faces)

    print(f"Source : {args.obj}")
    print(f"n points={len(verts)}  n triangles={len(faces)}")
    print(f"R mesure (rayon max des sommets) = {R:.6f} m")
    ecart_D = abs(R - D_REFERENCE / 2)
    print(f"D/2 (PARAMETRES_CAS.md, 14/09) = {D_REFERENCE / 2:.6f} m -- ecart = {ecart_D:.6f} m ({ecart_D / (D_REFERENCE/2)*100:.3f} %)")

    resultats = []
    for frac in (0.5, 0.7, 0.9):
        r = mesurer(centroids, frac, R, tol_frac=args.tol_frac)
        print(f"\n-- r/R = {frac} (r = {r['target_r']:.5f} m, bande +-{args.tol_frac*100:.1f}% de R, {r['n_pts']} faces) --")
        if r["n_clusters_rejetes"]:
            print(f"   {r['n_clusters_rejetes']} groupe(s) rejete(s) (< 8 points)")
        if not r["phis"]:
            print("   AUCUN groupe exploitable -- mesure IMPOSSIBLE a ce rayon.")
            resultats.append((frac, None, None, None))
            continue
        for i, phi in enumerate(r["phis"]):
            print(f"   pale {i+1}/{len(r['phis'])} : phi = {phi:+.2f} deg")
        phi_mean = sum(r["phis"]) / len(r["phis"])
        dispersion = max(r["phis"]) - min(r["phis"])
        fiable = dispersion <= SEUIL_DISPERSION_DEG
        PD = math.pi * frac * math.tan(math.radians(phi_mean))
        print(f"   phi_moyen = {phi_mean:+.2f} deg -- dispersion inter-pales = {dispersion:.2f} deg (seuil {SEUIL_DISPERSION_DEG} deg)")
        print(f"   P/D (= pi*{frac}*tan(phi), corrige le 18/09) = {abs(PD):.4f}")
        print(f"   VERDICT : {'FIABLE' if fiable else 'NON FIABLE -- NE PAS PUBLIER CETTE VALEUR'}")
        resultats.append((frac, phi_mean, dispersion, abs(PD) if fiable else None))

    print("\n=== Résumé ===")
    for frac, phi_mean, dispersion, PD in resultats:
        if PD is None:
            print(f"r/R={frac} : NON FIABLE (dispersion {dispersion if dispersion is not None else '?'} deg) -- rien a publier")
        else:
            print(f"r/R={frac} : phi={phi_mean:+.2f} deg, dispersion={dispersion:.2f} deg, P/D={PD:.4f}")


if __name__ == "__main__":
    main()
