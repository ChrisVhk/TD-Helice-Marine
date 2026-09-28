#!/usr/bin/env python3
"""Rendu de la galerie ParaView (LOT 2, consigne du 28/09 "Fiche-ParaView-autonome") --
produit, DEPUIS LE PACK (data/paraview_kit/, jamais depuis les cas de travail : c'est ce
que l'etudiant aura), les images qui ont servi a fixer les valeurs imposees de
docs/18_FICHE_PARAVIEW_autonome.md (echelles, isovaleur Q, camera). Sortie :
Images/galerie/*.png (gitignore -- ce sont les reponses visuelles, jamais distribuees).

Rejouer ce script (pvbatch scripts/rendre_galerie_paraview.py) reproduit exactement les
memes images : aucune valeur n'est choisie a l'oeil sans etre lue ici en sortie.

Vues :
  V1 sillage  : Slice normale Z, origine (0,0,0), colore |U| (lineaire, BORNES["U_mag"]).
  V2 nut      : meme slice, colore nut (log, BORNES["nut"]) -- absent en laminaire.
  V3 pression : patchs propeller* seuls, colore p (lineaire, BORNES["p"]), deux cameras
                (amont = vue depuis +Y vers -Y, aval = vue depuis -Y vers +Y).
  V4 iso-Q    : Contour Q=ISO_Q, colore |U|, pale (propeller*) en gris par-dessus.

Un filtre Cell Data to Point Data est applique avant coloration (TUTORIEL_OpenFOAM-et-
ParaView.md, piege 3 : donnees cell data affichees en damier sans lui).
"""
import sys
from pathlib import Path

from paraview.simple import (
    OpenFOAMReader, UpdatePipeline, Slice, Contour, CellDatatoPointData,
    Show, Hide, ColorBy, GetColorTransferFunction, GetActiveViewOrCreate,
    SaveScreenshot, GetDisplayProperties, Render,
    RenameSource, GetAnimationScene,
)

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / "data" / "paraview_kit"
GALERIE = ROOT / "Images" / "galerie"
GALERIE.mkdir(parents=True, exist_ok=True)

# Bornes d'echelle IMPOSEES -- mesurees sur les 3 fermetures a t=0,158 s (script
# d'exploration prealable, voir rapport). PAS l'enveloppe min/max brute pour U et p :
# l'essai avec min/max brut (0-18 pour U, -112..99 pour p) a produit des images QUASI
# UNIFORMES, ecrasees par un extremum local (U : omega*R=17,96 m/s au tip de pale, une
# seule petite zone ; p : pic de pression/depression au bord d'attaque) -- exactement le
# piege deja documente sur CE cas (TUTORIEL_OpenFOAM-et-ParaView.md, piege 1, incident du
# 13/09 sur la pression). Bornes retenues : percentile 2-98 (mesure separee, script
# d'exploration), arrondi vers l'EXTERIEUR (jamais vers l'interieur -- une borne resserree
# masquerait des valeurs reelles). nut reste sur l'enveloppe min/max brute : deja en
# echelle LOG, pas d'ecrasement constate a l'image (voir rapport).
BORNES = {
    "U_mag": (0.0, 10.0),      # p98 mesuré 9,69 m/s (3 fermetures, domaine entier) -- floor 0 gardé (stagnation réelle)
    "p": (-34.0, 16.0),        # p2/p98 mesurés -33,25/15,67 (3 fermetures, PALE SEULE -- ce que V3 colore)
    "nut": (6e-7, 9.1e-3),     # enveloppe min/max brute : min 6.4845e-7 (kOmegaSST), max 9.0369e-3 (kEpsilon) -- LOG
}
ISO_Q = 1000.0  # valeur du setup (05_GUIDE_PARAVIEW.md) -- confirmee ou remplacee, voir rapport

PATCHS_PALE = ["patch/propellerTip", "patch/propellerStem1", "patch/propellerStem2", "patch/propellerStem3"]

