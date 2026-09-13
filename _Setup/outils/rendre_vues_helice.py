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
    rep.Representation = "Surface"
    solid_color(rep, (0.55, 0.58, 0.62))
    bounds = reader.GetDataInformation().GetBounds()
    # Vue quasi axiale (le long de l'axe Y) legerement inclinee : c'est ce qui
    # permet de compter les 4 pales autour du moyeu -- une vraie vue "trois
    # quarts" (perpendiculaire a l'axe) les mettrait en majorite de profil.
    frame_camera(view, bounds, direction=(0.32, 0.82, 0.42), up=(0.0, 0.0, 1.0), zoom=2.3)
    add_provenance(view, provenance_line(args.cas, args.time, ETAT_DEMO))
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
    rep_prop.Representation = "Surface"
    solid_color(rep_prop, (0.55, 0.58, 0.62))

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
    frame_camera(view, bounds, direction=(0.55, 0.35, 0.75), up=(0.0, 1.0, 0.0), zoom=1.7)
    add_provenance(view, provenance_line(args.cas, args.time, ETAT_DEMO)
                   + " -- domaine : outerCylinder + inlet/outlet")
    Render(view)
    save(view, os.path.join(args.out_dir, "02_geometrie_domaine.png"))


# --------------------------------------------------------------------------- #
# Image 3 -- coupe du maillage volumique
# --------------------------------------------------------------------------- #

def image_03(args):
    case_dir = f"Helice/{args.cas}"
    reader = make_reader(case_dir, ["internalMesh"], [], args.time)

    sl = Slice(Input=reader)
    sl.SliceType = "Plane"
    sl.SliceType.Origin = [0.0, 0.0, 0.0]
    sl.SliceType.Normal = [0.0, 0.0, 1.0]
    sl.UpdatePipeline(time=args.time)

    view = new_view()
    rep = Show(sl, view)
    rep.Representation = "Surface With Edges"
    solid_color(rep, (0.85, 0.85, 0.85))
    rep.EdgeColor = [0.1, 0.1, 0.1]
    rep.LineWidth = 0.5

    bounds = reader.GetDataInformation().GetBounds()
    # Cadrage large (vue de face sur le plan de coupe) pour que le contraste
    # maille fin pres de la pale / maille grossier au loin soit visible.
    frame_camera(view, bounds, direction=(0.0, 0.05, 1.0), up=(0.0, 1.0, 0.0), zoom=1.55)
    add_provenance(view, provenance_line(args.cas, args.time, ETAT_DEMO)
                   + " -- coupe maillage, plan (0,0,0)/normale z")
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
    rep_prop.Representation = "Surface"
    solid_color(rep_prop, (0.5, 0.5, 0.5))

    rep_ami1 = Show(ami1, view)
    rep_ami1.Representation = "Surface"
    solid_color(rep_ami1, (0.85, 0.15, 0.1))  # rouge, rotor (AMI1, reduite)
    rep_ami1.Opacity = 0.6

    rep_ami2 = Show(ami2, view)
    rep_ami2.Representation = "Surface"
    solid_color(rep_ami2, (0.1, 0.35, 0.85))  # bleu, stator (AMI2)
    rep_ami2.Opacity = 0.45

    bounds = dom.GetDataInformation().GetBounds()
    frame_camera(view, bounds, direction=(0.6, 0.3, 0.75), up=(0.0, 1.0, 0.0), zoom=1.6)
    add_provenance(view, provenance_line(args.cas, args.time, ETAT_DEMO)
                   + " -- AMI1 (rouge) / AMI2 (bleu), interface de maillage glissant")
    Render(view)
    save(view, os.path.join(args.out_dir, "04_interface_AMI.png"))


# --------------------------------------------------------------------------- #
# Image 5 -- pression sur les pales, deux vues (echelle commune)
# --------------------------------------------------------------------------- #

