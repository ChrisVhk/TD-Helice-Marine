#!/usr/bin/env pvbatch
# -*- coding: utf-8 -*-
"""Galerie d'images d'introduction (TD Helice), rendues hors ecran par pvbatch.

Usage :
    pvbatch _Setup/outils/rendre_vues_helice.py [--cas case_kEpsilon] [--time 0.06]
                                                 [--out-dir Helice/Images/galerie]
                                                 [--only 1,2,3,4,5,6]

A executer depuis la racine du depot (TD-Helice-Marine/), les .foam et les
chemins de cas etant relatifs a Helice/.

API PINNEE : ParaView 5.11.2 (paraview.simple), verifie sur ce poste le 13/09.
PIEGE D'API CONNU SUR 5.11 : appeler ColorBy(rep, None) leve
`RuntimeError: invalid association string 'NONE'`. Pour une surface unie, ne
PAS appeler ColorBy : fixer directement rep.ColorArrayName = [None, ''] puis
une couleur via rep.DiffuseColor -- c'est le contournement utilise ici.

Ne recalcule rien : lit uniquement les champs/maillages deja sur disque.
"""
import argparse
import math
import os
import re
import sys

from paraview.simple import *  # noqa: F401,F403 -- API ParaView standard

ROTATION_AXIS = (0.0, 1.0, 0.0)  # cellZone innerCylinderSmall, omega = 158 rad/s -- jamais supposer z
VIEW_SIZE = (1600, 1200)


# --------------------------------------------------------------------------- #
# Utilitaires communs
# --------------------------------------------------------------------------- #

def foam_file(case_dir):
    name = os.path.basename(os.path.normpath(case_dir))
    path = os.path.join(case_dir, f"{name}.foam")
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"fichier .foam manquant : {path} -- LOT A aurait du le creer (touch)"
        )
    return path


def make_reader(case_dir, regions, cell_arrays, time):
    """Lit un cas OpenFOAM existant. N'appelle jamais rien qui recalcule."""
    reader = OpenFOAMReader(FileName=foam_file(case_dir))
    reader.MeshRegions = regions
    if cell_arrays:
        reader.CellArrays = cell_arrays
    reader.UpdatePipeline(time=time)
    return reader


def solid_color(rep, rgb):
    """Surface unie sans coloration par champ.

    NE PAS faire ColorBy(rep, None) (RuntimeError sur ParaView 5.11 : association
    'NONE' invalide). Le contournement verifie : fixer l'association a une
    chaine vide directement sur la representation.
    """
    rep.ColorArrayName = [None, ""]
    rep.DiffuseColor = list(rgb)
    rep.AmbientColor = list(rgb)


def new_view(size=VIEW_SIZE):
    view = CreateView("RenderView")
    view.ViewSize = list(size)
    view.Background = [1.0, 1.0, 1.0]
    view.UseColorPaletteForBackground = 0
    view.OrientationAxesVisibility = 0
    return view


def frame_camera(view, bounds, direction, up, zoom=1.8):
    """Camera EXPLICITE calculee depuis les bornes reelles de la geometrie.

    Jamais un simple ResetCamera() : position, point focal et vertical sont
    tous les trois fixes numeriquement, pour rester reproductibles d'une
    version de ParaView (ou d'un cas V2) a l'autre.
    """
    xmin, xmax, ymin, ymax, zmin, zmax = bounds
    cx, cy, cz = (xmin + xmax) / 2.0, (ymin + ymax) / 2.0, (zmin + zmax) / 2.0
    diag = math.sqrt((xmax - xmin) ** 2 + (ymax - ymin) ** 2 + (zmax - zmin) ** 2)
    diag = max(diag, 1e-6)
    dx, dy, dz = direction
    n = math.sqrt(dx * dx + dy * dy + dz * dz) or 1.0
    dx, dy, dz = dx / n, dy / n, dz / n
    dist = diag * zoom
    view.CameraFocalPoint = [cx, cy, cz]
    view.CameraPosition = [cx + dx * dist, cy + dy * dist, cz + dz * dist]
    view.CameraViewUp = list(up)
    view.CameraParallelProjection = 0
    return (cx, cy, cz), dist


def add_provenance(view, text, location="Lower Center", size=10):
    """Ligne de provenance incrustee : cas . modele . instant . etat de validation.

    Regle non negociable de la consigne du 13/09 : aucune image n'est livree
    sans elle.
    """
    t = Text()
    t.Text = text
    d = Show(t, view)
    d.WindowLocation = location
    d.FontSize = size
    d.Color = [0.05, 0.05, 0.05]
    d.Bold = 0
    return t, d


def save(view_or_layout, path, size=VIEW_SIZE):
    SaveScreenshot(path, view_or_layout, ImageResolution=list(size))
    print(f"  ecrit : {path}")


_REAL_SAVE = save  # snapshot pris avant toute pollution possible -- voir _restore_builtins()


def _restore_builtins():
    """BUG VTK/ParaView confirme le 14/09 : importer
    vtk.numpy_interface.dataset_adapter (directement, ou via un
    ProgrammableFilter dont le script partage nos globals -- pvbatch execute
    ce fichier comme __main__) REMPLACE min/max/sum/abs des BUILTINS du
    process entier, ET ECRASE aussi nos PROPRES noms de fonctions qui
    collisionnent avec des symboles numpy (notre `save` <-> `numpy.save`).
    TypeError totalement sans rapport apparent avec l'appel qui echoue.
    A appeler apres CHAQUE usage de dataset_adapter/sm.Fetch, ou juste avant
    tout min()/max()/save() qui suit un tel usage dans la meme fonction.
    """
    import builtins as _b
    g = globals()
    g["min"], g["max"], g["sum"], g["abs"] = _b.min, _b.max, _b.sum, _b.abs
    g["save"] = _REAL_SAVE


def interpolate_to_points(source):
    """CellDataToPoint : donnees OpenFOAM natives en CELL DATA -> POINT DATA.

    Sans ca, ColorBy(('CELLS', champ)) peint chaque maille d'une seule teinte
    plate : rendu en blocs rectangulaires, jamais lisse (constate le 14/09 sur
    05/07/08). Colorer ensuite par ('POINTS', champ), jamais par CELLS.
    """
    interp = CellDatatoPointData(Input=source)
    interp.UpdatePipeline()
    return interp