# ─────────────────────────────────────────────────────────────────────────
# LOT 2a (consigne du 28/09 "Correctifs-fiche18-foam-coulisses") -- UNE seule
# caméra par vue, commune à TOUS les cas (fermetures, série, layers, MRF).
# Avant : ResetCamera() par cas donnait des cotes différentes (ex. V3 aval
# -0,730 sur case_kEpsilon_layers contre -0,696 sur les 3 fermetures) -- les
# comparaisons demandées en partie C ne se superposaient pas. Valeurs figées
# ici = celles du CAS LE PLUS GRAND relevées au run précédent (elles cadrent
# large, rien n'est coupé sur les cas plus petits -- vérifié en LOT 2, voir
# rapport) :
#   V3 aval/amont  : case_kEpsilon_layers (le plus distant des 4 cas AMI)
#   V4             : case_kEpsilon_MRF (le plus distant des 7 cas)
#   V1/V2          : déjà identiques sur les 7 cas au run précédent
# ─────────────────────────────────────────────────────────────────────────
CAMERA_V1V2 = {"Position": (0.0, -0.3, 2.2529), "FocalPoint": (0.0, -0.3, 0.0),
               "ViewUp": (0.0, 1.0, 0.0), "ViewAngle": 30.0}
CAMERA_V3_AVAL = {"Position": (0.0, -0.7304, 0.0), "FocalPoint": (0.0, 0.0695, 0.0),
                  "ViewUp": (0.0, 0.0, 1.0), "ViewAngle": 30.0}
CAMERA_V3_AMONT = {"Position": (0.0, 0.8694, 0.0), "FocalPoint": (0.0, 0.0695, 0.0),
                   "ViewUp": (0.0, 0.0, 1.0), "ViewAngle": 30.0}
CAMERA_V4 = {"Position": (0.0, -0.2521, 1.8739), "FocalPoint": (0.0, -0.2521, 0.0),
             "ViewUp": (0.0, 1.0, 0.0), "ViewAngle": 30.0}

CAMERAS = {}  # rempli au fil du script, imprime a la fin


def ouvrir(case: str, patches=None):
    foam = KIT / case / f"{case}.foam"
    if not foam.is_file():
        sys.exit(f"{foam} introuvable -- pack absent ou pas encore regenere (LOT 1).")
    r = OpenFOAMReader(FileName=str(foam))
    # Cachemesh vaut 1 par défaut -- suppose un maillage STATIQUE et réutilise les points
    # déjà lus d'un pas à l'autre. Sur les cas AMI le maillage TOURNE (rotor rigide,
    # <t>/polyMesh/points change réellement, cf. LOT 1) : laissé à 1, la géométrie affichée
    # reste figée au premier pas chargé quel que soit le `time=` demandé ensuite -- seuls les
    # champs (U, p, Q...) suivent le bon pas. Repéré en comparant deux images de la série
    # kOmegaSST (0,155 et 0,159, 36° d'écart) : visuellement identiques alors que
    # `polyMesh/points` diffère bien sur disque (md5 différents).
    r.Cachemesh = 0
    r.MeshRegions = patches if patches is not None else r.MeshRegions.Available
    r.CellArrays = r.CellArrays.Available
    RenameSource(f"{case}", r)
    return r


def au_temps(reader, t):
    # UpdatePipeline(time=t, proxy=reader) mAJ le pipeline de CE reader pour un Fetch()
    # direct, mais PAS le temps de la scène -- la vue (réutilisée d'un rendu à l'autre,
    # voir nouvelle_vue()) continuait d'afficher le premier temps jamais synchronisé :
    # les 5 images de la série kOmegaSST étaient visuellement identiques malgré
    # Cachemesh=0 et des points de maillage bien différents (vérifié par Fetch direct).
    # GetAnimationScene().AnimationTime pilote le TimeKeeper que Render()/SaveScreenshot
    # interrogent réellement.
    UpdatePipeline(time=t, proxy=reader)
    GetAnimationScene().AnimationTime = t


def champ_present(reader, nom: str) -> bool:
    return nom in reader.CellArrays.Available


def nouvelle_vue():
    v = GetActiveViewOrCreate("RenderView")
    v.ViewSize = [1920, 1080]
    v.OrientationAxesVisibility = 0
    return v