def image_05(args):
    case_dir = f"Helice/{args.cas}"
    reader = make_reader(
        case_dir,
        ["patch/propellerTip", "patch/propellerStem1", "patch/propellerStem2", "patch/propellerStem3"],
        ["p"],
        args.time,
    )
    bounds = reader.GetDataInformation().GetBounds()

    # Layout a deux cellules. Verifie a la main sur cette install (5.11.2,
    # pvbatch) : CreateView() NE place PAS automatiquement dans le layout ;
    # il faut un AssignView(0, ...) explicite. Et apres SplitViewHorizontal(),
    # le numero de cellule qu'il RETOURNE n'est pas celui qui marche pour la
    # nouvelle vue -- empiriquement c'est (retour + 1). D'ou l'essai des deux.
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

    rep_a = Show(reader, view_a)
    rep_a.Representation = "Surface"
    ColorBy(rep_a, ("CELLS", "p"))
    p_lut = GetColorTransferFunction("p")
    p_lut.RescaleTransferFunctionToDataRange(True)
    rep_a.SetScalarBarVisibility(view_a, True)
    sb = GetScalarBar(p_lut, view_a)
    sb.Title = "p [m2/s2]"
    sb.ComponentTitle = ""

    rep_b = Show(reader, view_b)
    rep_b.Representation = "Surface"
    ColorBy(rep_b, ("CELLS", "p"))
    rep_b.SetScalarBarVisibility(view_b, False)  # une seule echelle affichee, commune aux deux

    # Deux points de vue antipodaux (camera symetrique par rapport au centre) :
    # PAS de coupe planaire, la geometrie est vrillee (echec du 13/09) --
    # l'orientation de la camera separe les faces, jamais une geometrie coupee.
    dir_a = (1.0, 0.35, 0.25)
    dir_b = tuple(-c for c in dir_a)
    frame_camera(view_a, bounds, direction=dir_a, up=(0.0, 1.0, 0.0), zoom=2.1)
    frame_camera(view_b, bounds, direction=dir_b, up=(0.0, 1.0, 0.0), zoom=2.1)

    prov = provenance_line(args.cas, args.time, ETAT_DEMO) + " -- p, echelle commune"
    add_provenance(view_a, "intrados (cote pression) -- " + prov)
    add_provenance(view_b, "extrados (cote succion) -- " + prov)

    Render(view_a)
    Render(view_b)
    save(layout, os.path.join(args.out_dir, "05_pression_pales.png"))


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
    case_layers = f"{args.cas}_layers"
    case_dir = f"Helice/{case_layers}"
    if not os.path.isdir(case_dir):
        print(f"  bonus ignore : {case_dir} n'existe pas")
        return
    reader = make_reader(case_dir, ["internalMesh"], [], 0.0)

    # Zoom sur le CORPS de la pale (Stem2, mi-envergure), pas sur le bout :
    # ce cas retire explicitement les couches au bout de pale
    # (propellerTipEdge, nSurfaceLayers 0 -- LOT N, 13/09). Zoomer sur le bout
    # montrerait 0 couche et donnerait une image trompeuse.
    stem_reader = make_reader(case_dir, ["patch/propellerStem2"], [], 0.0)
    stem_bounds = stem_reader.GetDataInformation().GetBounds()
    cy = (stem_bounds[2] + stem_bounds[3]) / 2.0
    # Point sur la SURFACE du moyeu (pas son axe) : bord +X de la coupe, a
    # mi-envergure. Les couches poussent radialement depuis ce point.
    px, py, pz = stem_bounds[1], cy, 0.0

    sl = Slice(Input=reader)
    sl.SliceType = "Plane"
    sl.SliceType.Origin = [0.0, py, 0.0]
    sl.SliceType.Normal = [0.0, 1.0, 0.0]
    sl.UpdatePipeline(time=0.0)

    # Cadrage resserre sur l'epaisseur REELLE de la pile de couches (lue dans
    # le snappyHexMeshDict de ce cas, pas une constante) : sans cette lecture,
    # un zoom cale sur la taille du moyeu (cm) est ~30x trop large pour
    # distinguer des couches sub-millimetriques.
    thickness = read_layer_stack_thickness(case_dir)
    if thickness is None or thickness <= 0:
        print("  bonus : epaisseur de couches non lue dans snappyHexMeshDict -- repli 5 mm (non verifie)")
        half = 0.005
    else:
        half = thickness * 6.0  # marge : pile complete + un peu de volume de part et d'autre
    zoom_bounds = (px - half, px + half, py - half, py + half, pz - half, pz + half)

    # Ne PAS zoomer la camera sur des donnees non decoupees : a cette echelle
    # (mm) contre un domaine a l'echelle du metre, Render() detecte un ratio
    # near/far degenere et reinitialise la camera de lui-meme (verifie : sans
    # ce Clip, la camera repart en vue d'ensemble malgre un CameraPosition
    # explicite). Le Clip ramene la geometrie AFFICHEE a l'echelle du zoom.
    clip = Clip(Input=sl)
    clip.ClipType = "Box"
    clip.ClipType.Position = [zoom_bounds[0], zoom_bounds[2], zoom_bounds[4]]
    clip.ClipType.Length = [2 * half, 2 * half, 2 * half]
    clip.Invert = 1
    clip.UpdatePipeline(time=0.0)

    view = new_view()
    rep = Show(clip, view)
    rep.Representation = "Surface With Edges"
    solid_color(rep, (0.85, 0.85, 0.85))
    rep.EdgeColor = [0.1, 0.1, 0.1]
    rep.LineWidth = 1.0

    # Vue quasi perpendiculaire au plan de coupe (axe Y) : les couches
    # s'empilent radialement DANS ce plan (X,Z) depuis la surface du moyeu --
    # une vue de face les montre comme des bandes concentriques emboitees.
    frame_camera(view, zoom_bounds, direction=(0.15, 1.0, 0.25), up=(0.0, 0.0, 1.0), zoom=1.3)
    add_provenance(
        view,
        f"{case_layers} · maillage a couches (6 couches, propeller.*) · t = 0 s · {ETAT_MAILLAGE}"
        " -- zoom corps de pale (pas le bout, couches retirees a propellerTipEdge)",
    )
    Render(view)
    save(view, os.path.join(args.out_dir, "06_couches_prismes.png"))


IMAGES = {
    "1": image_01,
    "2": image_02,
    "3": image_03,
    "4": image_04,
    "5": image_05,
    "6": image_06,
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