def style_scalarbar(sb, title, location="Lower Right Corner", length=0.35, font=12):
    """Barre DANS le cadre (emplacements ancres ParaView, jamais rognes),
    graduee, avec titre/unite lisibles sur fond blanc."""
    sb.Title = title
    sb.ComponentTitle = ""
    sb.WindowLocation = location
    sb.ScalarBarLength = length
    sb.TitleFontSize = font
    sb.LabelFontSize = max(font - 2, 9)
    sb.AutomaticLabelFormat = 0
    sb.RangeLabelFormat = "%-#5.2g"
    sb.TitleColor = [0.0, 0.0, 0.0]
    sb.LabelColor = [0.0, 0.0, 0.0]
    sb.DrawBackground = 1
    sb.BackgroundColor = [1.0, 1.0, 1.0, 0.75]


def solid_body(source, view, color=(0.55, 0.55, 0.58), edge=(0.15, 0.15, 0.15)):
    """Corps solide grise avec contour sombre -- JAMAIS blanc sur fond blanc
    (defaut constate le 14/09 : un solide non colore se lit comme un trou).
    """
    rep = Show(source, view)
    rep.Representation = "Surface With Edges"
    solid_color(rep, color)
    rep.EdgeColor = list(edge)
    rep.LineWidth = 0.6
    return rep


def clip_box(source, bounds):
    """Decoupe la geometrie AFFICHEE a l'echelle du cadrage voulu.

    Necessaire des qu'on zoome fort : verifie le 13/09 sur l'image des couches
    -- si la donnee montree deborde largement le cadrage camera, Render()
    detecte un ratio near/far degenere et REINITIALISE la camera de lui-meme,
    silencieusement. Le Clip evite le probleme a la racine.
    """
    xmin, xmax, ymin, ymax, zmin, zmax = bounds
    clip = Clip(Input=source)
    clip.ClipType = "Box"
    clip.ClipType.Position = [xmin, ymin, zmin]
    clip.ClipType.Length = [xmax - xmin, ymax - ymin, zmax - zmin]
    clip.Invert = 1
    clip.UpdatePipeline()
    return clip


def add_flow_arrow(view, bounds, color=(0.05, 0.05, 0.55), subject_bounds=None):
    """Repere d'ecoulement : segment + cone, le long de l'axe reel de
    l'ecoulement (-Y, inlet -> outlet). Objet 3D (pas une simple etiquette) :
    il projette correctement quel que soit l'angle de camera choisi.

    Dimensionne et centre sur `subject_bounds` (l'objet d'interet, par
    defaut `bounds`) selon X/Z, PAS sur l'etendue Y complete du cadrage :
    celle-ci porte souvent une marge de sillage tres allongee (voir
    propeller_zoom_bounds) qui detacherait sinon la fleche de l'objet.
    """
    sb = subject_bounds if subject_bounds is not None else bounds
    xmin, xmax, _, _, zmin, zmax = sb
    _, _, ymin, ymax, _, _ = bounds
    cx = (xmin + xmax) / 2.0
    cy = (ymin + ymax) / 2.0
    span = max(xmax - xmin, zmax - zmin, 1e-6)
    z0 = zmax + span * 0.35
    length = span * 0.7
    y_top = cy + length / 2.0
    p1 = [cx, y_top, z0]
    p2 = [cx, y_top - length, z0]
    shaft = Line(Point1=p1, Point2=p2)
    srep = Show(shaft, view)
    srep.LineWidth = 5
    srep.AmbientColor = list(color)
    srep.DiffuseColor = list(color)
    cone = Cone(Center=[p2[0], p2[1] - length * 0.05, p2[2]], Direction=[0.0, -1.0, 0.0],
                Radius=length * 0.12, Height=length * 0.28, Resolution=14)
    crep = Show(cone, view)
    solid_color(crep, color)
    label = Text()
    label.Text = "ecoulement"
    d = Show(label, view)
    d.WindowLocation = "Upper Center"
    d.FontSize = 10
    d.Color = list(color)
    return shaft, cone


def add_scale_bar(view, bounds, length_m, color=(0.05, 0.05, 0.05)):
    """Barre d'echelle graphique (segment 3D dans le plan de coupe) + son
    libelle en mm. Placee pres du coin bas-gauche des donnees affichees.
    """
    xmin, xmax, ymin, ymax, zmin, zmax = bounds
    x0 = xmin + (xmax - xmin) * 0.06
    y0 = ymin + (ymax - ymin) * 0.08
    z0 = zmin + (zmax - zmin) * 0.5
    p1 = [x0, y0, z0]
    p2 = [x0 + length_m, y0, z0]
    line = Line(Point1=p1, Point2=p2)
    rep = Show(line, view)
    rep.LineWidth = 4
    rep.AmbientColor = list(color)
    rep.DiffuseColor = list(color)
    label = Text()
    label.Text = f"echelle : {length_m * 1000:.0f} mm"
    d = Show(label, view)
    d.WindowLocation = "Lower Left Corner"
    d.FontSize = 10
    d.Color = list(color)
    return line


def percentile_range(source, array_name, association="CELLS", lo=5, hi=95):
    """Plage [percentile lo, percentile hi] d'un champ, PAS le min/max brut.

    Sur ces calculs non valides (Porte B non franchie), quelques cellules
    extremes (bout de pale, cf. l'historique de divergence du 13/09) suffisent
    a etaler l'echelle de couleur sur tout un ordre de grandeur -- le reste de
    la surface s'affiche alors uniformement blanc. Verifie sur `p` le 13/09 :
    min/max = [-105,3 ; 97,7] contre p5/p95 = [-25,6 ; 11,3]. Retombe sur
    RescaleTransferFunctionToDataRange (min/max) si numpy/vtk ne cooperent pas.
    """
    try:
        from paraview import servermanager as sm
        from vtk.numpy_interface import dataset_adapter as dsa
        import numpy as np

        data = sm.Fetch(source)
        wrapped = dsa.WrapDataObject(data)
        cd = wrapped.CellData if association == "CELLS" else wrapped.PointData
        arr = cd[array_name]
        pieces = [np.asarray(a) for a in getattr(arr, "Arrays", [arr]) if a is not None]
        if not pieces:
            return None
        values = np.concatenate(pieces)
        if values.ndim > 1:  # champ vectoriel (U) -> norme
            values = np.linalg.norm(values, axis=1)
        return float(np.percentile(values, lo)), float(np.percentile(values, hi))
    except Exception as exc:  # defensif : jamais bloquant pour une image
        print(f"  percentile_range({array_name}) a echoue ({exc}) -- repli min/max")
        return None
    finally:
        _restore_builtins()