def colorer(display, view, nom, bornes, log=False):
    # POINTS, pas CELLS : chaque représentation coloriée est construite sur une sortie de
    # CellDatatoPointData (voir vue_v1/v2/v3/v4) -- colorier par CELLS sur cette sortie ne
    # trouve pas de plage valide (WARN "Could not determine array range" repéré au premier
    # rendu, images géométriquement correctes mais entièrement plates, aucune couleur).
    ColorBy(display, ("POINTS", nom))
    display.RescaleTransferFunctionToDataRange(False)
    ctf = GetColorTransferFunction(nom)
    ctf.RescaleTransferFunction(bornes[0], bornes[1])
    ctf.UseLogScale = 1 if log else 0
    display.SetScalarBarVisibility(view, True)


def appliquer_camera(view, cam):
    """Caméra FIXE, commune à tous les cas d'une même vue (LOT 2a du 28/09) -- plus de
    ResetCamera() par cas : les cotes différaient d'un cas à l'autre (ex. V3 aval -0,730 sur
    case_kEpsilon_layers contre -0,696 sur les 3 fermetures), rendant les comparaisons
    demandées en partie C non superposables. cam = un des CAMERA_* ci-dessus."""
    c = view.GetActiveCamera()
    c.SetPosition(*cam["Position"])
    c.SetFocalPoint(*cam["FocalPoint"])
    c.SetViewUp(*cam["ViewUp"])
    c.SetViewAngle(cam["ViewAngle"])


def camera_info(view):
    c = view.GetActiveCamera()
    return {
        "Position": tuple(round(x, 4) for x in c.GetPosition()),
        "FocalPoint": tuple(round(x, 4) for x in c.GetFocalPoint()),
        "ViewUp": tuple(round(x, 4) for x in c.GetViewUp()),
        "ViewAngle": round(c.GetViewAngle(), 3),
    }


def capturer(view, nom_fichier: str, cle_camera: str = None):
    Render(view)
    path = GALERIE / nom_fichier
    SaveScreenshot(str(path), view, ImageResolution=[1920, 1080])
    if cle_camera:
        CAMERAS[cle_camera] = camera_info(view)
    print(f"  -> Images/galerie/{nom_fichier}  (camera: {camera_info(view)})")


def vue_v1_sillage(case: str, t, suffixe: str):
    r = ouvrir(case)
    au_temps(r, t)
    pdata = CellDatatoPointData(Input=r)
    sl = Slice(Input=pdata)
    sl.SliceType.Origin = [0.0, 0.0, 0.0]
    sl.SliceType.Normal = [0.0, 0.0, 1.0]
    view = nouvelle_vue()
    disp = Show(sl, view)
    colorer(disp, view, "U", BORNES["U_mag"])
    appliquer_camera(view, CAMERA_V1V2)
    capturer(view, f"V1_sillage_{suffixe}.png", f"V1_{suffixe}")
    Hide(sl, view)
    del r, pdata, sl, view


def vue_v2_nut(case: str, t, suffixe: str):
    r = ouvrir(case)
    au_temps(r, t)
    if not champ_present(r, "nut"):
        print(f"  V2 {suffixe} : champ nut ABSENT (constate, pas une image -- {case} n'a pas de modele de turbulence).")
        del r
        return
    pdata = CellDatatoPointData(Input=r)
    sl = Slice(Input=pdata)
    sl.SliceType.Origin = [0.0, 0.0, 0.0]
    sl.SliceType.Normal = [0.0, 0.0, 1.0]
    view = nouvelle_vue()
    disp = Show(sl, view)
    colorer(disp, view, "nut", BORNES["nut"], log=True)
    appliquer_camera(view, CAMERA_V1V2)  # même caméra que V1 : vues comparables
    capturer(view, f"V2_nut_{suffixe}.png", f"V2_{suffixe}")
    Hide(sl, view)
    del r, pdata, sl, view


def vue_v3_pression(case: str, t, suffixe: str):
    r = ouvrir(case, patches=PATCHS_PALE)
    au_temps(r, t)
    pdata = CellDatatoPointData(Input=r)
    view = nouvelle_vue()
    disp = Show(pdata, view)
    colorer(disp, view, "p", BORNES["p"])
    # Caméra "aval" (face en pression, l'intrados) puis "amont" (face en dépression,
    # l'extrados) : deux caméras FIXES (LOT 2a), communes aux 3 fermetures ET à
    # case_kEpsilon_layers (partie C1) -- plus de ResetCamera() par cas.
    appliquer_camera(view, CAMERA_V3_AVAL)
    capturer(view, f"V3_pression_aval_{suffixe}.png", f"V3_aval_{suffixe}")
    appliquer_camera(view, CAMERA_V3_AMONT)
    capturer(view, f"V3_pression_amont_{suffixe}.png", f"V3_amont_{suffixe}")
    Hide(pdata, view)
    del r, pdata, view


