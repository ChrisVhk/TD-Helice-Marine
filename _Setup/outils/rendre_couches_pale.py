#!/usr/bin/env pvbatch
"""Coupe des couches de prismes sur la PALE, perpendiculaire à la paroi -- variante
de l'image 06 (`rendre_vues_helice.py`), consigne du 19/09.

L'image 06 zoome sur `propellerStem2` (moyeu, mi-envergure) PARCE QUE les couches
y fonctionnent : elle ne peut donc jamais montrer le problème. Ici la coupe est
ancrée sur la pale à un rayon r/R donné : plan de normale RADIALE passant par le
centre des faces de pale à ce rayon (coupe de profil : lentille de ~3 mm entourée
de ses couches), caméra en projection parallèle, même grossissement pour tous les
maillages -- la position de coupe est calculée UNE fois (maillage de référence,
`--ref`) et réutilisée telle quelle, pour un avant/après direct.

ATTENTION : la bande r/R ≈ 0,80 à 0,925 est `propellerTipEdge`, SANS couches par
décision (nSurfaceLayers 0, 13/09) : une coupe à 0,90R n'y montrera pas de couches
et ce n'est pas un échec. Les couches se regardent à r/R >= 0,95 (`propellerTip`).

Sortie : Helice/Images/_brouillon/ (gitignoré : figures de diagnostic non validées).
Ne recalcule rien, ne modifie aucun cas (lecture seule ; un .foam vide est créé
si absent, gitignoré).

Usage :
    pvbatch _Setup/outils/rendre_couches_pale.py --ref Helice/case_kEpsilon_layers \
        --cas Helice/case_kEpsilon_layers --cas Helice/case_kEpsilon_layers_test-nSL3 --r 0.96
"""
import argparse
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mesurer_vide_pale as mv  # noqa: E402  (lecture polyMesh en numpy)
from paraview.simple import *  # noqa: F401,F403,E402

R = mv.R_DEFAUT
FENETRE_MM = 5.0  # demi-hauteur visible


def centre_de_coupe(ref_case, frac):
    """Centre des faces de pale (patches propellerTip + Edge) à r/R = frac, pour UNE pale
    (celle dont l'azimut est le plus proche de +x), et normale radiale."""
    C, N = mv.faces_de_patch(ref_case)
    r = np.hypot(C[:, 0], C[:, 2]) / R
    sel = np.where(np.abs(r - frac) < 0.01)[0]
    th = np.degrees(np.arctan2(C[sel, 2], C[sel, 0]))
    # une pale = un paquet d'azimuts ; on prend le paquet autour du minimum |theta| trié
    ordre = np.argsort(th)
    th_s = th[ordre]
    coupures = np.where(np.diff(th_s) > 15.0)[0]
    paquets = np.split(ordre, coupures + 1)
    p = min(paquets, key=lambda idx: abs(np.median(th[idx])))
    pts = C[sel][p]
    c = pts.mean(axis=0)
    ur = np.array([c[0], 0.0, c[2]]); ur /= np.linalg.norm(ur)
    return c, ur, len(p)


def rendre(case, centre, ur, frac, out, label):
    name = os.path.basename(os.path.normpath(case))
    foam = os.path.join(case, f"{name}.foam")
    if not os.path.isfile(foam):
        open(foam, "w").close()
    mesh = OpenFOAMReader(FileName=foam)
    mesh.MeshRegions = ["internalMesh"]
    mesh.UpdatePipeline(time=0.0)
    wall = OpenFOAMReader(FileName=foam)
    wall.MeshRegions = ["patch/propellerTip", "patch/propellerTipEdge"]
    wall.UpdatePipeline(time=0.0)

    def coupe(src):
        s = Slice(Input=src)
        s.SliceType = "Plane"
        s.SliceType.Origin = list(centre)
        s.SliceType.Normal = list(ur)
        s.UpdatePipeline(time=0.0)
        return s

    demi = 0.008
    boite = (centre[0] - demi, centre[0] + demi, centre[1] - demi, centre[1] + demi,
             centre[2] - demi, centre[2] + demi)

    def clip(src):
        c = Clip(Input=src)
        c.ClipType = "Box"
        c.ClipType.Position = [boite[0], boite[2], boite[4]]
        c.ClipType.Length = [boite[1] - boite[0], boite[3] - boite[2], boite[5] - boite[4]]
        c.Invert = 1
        c.UpdatePipeline(time=0.0)
        return c

    view = CreateView("RenderView")
    view.ViewSize = [1400, 1000]
    view.Background = [1.0, 1.0, 1.0]
    view.UseColorPaletteForBackground = 0
    view.OrientationAxesVisibility = 0
    m = Show(clip(coupe(mesh)), view)
    m.Representation = "Surface With Edges"
    m.ColorArrayName = [None, ""]
    m.DiffuseColor = [0.80, 0.90, 0.95]
    m.AmbientColor = [0.80, 0.90, 0.95]
    m.EdgeColor = [0.10, 0.25, 0.45]
    m.LineWidth = 1.0
    w = Show(clip(coupe(wall)), view)
    w.Representation = "Surface"
    w.ColorArrayName = [None, ""]
    w.DiffuseColor = [0.85, 0.10, 0.10]
    w.AmbientColor = [0.85, 0.10, 0.10]
    w.LineWidth = 4.0
    w.RenderLinesAsTubes = 1
    # Premier rendu AVANT de fixer la camera : Render() reinitialise sinon la camera
    # (piege deja documente dans rendre_vues_helice.clip_box, constate ici : fenetre x4).
    Render(view)
    view.CameraFocalPoint = list(centre)
    view.CameraPosition = [centre[i] + ur[i] * 0.2 for i in range(3)]
    view.CameraViewUp = [0.0, 1.0, 0.0]
    view.CameraParallelProjection = 1
    view.CameraParallelScale = FENETRE_MM * 1e-3
    t = Text()
    r_reel = math.hypot(centre[0], centre[2]) / R  # le centre est une MOYENNE de faces : r reel != r demande
    t.Text = (f"{label} -- coupe de pale a r/R={r_reel:.2f} (demande {frac:.2f}, plan normal radial) -- paroi en rouge -- "
              f"fenetre {2 * FENETRE_MM * 1.4:.0f} x {2 * FENETRE_MM:.0f} mm -- diagnostic, non valide")
    d = Show(t, view)
    d.WindowLocation = "Upper Center"
    d.FontSize = 11
    d.Color = [0.05, 0.05, 0.05]
    Render(view)
    SaveScreenshot(out, view, ImageResolution=[1400, 1000])
    print(f"  ecrit : {out}")
    for o in list(GetSources().values()):
        Delete(o)
    Delete(view)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ref", required=True, help="cas de référence pour la position de coupe")
    ap.add_argument("--cas", action="append", required=True)
    ap.add_argument("--r", type=float, action="append", required=True)
    ap.add_argument("--out", default="Helice/Images/_brouillon")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for frac in a.r:
        c, ur, n = centre_de_coupe(a.ref, frac)
        print(f"r/R={frac}: centre {np.round(c, 5)} normale {np.round(ur, 3)} ({n} faces de la pale de reference)")
        for case in a.cas:
            nom = os.path.basename(os.path.normpath(case)).replace("case_kEpsilon_layers", "layers")
            out = os.path.join(a.out, f"couches-pale_r{int(round(frac * 100)):03d}_{nom}.png")
            rendre(case, c, ur, frac, out, os.path.basename(os.path.normpath(case)))


if __name__ == "__main__":
    main()