MODELE_NOM = {
    "kEpsilon": "k-epsilon",
    "kEpsilon_layers": "k-epsilon (maillage a couches)",
    "kOmegaSST": "k-omega SST",
    "laminar": "laminaire",
}


def provenance_line(case, time, etat):
    suffixe = case.split("case_")[-1] if case.startswith("case_") else case
    modele = MODELE_NOM.get(suffixe, suffixe)
    return f"{case} · {modele} · t = {time:g} s · {etat}"


ETAT_DEMO = "calcul de demonstration, non valide (Porte B non franchie)"
ETAT_MAILLAGE = "maillage seul, aucun champ associe"


# --------------------------------------------------------------------------- #
# Image 1 -- geometrie de l'helice seule
# --------------------------------------------------------------------------- #

def image_01(args):
    case_dir = f"Helice/{args.cas}"
    reader = make_reader(
        case_dir,
        ["patch/propellerTip", "patch/propellerStem1", "patch/propellerStem2", "patch/propellerStem3"],
        [],
        args.time,
    )
    view = new_view()
    rep = Show(reader, view)
    rep.Representation = "Surface With Edges"
    solid_color(rep, (0.55, 0.58, 0.62))
    rep.EdgeColor = [0.12, 0.12, 0.14]
    rep.LineWidth = 0.4
    bounds = reader.GetDataInformation().GetBounds()
    # Vue quasi axiale (le long de l'axe Y) legerement inclinee : c'est ce qui
    # permet de compter les 4 pales autour du moyeu -- une vraie vue "trois
    # quarts" (perpendiculaire a l'axe) les mettrait en majorite de profil.
    frame_camera(view, bounds, direction=(0.32, 0.82, 0.42), up=(0.0, 0.0, 1.0), zoom=2.3)
    # D mesure sur cette geometrie (LOT 1, 14/09) = 0,227378 m, PAS 0,2 m code en
    # dur -- arbitrage enseignant rendu le 14/09 : system/propellerInfo corrige
    # (radius 0.113689) dans les quatre cas, J/K_T/10K_Q reechelonnes.
    add_scale_bar(view, bounds, 0.05)
    add_provenance(view, provenance_line(args.cas, args.time, ETAT_DEMO)
                   + " -- D mesure 0,227378 m (corrige le 14/09, etait 0,2 m)")
    Render(view)
    save(view, os.path.join(args.out_dir, "01_geometrie.png"))


# --------------------------------------------------------------------------- #
# Image 2 -- geometrie + domaine de calcul
# --------------------------------------------------------------------------- #

def image_02(args):
    case_dir = f"Helice/{args.cas}"
    prop = make_reader(
        case_dir,
        ["patch/propellerTip", "patch/propellerStem1", "patch/propellerStem2", "patch/propellerStem3"],
        [],
        args.time,
    )
    outer = make_reader(case_dir, ["patch/outerCylinder"], [], args.time)
    inlet = make_reader(case_dir, ["patch/inlet"], [], args.time)
    outlet = make_reader(case_dir, ["patch/outlet"], [], args.time)

    view = new_view()
    rep_prop = Show(prop, view)
    rep_prop.Representation = "Surface With Edges"
    solid_color(rep_prop, (0.55, 0.58, 0.62))
    rep_prop.EdgeColor = [0.12, 0.12, 0.14]
    rep_prop.LineWidth = 0.4

    rep_outer = Show(outer, view)
    rep_outer.Representation = "Surface"
    solid_color(rep_outer, (0.35, 0.55, 0.85))
    rep_outer.Opacity = 0.12

    # inlet/outlet "marques" : couleurs franches et opaques, pas noyes dans la
    # transparence du cylindre lateral.
    rep_inlet = Show(inlet, view)
    rep_inlet.Representation = "Surface"
    solid_color(rep_inlet, (0.2, 0.7, 0.3))  # vert
    rep_inlet.Opacity = 0.35

    rep_outlet = Show(outlet, view)
    rep_outlet.Representation = "Surface"
    solid_color(rep_outlet, (0.9, 0.55, 0.1))  # orange
    rep_outlet.Opacity = 0.35

    bounds = outer.GetDataInformation().GetBounds()
    # Ligne d'arbre A L'HORIZONTALE (up = Z, pas Y) : Y est l'axe du maillage
    # (arbitraire, ce domaine n'a pas de surface libre ni de "haut" physique),
    # mais une vue "helice debout comme un verre" n'est pas comment un marin
    # dessine une ligne d'arbre. Vue de cote, viser perpendiculairement a Y.
    frame_camera(view, bounds, direction=(0.9, 0.2, 0.35), up=(0.0, 0.0, 1.0), zoom=1.7)
    add_provenance(view, provenance_line(args.cas, args.time, ETAT_DEMO)
                   + " -- domaine : outerCylinder + inlet/outlet")
    Render(view)
    save(view, os.path.join(args.out_dir, "02_geometrie_domaine.png"))


# --------------------------------------------------------------------------- #
# Image 3 -- coupe du maillage volumique
# --------------------------------------------------------------------------- #

def propeller_zoom_bounds(prop_bounds, wake_margin=2.2, radial_margin=1.8):
    """Cadrage resserre sur l'helice + sillage proche (defaut constate le
    14/09 : l'helice n'occupait que ~5% de l'image sur les bornes du domaine
    complet). radial_margin/wake_margin sont des facteurs sur le rayon max ;
    l'ecoulement va de l'inlet (+Y) vers l'outlet (-Y) -- le sillage proche
    est donc du cote -Y (Ymin), pas +Y.
    """
    xmin, xmax, ymin, ymax, zmin, zmax = prop_bounds
    r = max(xmax - xmin, zmax - zmin) / 2.0
    cx, cz = (xmin + xmax) / 2.0, (zmin + zmax) / 2.0
    return (
        cx - r * radial_margin, cx + r * radial_margin,
        ymin - r * wake_margin, ymax + r * wake_margin * 0.4,
        cz - r * radial_margin, cz + r * radial_margin,
    )


