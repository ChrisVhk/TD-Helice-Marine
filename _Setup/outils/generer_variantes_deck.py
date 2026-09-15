#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère les deux variantes du deck S02 (LOT 3, consigne du 15/09) à partir d'une
SOURCE UNIQUE, `Seances/S02_Slides.md` — plutôt que deux fichiers `.md` qui
divergent silencieusement l'un de l'autre au fil des corrections (c'est exactement
ce qui menaçait de se produire entre `S02_Slides.md` et
`S02bis_Rattrapage-groupes-1-2_Slides.md`, fusionnés ce jour dans le premier, le
second étant supprimé une fois la fusion vérifiée).

Le bloc rattrapage est marqué dans la source par
`<!-- RATTRAPAGE G1-G2 -->` ... `<!-- FIN RATTRAPAGE -->` (diapositives 90-93,
numérotation hors séquence pour ne jamais entrer en conflit avec la numérotation
0-7 de la séance 2, citée ailleurs dans le dépôt). Ce script ne réimplémente PAS le
parseur/remplisseur de gabarit : il réutilise tel quel `parse_slides`,
`_construire` et `TEMPLATE` de `Seances/generer_pptx_S02.py` (même convention que
tous les générateurs de deck du dépôt), en appelant seulement `parse_slides` une
fois avec `keep_rattrapage=False` et une fois avec `True`.

Produit deux fichiers, Vega (sans notesSlide, comme l'exemplaire par défaut de
tous les autres decks) :
    Seances/S02_groupe3.pptx      -- sans le bloc rattrapage
    Seances/S02_groupes1-2.pptx   -- avec le bloc rattrapage

Idempotent : ne dépend que du contenu de S02_Slides.md, jamais d'un état externe ou
d'une horloge -- relancer le script sans toucher la source reproduit des fichiers
dont le contenu XML interne est identique (voir le contrôle GATE dans le rapport de
boucle : diff après désarchivage, pas diff binaire brut, le zip peut légitimement
réordonner ses métadonnées internes sans changer le contenu).
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _find_upwards(start, dirname, max_levels=6):
    d = start
    for _ in range(max_levels):
        cand = os.path.join(d, dirname)
        if os.path.isdir(cand):
            return cand
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return None


_SETUP_DIR = _find_upwards(HERE, "_Setup")
if _SETUP_DIR is None:
    sys.exit(f"_Setup/ introuvable en remontant depuis {HERE}.")
_REPO_ROOT = os.path.dirname(_SETUP_DIR)
SEANCES_DIR = os.path.join(_REPO_ROOT, "Seances")

_S02_MODULE_PATH = os.path.join(SEANCES_DIR, "generer_pptx_S02.py")
if not os.path.isfile(_S02_MODULE_PATH):
    sys.exit(f"Générateur de base introuvable : {_S02_MODULE_PATH}")

_spec = importlib.util.spec_from_file_location("generer_pptx_S02", _S02_MODULE_PATH)
_s02 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_s02)  # exécute le module (chemins TEMPLATE/SLIDES_MD calculés à l'import)

SLIDES_MD = _s02.SLIDES_MD
OUT_G3 = os.path.join(SEANCES_DIR, "S02_groupe3.pptx")
OUT_G12 = os.path.join(SEANCES_DIR, "S02_groupes1-2.pptx")


def build():
    if not os.path.isfile(SLIDES_MD):
        sys.exit(f"Source introuvable : {SLIDES_MD}")

    with open(SLIDES_MD, encoding="utf-8") as f:
        raw = f.read()
    if "<!-- RATTRAPAGE G1-G2 -->" not in raw or "<!-- FIN RATTRAPAGE -->" not in raw:
        sys.exit(
            f"{SLIDES_MD} ne contient pas les marqueurs "
            "`<!-- RATTRAPAGE G1-G2 -->` / `<!-- FIN RATTRAPAGE -->` -- fusion LOT 3 "
            "absente ou marqueurs déplacés/renommés."
        )

    slides_g3 = _s02.parse_slides(SLIDES_MD, keep_rattrapage=False)
    slides_g12 = _s02.parse_slides(SLIDES_MD, keep_rattrapage=True)

    if len(slides_g12) <= len(slides_g3):
        sys.exit(
            f"Variante 'groupes 1-2' ({len(slides_g12)} diapos) n'a pas plus de "
            f"diapositives que 'groupe 3' ({len(slides_g3)}) -- le bloc rattrapage "
            "n'a pas été inclus, vérifier les marqueurs."
        )

    prs_g3 = _s02._construire(slides_g3, avec_notes=False)
    prs_g3.save(OUT_G3)

    prs_g12 = _s02._construire(slides_g12, avec_notes=False)
    prs_g12.save(OUT_G12)

    print(f"OK -> {OUT_G3}  ({len(slides_g3)} diapositives, sans rattrapage)")
    print(f"OK -> {OUT_G12}  ({len(slides_g12)} diapositives, avec rattrapage 90-93)")
    print(f"Contrôle obligatoire : regarder les deux rendus avant de supprimer S02bis.")


if __name__ == "__main__":
    build()
