#!/usr/bin/env python3
"""
generer_figure_helice_3D.py — Correctif A2 (deck V2, 07/09).

Rendu 3D de la géométrie d'hélice (patch `propellerTip`, qui porte les 3 pales -- contre-intuitif :
`propellerStem1/2/3` porte l'ARBRE cylindrique, pas les pales, vérifié en rendant les deux
séparément), pvpython headless, sur le cas kEpsilon reconstruit (t=0,06). Objet du TD, absent du
deck jusqu'ici.

Usage : pvpython generer_figure_helice_3D.py
Sortie : Helice/Images/FIG-fon-s7-helice-3D.png
"""
import os

from paraview.simple import *

ICI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(ICI, "..", ".."))
HELICE = os.path.join(REPO, "Helice")
CASE_FOAM = os.path.join(HELICE, "case_kEpsilon", "case_kEpsilon.foam")
OUT = os.path.join(HELICE, "Images", "FIG-fon-s7-helice-3D.png")

if not os.path.isfile(CASE_FOAM):
    open(CASE_FOAM, "w").close()

reader = OpenFOAMReader(FileName=CASE_FOAM)
reader.CaseType = "Reconstructed Case"
# propellerTip porte les 3 pales ; propellerStem1/2/3 porte l'arbre cylindrique -- l'inverse de
# ce que les noms suggèrent, vérifié en rendant chaque patch séparément (06-07/09).
reader.MeshRegions = ["patch/propellerTip"]
reader.UpdatePipeline(time=0.06)

view = GetActiveViewOrCreate("RenderView")
view.ViewSize = [1200, 1200]
view.UseColorPaletteForBackground = 0
view.Background = [1, 1, 1]
view.Background2 = [1, 1, 1]
view.OrientationAxesVisibility = 0

disp = Show(reader, view)
disp.Representation = "Surface"
disp.DiffuseColor = [0.55, 0.60, 0.68]
disp.Specular = 0.3
ColorBy(disp, None)

view.ResetCamera()
cam = view.GetActiveCamera()
cam.Azimuth(35)
cam.Elevation(20)
view.ResetCamera()
cam.Zoom(1.3)

Render(view)
SaveScreenshot(OUT, view)
print("écrit :", OUT)