def image_03(args):
    case_dir = f"Helice/{args.cas}"
    reader = make_reader(case_dir, ["internalMesh"], [], args.time)
    prop = make_reader(
        case_dir,
        ["patch/propellerTip", "patch/propellerStem1", "patch/propellerStem2", "patch/propellerStem3"],
        [], args.time,
    )
    prop_bounds = prop.GetDataInformation().GetBounds()
    zoom_bounds = propeller_zoom_bounds(prop_bounds)

    sl_full = Slice(Input=reader)
    sl_full.SliceType = "Plane"
    sl_full.SliceType.Origin = [0.0, 0.0, 0.0]
    sl_full.SliceType.Normal = [0.0, 0.0, 1.0]
    sl_full.UpdatePipeline(time=args.time)
    # Cadrage resserre (defaut 3.3) : decouper la coupe elle-meme, pas
    # seulement zoomer la camera (sinon Render() la reinitialise -- meme piege
    # que sur l'image des couches, cf. clip_box()).
    sl = clip_box(sl_full, zoom_bounds)

    view = new_view()
    rep = Show(sl, view)
    rep.Representation = "Surface With Edges"
    solid_color(rep, (0.85, 0.85, 0.85))
    rep.EdgeColor = [0.1, 0.1, 0.1]
    rep.LineWidth = 0.5

    # Corps solide (pale + moyeu) DANS la meme vue (defaut 3.4) : sans lui, le
    # volume qu'occupe l'helice dans la coupe fluide est un simple trou blanc
    # sur fond blanc -- il doit se lire comme un objet.
    solid_body(prop, view, color=(0.5, 0.5, 0.55))

    # up = X (pas Y) : la coupe reste la meme (normale z, inchangee), seule
    # l'orientation a l'ecran tourne de 90 degres pour que l'axe de l'arbre
    # (Y) se lise a l'horizontale, comme une ligne d'arbre vue de cote.
    frame_camera(view, zoom_bounds, direction=(0.0, 0.05, 1.0), up=(1.0, 0.0, 0.0), zoom=1.5)
    add_flow_arrow(view, zoom_bounds, subject_bounds=prop_bounds)
    add_scale_bar(view, zoom_bounds, 0.02)
    add_provenance(view, provenance_line(args.cas, args.time, ETAT_DEMO)
                   + " -- coupe maillage (zoom pres helice), plan (0,0,0)/normale z")
    Render(view)
    save(view, os.path.join(args.out_dir, "03_maillage_coupe.png"))


# --------------------------------------------------------------------------- #
# Image 4 -- interface AMI (maillage glissant)
# --------------------------------------------------------------------------- #

def image_04(args):
    case_dir = f"Helice/{args.cas}"
    prop = make_reader(
        case_dir,
        ["patch/propellerTip", "patch/propellerStem1", "patch/propellerStem2", "patch/propellerStem3"],
        [],
        args.time,
    )
    ami1_raw = make_reader(case_dir, ["patch/AMI1"], [], args.time)
    ami2 = make_reader(case_dir, ["patch/AMI2"], [], args.time)
    dom = make_reader(case_dir, ["patch/outerCylinder"], [], args.time)

    # AMI1/AMI2 sont deux surfaces cylindriques QUASI COINCIDENTES (rayon
    # 0,11985 vs 0,11999 m -- rotor et stator de la meme interface) : rendues
    # opaques a l'identique, elles font du z-fighting et cachent l'helice.
    # Ecart radial exagere ICI, pour la lisibilite de l'image seulement (ne
    # touche aucun maillage ni calcul) : AMI1 reduite de 15% en X/Z autour de
    # l'axe, pour se voir comme un cylindre distinct emboite dans AMI2.
    ami1 = Transform(Input=ami1_raw)
    ami1.Transform = "Transform"
    ami1.Transform.Scale = [0.85, 1.0, 0.85]
    ami1.UpdatePipeline(time=args.time)

    view = new_view()

    rep_dom = Show(dom, view)
    rep_dom.Representation = "Surface"
    solid_color(rep_dom, (0.7, 0.7, 0.75))
    rep_dom.Opacity = 0.08

    rep_prop = Show(prop, view)
    rep_prop.Representation = "Surface With Edges"
    solid_color(rep_prop, (0.5, 0.5, 0.5))
    rep_prop.EdgeColor = [0.12, 0.12, 0.14]
    rep_prop.LineWidth = 0.4

    rep_ami1 = Show(ami1, view)
    rep_ami1.Representation = "Surface"
    solid_color(rep_ami1, (0.85, 0.15, 0.1))  # rouge, rotor (AMI1, reduite)
    rep_ami1.Opacity = 0.6

    rep_ami2 = Show(ami2, view)
    rep_ami2.Representation = "Surface"
    solid_color(rep_ami2, (0.1, 0.35, 0.85))  # bleu, stator (AMI2)
    rep_ami2.Opacity = 0.45

    bounds = dom.GetDataInformation().GetBounds()
    # Meme convention que l'image 2 : ligne d'arbre a l'horizontale (up = Z).
    frame_camera(view, bounds, direction=(0.9, 0.2, 0.35), up=(0.0, 0.0, 1.0), zoom=1.6)
    add_provenance(view, provenance_line(args.cas, args.time, ETAT_DEMO)
                   + " -- AMI1 (rouge) / AMI2 (bleu), interface de maillage glissant")
    Render(view)
    save(view, os.path.join(args.out_dir, "04_interface_AMI.png"))


# --------------------------------------------------------------------------- #
# Image 5 -- pression sur les pales, deux vues (echelle commune)
# --------------------------------------------------------------------------- #

TWO_MEANS_SCRIPT = """
import numpy as np
from vtk.numpy_interface import dataset_adapter as dsa

inp = inputs[0]
normals = np.asarray(inp.CellData['Normals'])
c0 = normals[np.argmax(normals[:, 1])]
c1 = normals[np.argmin(normals[:, 1])]
centers = np.array([c0, c1], dtype=float)
for _ in range(30):
    d0 = np.linalg.norm(normals - centers[0], axis=1)
    d1 = np.linalg.norm(normals - centers[1], axis=1)
    assign = (d1 < d0).astype(np.int32)
    n0 = normals[assign == 0].mean(axis=0) if (assign == 0).any() else centers[0]
    n1 = normals[assign == 1].mean(axis=0) if (assign == 1).any() else centers[1]
    n0 = n0 / np.linalg.norm(n0)
    n1 = n1 / np.linalg.norm(n1)
    if np.allclose(n0, centers[0]) and np.allclose(n1, centers[1]):
        centers = np.array([n0, n1])
        break
    centers = np.array([n0, n1])

output.ShallowCopy(inp.VTKObject)
arr = dsa.numpyTovtkDataArray(assign.astype(np.int32), name='cluster')
output.GetCellData().AddArray(arr)
"""