def vue_v4_isoQ(case: str, t, suffixe: str):
    r = ouvrir(case)
    au_temps(r, t)
    pdata = CellDatatoPointData(Input=r)
    contour = Contour(Input=pdata)
    contour.ContourBy = ["POINTS", "Q"]
    contour.Isosurfaces = [ISO_Q]
    view = nouvelle_vue()
    disp_c = Show(contour, view)
    colorer(disp_c, view, "U", BORNES["U_mag"])
    # Pale en gris : reconstruire un reader borné aux patchs propeller* pour la surface.
    r2 = OpenFOAMReader(FileName=str(KIT / case / f"{case}.foam"))
    r2.Cachemesh = 0
    r2.MeshRegions = PATCHS_PALE
    r2.CellArrays = r2.CellArrays.Available
    au_temps(r2, t)
    disp_pale = Show(r2, view)
    ColorBy(disp_pale, None)
    disp_pale.AmbientColor = [0.6, 0.6, 0.6]
    disp_pale.DiffuseColor = [0.6, 0.6, 0.6]
    appliquer_camera(view, CAMERA_V4)  # caméra fixe, commune à A/B/C2 (LOT 2a)
    capturer(view, f"V4_isoQ_{suffixe}.png", f"V4_{suffixe}")
    Hide(contour, view)
    Hide(r2, view)
    del r, pdata, contour, view, r2


def ligne(txt):
    print("\n" + "=" * 10 + " " + txt + " " + "=" * 10)


# ─── 3 fermetures à t = 0,158 : V1, V2, V3, V4 ────────────────────────────
for case in ("case_kEpsilon", "case_kOmegaSST", "case_laminar"):
    ligne(f"{case} @ 0.158")
    vue_v1_sillage(case, 0.158, f"{case}_t0158")
    vue_v2_nut(case, 0.158, f"{case}_t0158")
    vue_v3_pression(case, 0.158, f"{case}_t0158")
    vue_v4_isoQ(case, 0.158, f"{case}_t0158")

# ─── Série kOmegaSST 0,155→0,159 : V1, V4 ────────────────────────────────
ligne("case_kOmegaSST série 0.155-0.159")
for t in (0.155, 0.156, 0.157, 0.158, 0.159):
    suf = f"case_kOmegaSST_t{str(t).replace('0.', '')}"
    vue_v1_sillage("case_kOmegaSST", t, suf)
    vue_v4_isoQ("case_kOmegaSST", t, suf)

# ─── Couches vs sans couches à 0,158 : V1, V3 sur case_kEpsilon_layers ───
# (case_kEpsilon déjà rendu ci-dessus dans les 3 fermetures : réutilisé pour comparer)
ligne("case_kEpsilon_layers @ 0.158 (vs case_kEpsilon)")
vue_v1_sillage("case_kEpsilon_layers", 0.158, "case_kEpsilon_layers_t0158")
vue_v3_pression("case_kEpsilon_layers", 0.158, "case_kEpsilon_layers_t0158")

# ─── 3 MRF à l'itération 1500 : V1, V4 ───────────────────────────────────
ligne("MRF @ itération 1500")
for case in ("case_kEpsilon_MRF", "case_kOmegaSST_MRF", "case_laminar_MRF"):
    vue_v1_sillage(case, 1500.0, f"{case}_i1500")
    vue_v4_isoQ(case, 1500.0, f"{case}_i1500")

ligne("CAMÉRAS RELEVÉES (à recopier dans la fiche)")
for k, v in CAMERAS.items():
    print(f"{k} : Position={v['Position']} FocalPoint={v['FocalPoint']} "
          f"ViewUp={v['ViewUp']} ViewAngle={v['ViewAngle']}")

print(f"\n{len(list(GALERIE.glob('*.png')))} images dans {GALERIE}")