def split_by_normal(source, time):
    """Separe une surface en DEUX groupes de mailles par 2-means sur
    l'orientation de leurs normales (methode du 13/09, PAS un point de vue :
    verifie le 14/09 que deux cameras antipodales melangent les deux signes
    sur une pale vrillee). Retourne le filtre annote (champ CELLS 'cluster'
    0/1) -- Threshold dessus pour extraire chaque face."""
    merged = MergeBlocks(Input=source)
    merged.UpdatePipeline(time=time)
    surf = ExtractSurface(Input=merged)
    surf.UpdatePipeline(time=time)
    normals = GenerateSurfaceNormals(Input=surf)
    normals.ComputeCellNormals = 1
    normals.UpdatePipeline(time=time)
    pf = ProgrammableFilter(Input=normals)
    pf.Script = TWO_MEANS_SCRIPT
    pf.UpdatePipeline(time=time)
    _restore_builtins()  # voir la fonction -- ProgrammableFilter + dsa pollue nos globals
    return pf


def safe_up(direction):
    """Axe global le MOINS aligne avec `direction`, pour eviter une camera
    degeneree (up parallele a la direction de vue)."""
    ax, ay, az = abs(direction[0]), abs(direction[1]), abs(direction[2])
    if ax <= ay and ax <= az:
        return (1.0, 0.0, 0.0)
    if ay <= ax and ay <= az:
        return (0.0, 1.0, 0.0)
    return (0.0, 0.0, 1.0)


def image_05(args):
    case_dir = f"Helice/{args.cas}"
    tip = make_reader(case_dir, ["patch/propellerTip"], ["p"], args.time)
    stem = make_reader(
        case_dir, ["patch/propellerStem1", "patch/propellerStem2", "patch/propellerStem3"], [], args.time
    )
    bounds = make_reader(
        case_dir,
        ["patch/propellerTip", "patch/propellerStem1", "patch/propellerStem2", "patch/propellerStem3"],
        [], args.time,
    ).GetDataInformation().GetBounds()

    # 3.8 -- separation par ORIENTATION DE LA NORMALE (2-means), pas par
    # point de vue : la version au 13/09 (deux cameras antipodales) melangeait
    # les deux signes de pression dans chaque vue, verifie a l'oeil.
    clustered = split_by_normal(tip, args.time)

    from paraview import servermanager as sm
    from vtk.numpy_interface import dataset_adapter as dsa
    import numpy as np

    fetched = dsa.WrapDataObject(sm.Fetch(clustered))
    normals_np = np.asarray(fetched.CellData["Normals"])
    cluster_np = np.asarray(fetched.CellData["cluster"])
    p_np = np.asarray(fetched.CellData["p"])
    mean0 = normals_np[cluster_np == 0].mean(axis=0)
    mean1 = normals_np[cluster_np == 1].mean(axis=0)
    mean0 = mean0 / np.linalg.norm(mean0)
    mean1 = mean1 / np.linalg.norm(mean1)
    dot = float(mean0[0] * mean1[0] + mean0[1] * mean1[1] + mean0[2] * mean1[2])
    # NE PAS utiliser min()/max() ici : "from paraview.simple import *" plus
    # haut masque les builtins par les reductions numpy de vtk (verifie le
    # 14/09 -- TypeError sournoise, aucun rapport avec la logique).
    if dot > 1.0:
        dot = 1.0
    elif dot < -1.0:
        dot = -1.0
    angle_deg = math.degrees(math.acos(dot))
    mean0 = mean0.tolist()
    mean1 = mean1.tolist()
    p_mean0 = float(p_np[cluster_np == 0].mean())
    p_mean1 = float(p_np[cluster_np == 1].mean())
    _restore_builtins()  # dsa importe juste au-dessus -- voir la fonction
    # Etiquetage PRUDENT : la face de pression moyenne la plus HAUTE est
    # probablement l'intrados (cote pression) d'un rotor qui pousse -- indice
    # de coherence physique, pas une demonstration aerodynamique rigoureuse.
    if p_mean0 >= p_mean1:
        label0, label1 = "haute pression (probable intrados)", "basse pression (probable extrados)"
    else:
        label0, label1 = "basse pression (probable extrados)", "haute pression (probable intrados)"

    face_a = Threshold(Input=clustered)
    face_a.Scalars = ["CELLS", "cluster"]
    face_a.LowerThreshold = 0
    face_a.UpperThreshold = 0
    face_a.ThresholdMethod = "Between"
    face_a.UpdatePipeline(time=args.time)
    face_b = Threshold(Input=clustered)
    face_b.Scalars = ["CELLS", "cluster"]
    face_b.LowerThreshold = 1
    face_b.UpperThreshold = 1
    face_b.ThresholdMethod = "Between"
    face_b.UpdatePipeline(time=args.time)

    # 3.1 -- interpolation CELLS -> POINTS pour un rendu lisse.
    interp_a = interpolate_to_points(face_a)
    interp_b = interpolate_to_points(face_b)

    # Layout a deux cellules (technique verifiee 5.11.2/pvbatch).
    layout = CreateLayout("pression_pales")
    view_a = CreateView("RenderView")
    view_a.ViewSize = list(VIEW_SIZE)
    view_a.Background = [1.0, 1.0, 1.0]
    view_a.UseColorPaletteForBackground = 0
    view_a.OrientationAxesVisibility = 0
    layout.AssignView(0, view_a)
    split_return = layout.SplitViewHorizontal(view_a, 0.5)
    view_b = CreateView("RenderView")
    view_b.ViewSize = list(VIEW_SIZE)
    view_b.Background = [1.0, 1.0, 1.0]
    view_b.UseColorPaletteForBackground = 0
    view_b.OrientationAxesVisibility = 0
    for candidate in (split_return + 1, split_return, 2):
        if layout.AssignView(candidate, view_b):
            break
    else:
        raise RuntimeError("impossible de placer la seconde vue dans le layout (image 5)")

    rep_a = Show(interp_a, view_a)
    rep_a.Representation = "Surface"
    ColorBy(rep_a, ("POINTS", "p"))
    p_lut = GetColorTransferFunction("p")
    p_lut.ApplyPreset("Cool to Warm", True)  # divergent : rouge = surpression, bleu = depression
    rng = percentile_range(tip, "p", "CELLS", lo=2, hi=98)
    if rng:
        L = max(abs(rng[0]), abs(rng[1]))
        p_lut.RescaleTransferFunction(-L, L)
        suffix = " (p2-p98, centree sur 0)"
    else:
        p_lut.RescaleTransferFunctionToDataRange(True)
        suffix = ""
    rep_a.SetScalarBarVisibility(view_a, True)
    style_scalarbar(GetScalarBar(p_lut, view_a), f"p [m²/s²]{suffix}", location="Lower Right Corner")

    rep_b = Show(interp_b, view_b)
    rep_b.Representation = "Surface"
    ColorBy(rep_b, ("POINTS", "p"))
    rep_b.SetScalarBarVisibility(view_b, False)  # meme LUT, une seule barre affichee

    rep_stem_a = solid_body(stem, view_a, color=(0.6, 0.6, 0.62))
    rep_stem_a.Opacity = 0.35
    rep_stem_b = solid_body(stem, view_b, color=(0.6, 0.6, 0.62))
    rep_stem_b.Opacity = 0.35

    # Camera alignee sur la normale MOYENNE reelle de chaque groupe (pas un
    # axe suppose) : chaque face est vue de face, quel que soit son orientation.
    frame_camera(view_a, bounds, direction=mean0, up=safe_up(mean0), zoom=2.1)
    frame_camera(view_b, bounds, direction=mean1, up=safe_up(mean1), zoom=2.1)

    prov = provenance_line(args.cas, args.time, ETAT_DEMO) + " -- p, echelle commune"
    add_provenance(view_a, f"face A, {label0} -- " + prov)
    add_provenance(view_b, f"face B, {label1} -- " + prov)

    Render(view_a)
    Render(view_b)
    save(layout, os.path.join(args.out_dir, "05_pression_pales.png"))
    print(f"  image 5 : angle entre les deux normales moyennes = {angle_deg:.1f} deg"
          f" (180 = separation parfaite) ; p_moyen face A={p_mean0:.2f}, face B={p_mean1:.2f}")


# --------------------------------------------------------------------------- #
# Image 6 (bonus) -- zoom couches de prismes, maillage seul
# --------------------------------------------------------------------------- #

def read_layer_stack_thickness(case_dir):
    """Epaisseur totale de la pile de couches de prismes, lue dans le
    snappyHexMeshDict du CAS LUI-MEME (pas une constante figee) -- pour que
    le zoom reste juste si un cas V2 change ces valeurs.
    Retourne None si le fichier ou les cles ne sont pas trouves (repli gere
    par l'appelant, jamais une valeur inventee).
    """
    path = os.path.join(case_dir, "system", "snappyHexMeshDict")
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            text = fh.read()
    except OSError:
        return None
    m_first = re.search(r"\bfirstLayerThickness\s+([0-9.eE+-]+)\s*;", text)
    m_ratio = re.search(r"\bexpansionRatio\s+([0-9.eE+-]+)\s*;", text)
    m_n = re.search(r'"propeller\.\*"\s*\{\s*nSurfaceLayers\s+(\d+)\s*;', text)
    if not (m_first and m_ratio and m_n):
        return None
    first, ratio, n = float(m_first.group(1)), float(m_ratio.group(1)), int(m_n.group(1))
    if abs(ratio - 1.0) < 1e-12:
        return first * n
    return first * (ratio ** n - 1.0) / (ratio - 1.0)


def image_06(args):
    """REFAIT le 14/09 : la version precedente coupait par un plan NORMAL A
    L'AXE (Y) -- ce plan est quasi TANGENT a la paroi cylindrique du moyeu a
    l'endroit zoome, donc les couches n'y apparaissent que de biais, sur la
    tranche (constate en regardant l'image, pas un probleme de zoom). Pour
    voir une pile de prismes s'epaissir, le plan de coupe doit etre
    PERPENDICULAIRE A LA PAROI : ici, la paroi du moyeu est un cylindre
    d'axe Y, sa normale locale en (x=rayon, z=0) est +X -- un plan de coupe
    normal Z (le plan X-Y) contient a la fois cette normale et l'axe Y, donc
    tranche PERPENDICULAIREMENT au mur et montre les couches croitre le long
    de X. C'est la meme famille de coupe que l'image 3 (normal Z), a une
    autre origine et un zoom radicalement plus serre.
    """
    case_layers = f"{args.cas}_layers"
    case_dir = f"Helice/{case_layers}"
    if not os.path.isdir(case_dir):
        print(f"  bonus ignore : {case_dir} n'existe pas")
        return
    reader = make_reader(case_dir, ["internalMesh"], [], 0.0)
    prop = make_reader(
        case_dir,
        ["patch/propellerTip", "patch/propellerStem1", "patch/propellerStem2", "patch/propellerStem3"],
        [], 0.0,
    )

    # Zoom sur le CORPS de la pale (Stem2, mi-envergure), pas sur le bout :
    # ce cas retire explicitement les couches au bout de pale
    # (propellerTipEdge, nSurfaceLayers 0 -- LOT N, 13/09).
    stem_reader = make_reader(case_dir, ["patch/propellerStem2"], [], 0.0)
    stem_bounds = stem_reader.GetDataInformation().GetBounds()
    py = (stem_bounds[2] + stem_bounds[3]) / 2.0
    x_wall = stem_bounds[1]  # rayon du moyeu (surface, bord +X), a mi-envergure

    thickness = read_layer_stack_thickness(case_dir)
    n_layers_m = re.search(r'"propeller\.\*"\s*\{\s*nSurfaceLayers\s+(\d+)\s*;',
                            open(os.path.join(case_dir, "system", "snappyHexMeshDict")).read())
    first_m = re.search(r"\bfirstLayerThickness\s+([0-9.eE+-]+)\s*;",
                         open(os.path.join(case_dir, "system", "snappyHexMeshDict")).read())
    n_layers = int(n_layers_m.group(1)) if n_layers_m else None
    first_thickness = float(first_m.group(1)) if first_m else None
    if thickness is None or thickness <= 0:
        print("  bonus : epaisseur de couches non lue -- repli 2 mm (non verifie)")
        thickness = 0.002

    # Fenetre de coupe : X de juste-sous-le-mur a bien au-dela de la pile
    # (maillage de coeur inclus), Y sur une bonne portion d'envergure pour le
    # contexte, Z tres fin (le plan lui-meme est a z=0).
    # y_span reste du MEME ORDRE que la fenetre X (pas une longue bande) :
    # frame_camera cadre sur la DIAGONALE de la boite -- un Y demesure par
    # rapport a X (essaye : 40x l'epaisseur) noie le detail des couches dans
    # une bande verticale ou seul le maillage de coeur, plus grossier, reste
    # visible a l'oeil (constate le 14/09).
    x_near, x_far = x_wall - thickness * 0.5, x_wall + thickness * 6.0
    y_span = thickness * 5.0
    zoom_bounds = (x_near, x_far, py - y_span, py + y_span, -thickness * 2, thickness * 2)

    sl = Slice(Input=reader)
    sl.SliceType = "Plane"
    sl.SliceType.Origin = [0.0, py, 0.0]
    sl.SliceType.Normal = [0.0, 0.0, 1.0]
    sl.UpdatePipeline(time=0.0)
    detail = clip_box(sl, zoom_bounds)

    # Layout a deux cellules (meme technique verifiee que l'image 5) :
    # AssignView(0,...) explicite, puis SplitViewHorizontal + (retour+1).
    layout = CreateLayout("couches_prismes")
    view_l = CreateView("RenderView")
    view_l.ViewSize = list(VIEW_SIZE)
    view_l.Background = [1.0, 1.0, 1.0]
    view_l.UseColorPaletteForBackground = 0
    view_l.OrientationAxesVisibility = 0
    layout.AssignView(0, view_l)
    split_return = layout.SplitViewHorizontal(view_l, 0.4)
    view_r = CreateView("RenderView")
    view_r.ViewSize = list(VIEW_SIZE)
    view_r.Background = [1.0, 1.0, 1.0]
    view_r.UseColorPaletteForBackground = 0
    view_r.OrientationAxesVisibility = 0
    for candidate in (split_return + 1, split_return, 2):
        if layout.AssignView(candidate, view_r):
            break
    else:
        raise RuntimeError("impossible de placer la seconde vue (image 06)")

    # ---- Panneau gauche : vue d'ensemble + rectangle de reperage ----
    solid_body(prop, view_l, color=(0.55, 0.55, 0.58))
    prop_bounds = prop.GetDataInformation().GetBounds()
    rect = [
        [x_near, py - y_span, 0.0], [x_far, py - y_span, 0.0],
        [x_far, py + y_span, 0.0], [x_near, py + y_span, 0.0], [x_near, py - y_span, 0.0],
    ]
    for a, b in zip(rect[:-1], rect[1:]):
        seg = Line(Point1=a, Point2=b)
        srep = Show(seg, view_l)
        srep.LineWidth = 3
        srep.AmbientColor = srep.DiffuseColor = [0.85, 0.1, 0.1]
    frame_camera(view_l, prop_bounds, direction=(0.15, 0.75, 0.65), up=(0.0, 0.0, 1.0), zoom=2.1)
    add_provenance(view_l, f"{case_layers} · vue d'ensemble · t = 0 s · {ETAT_MAILLAGE}"
                   " -- rectangle rouge = zone agrandie (panneau de droite)")

    # ---- Panneau droit : agrandissement ----
    rep_r = Show(detail, view_r)
    rep_r.Representation = "Surface With Edges"
    solid_color(rep_r, (0.88, 0.88, 0.88))
    rep_r.EdgeColor = [0.05, 0.05, 0.05]
    rep_r.LineWidth = 1.1
    # up = Y : X (mur -> coeur) se lit a l'horizontale, mur a gauche.
    frame_camera(view_r, zoom_bounds, direction=(0.0, 0.0, 1.0), up=(0.0, 1.0, 0.0), zoom=1.25)
    add_provenance(view_r, f"{case_layers} · maillage a couches · t = 0 s · {ETAT_MAILLAGE}"
                   " -- agrandissement, coupe perpendiculaire a la paroi")
    if first_thickness:
        ann_text = f"{n_layers or '?'} couches, 1ere epaisseur {first_thickness * 1000:.3g} mm"
    else:
        ann_text = f"{n_layers or '?'} couches"
    ann = Text()
    ann.Text = ann_text
    d = Show(ann, view_r)
    d.WindowLocation = "Upper Left Corner"
    d.FontSize = 11
    d.Color = [0, 0, 0]
    core = Text()
    core.Text = "maillage de coeur ->"
    dcore = Show(core, view_r)
    dcore.WindowLocation = "Upper Right Corner"
    dcore.FontSize = 11
    dcore.Color = [0, 0, 0]

    Render(view_l)
    Render(view_r)
    save(layout, os.path.join(args.out_dir, "06_couches_prismes.png"))


# --------------------------------------------------------------------------- #
# Image 7 -- champ de vitesse (coupe), Image 8 -- turbulence k (coupe)
# --------------------------------------------------------------------------- #

def _field_reader_and_slice(args, array_name):
    """Coupe commune aux images 07/08 : plan (0,0,0)/normale z, resserree sur
    l'helice + sillage proche (defaut 3.3), champ interpole POINTS (defaut
    3.1). Retourne (slice_interpole, prop_bounds, zoom_bounds)."""
    case_dir = f"Helice/{args.cas}"
    reader = make_reader(case_dir, ["internalMesh"], [array_name], args.time)
    prop = make_reader(
        case_dir,
        ["patch/propellerTip", "patch/propellerStem1", "patch/propellerStem2", "patch/propellerStem3"],
        [], args.time,
    )
    prop_bounds = prop.GetDataInformation().GetBounds()
    zoom_bounds = propeller_zoom_bounds(prop_bounds)

    sl = Slice(Input=reader)
    sl.SliceType = "Plane"
    sl.SliceType.Origin = [0.0, 0.0, 0.0]
    sl.SliceType.Normal = [0.0, 0.0, 1.0]
    sl.UpdatePipeline(time=args.time)
    sl = clip_box(sl, zoom_bounds)
    # 3.1 -- CELL DATA -> POINT DATA : sans ca, ColorBy(CELLS,...) peint
    # chaque maille d'une teinte plate (rendu en blocs, constate le 14/09).
    interp = interpolate_to_points(sl)
    return interp, prop, prop_bounds, zoom_bounds


def image_07(args):
    args_case_dir = f"Helice/{args.cas}"
    interp, prop, prop_bounds, zoom_bounds = _field_reader_and_slice(args, "U")

    view = new_view()
    rep = Show(interp, view)
    rep.Representation = "Surface"
    ColorBy(rep, ("POINTS", "U"))
    lut = GetColorTransferFunction("U")
    lut.ApplyPreset("Viridis (matplotlib)", True)  # sequentiel : |U| n'a pas de zero a centrer
    rng = percentile_range(interp, "U", "POINTS", lo=2, hi=98)
    suffix = ""
    if rng:
        lut.RescaleTransferFunction(rng[0], rng[1])
        suffix = " (p2-p98)"
    else:
        lut.RescaleTransferFunctionToDataRange(True)
    rep.SetScalarBarVisibility(view, True)
    style_scalarbar(GetScalarBar(lut, view), f"|U| [m/s]{suffix}")

    # 3.4 -- corps solide DANS la vue, sinon la pale est un trou blanc.
    solid_body(prop, view, color=(0.55, 0.55, 0.58))

    frame_camera(view, zoom_bounds, direction=(0.0, 0.05, 1.0), up=(1.0, 0.0, 0.0), zoom=1.5)
    add_flow_arrow(view, zoom_bounds, subject_bounds=prop_bounds)
    add_scale_bar(view, zoom_bounds, 0.02)
    add_provenance(view, provenance_line(args.cas, args.time, ETAT_DEMO)
                   + " -- champ de vitesse (norme), coupe pres helice, plan (0,0,0)/normale z")
    Render(view)
    save(view, os.path.join(args.out_dir, "07_vitesse.png"))


def image_08(args):
    """k s'etale sur des decades (quasi nul loin de la pale, pic au bout) :
    UNE ECHELLE LINEAIRE NE MONTRE JAMAIS UN CHAMP ETALE SUR DES DECADES --
    vaut aussi pour epsilon, nut, Q, a reappliquer si on les rend un jour.
    Echelle LOG + Threshold : seule la zone turbulente reste coloree, le
    reste du domaine s'affiche en maillage gris (constat 14/09 : rectangle
    noir avec deux points brillants en lineaire -- tout le signal utile tient
    dans les 4 dernieres decades sous le maximum).
    """
    case_dir = f"Helice/{args.cas}"
    interp, prop, prop_bounds, zoom_bounds = _field_reader_and_slice(args, "k")

    # k_max robuste (p99.9, pas le max brut). Regle demandee : seuil bas =
    # k_max/1e4 (suppose un plancher quasi nul loin de la paroi). VERIFIE FAUX
    # sur ce champ (14/09) : k minimum reel sur tout le domaine = 0,033, pas
    # ~0 -- k_max/1e4 tombe alors SOUS le plancher reel, le Threshold ne
    # filtre rien du tout (896464/896464 cellules passent, confirme par
    # mesure directe), et les deux representations (fond gris + zone
    # coloree) se recouvrent exactement -> z-fighting (motif rouge/blanc en
    # dents de scie a l'ecran, pas un vrai defaut de donnee).
    # Repli adopte : seuil bas = PERCENTILE (p85), qui filtre toujours
    # reellement quel que soit le plancher du champ -- l'echelle reste log.
    rng = percentile_range(interp, "k", "POINTS", lo=85, hi=99.9)
    k_max = rng[1] if rng else None
    k_low = rng[0] if rng else None

    view = new_view()

    # Fond : le maillage COMPLET de la coupe, gris, pour que "le reste" reste
    # lisible comme du maillage et non comme du vide.
    rep_bg = Show(interp, view)
    rep_bg.Representation = "Surface With Edges"
    solid_color(rep_bg, (0.88, 0.88, 0.88))
    rep_bg.EdgeColor = [0.6, 0.6, 0.6]
    rep_bg.LineWidth = 0.3

    if k_max and k_low and k_max > k_low > 0:
        thresh = Threshold(Input=interp)
        thresh.Scalars = ["POINTS", "k"]
        low = k_low
        thresh.LowerThreshold = low
        thresh.UpperThreshold = k_max
        thresh.ThresholdMethod = "Between"
        thresh.UpdatePipeline()

        rep = Show(thresh, view)
        rep.Representation = "Surface"
        ColorBy(rep, ("POINTS", "k"))
        lut = GetColorTransferFunction("k")
        lut.ApplyPreset("Inferno (matplotlib)", True)
        lut.UseLogScale = 1
        lut.RescaleTransferFunction(low, k_max)
        rep.SetScalarBarVisibility(view, True)
        style_scalarbar(GetScalarBar(lut, view), f"k [m²/s²] (log, >p85, {low:.1e}-{k_max:.1e})")
    else:
        print("  image 08 : k_max non mesure -- seuil/log ignores, repli lineaire complet")
        rep = Show(interp, view)
        ColorBy(rep, ("POINTS", "k"))

    solid_body(prop, view, color=(0.55, 0.55, 0.58))

    frame_camera(view, zoom_bounds, direction=(0.0, 0.05, 1.0), up=(1.0, 0.0, 0.0), zoom=1.5)
    add_flow_arrow(view, zoom_bounds, subject_bounds=prop_bounds)
    add_scale_bar(view, zoom_bounds, 0.02)
    # Correction du 14/09 : "zone turbulente seule coloree, reste quasi nul"
    # est FAUX -- k ne descend jamais sous 0,033 nulle part dans le domaine
    # (niveau ambiant impose a l'entree, physique, pas une absence de
    # turbulence). L'image montre le HAUT de la distribution (>p85), pas un
    # seuil physique de "turbulence presente / absente".
    add_provenance(view, provenance_line(args.cas, args.time, ETAT_DEMO)
                   + " -- k produite au bout de pale, 1 ordre de grandeur au-dessus"
                     " du niveau ambiant (image = >p85, pas un seuil physique)")
    Render(view)
    save(view, os.path.join(args.out_dir, "08_turbulence.png"))


IMAGES = {
    "1": image_01,
    "2": image_02,
    "3": image_03,
    "4": image_04,
    "5": image_05,
    "6": image_06,
    "7": image_07,
    "8": image_08,
}


def parse_args(argv):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cas", default="case_kEpsilon",
                   help="cas de reference pour les images 1-5 (ex: case_kEpsilon). "
                        "L'image 6 (bonus) lit <cas>_layers si ce dossier existe.")
    p.add_argument("--time", type=float, default=0.06, help="instant a lire (deja sur disque)")
    p.add_argument("--out-dir", default="Helice/Images/galerie", help="dossier de sortie des PNG")
    p.add_argument("--only", default=None, help="sous-ensemble d'images a regenerer, ex: 1,5")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])
    os.makedirs(args.out_dir, exist_ok=True)
    wanted = args.only.split(",") if args.only else list(IMAGES.keys())
    for key in wanted:
        key = key.strip()
        fn = IMAGES.get(key)
        if fn is None:
            print(f"image inconnue : {key}", file=sys.stderr)
            continue
        print(f"-- image {key} --")
        fn(args)


if __name__ == "__main__":
    main()
