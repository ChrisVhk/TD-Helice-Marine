#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générateur UNIQUE de support PPTX, paramétré par le numéro de séance (LOT 4, consigne
du 15/09 -- remplace `generer_pptx_S00.py`/`S02.py`/`S03.py`, trois copies qui ont
divergé de zéro fonctionnellement mais auraient continué à diverger à la prochaine
correction ponctuelle sur un seul fichier -- exactement le schéma qui a déjà produit
onze documents contradictoires ailleurs dans ce dépôt).

Adapté depuis `_Setup/MODELE_generer_pptx_seance.py` (le modèle partagé, synchronisé
depuis le noyau `ENSM-Enseignement`, jamais commité ici) -- ce fichier-ci EST la copie
adaptée à `TD-Helice-Marine`, suivie en git.

## Usage

    python3 Seances/generer_pptx_seance.py S01
    python3 Seances/generer_pptx_seance.py S02
    python3 Seances/generer_pptx_seance.py S03

Résout `SLIDES_MD` depuis le numéro de séance : `Seances/<STEM>_Slides.md`, toujours --
`SLIDES_MD_OVERRIDE` (ci-dessous) ne sert plus depuis le 18/09 (consigne « Supports-Vega »,
LOT 3) que le retrait du deck `S00` générique (fusionné dans `S01_Slides.md`, un seul
deck par séance déposable sur Vega) a vidé de ses deux seules entrées historiques.

Produit toujours DEUX fichiers (LOT B, audit charte 11/09) :
  - `Seances/<STEM>.pptx` — **exemplaire PUBLIC (GitHub)**, sans aucune part
    `notesSlide` ET sans aucune figure `licence: restreint` (GARDE 2, consigne du 18/09
    "Consolidee_Figures-et-variante-Vega" -- échoue plutôt que d'en publier une par
    erreur). Les notes de conduite sont des notes de préparation pour l'enseignant, pas un
    contenu pour les étudiants qui liraient le deck en dehors de la séance.
  - `Seances/<STEM>_enseignant.pptx` — même contenu, notes de conduite incluses ET toutes
    les figures (attribution imprimée sur chaque `restreint`). **Jamais publié.**

Et, SI ET SEULEMENT SI la source contient AU MOINS UNE figure `licence: restreint`
(détection automatique) :
  - `Seances/<STEM>_vega.pptx` — **espace fermé de l'école** : toutes les figures
    (attribution imprimée sur chaque `restreint`), sans notes de conduite. C'est ce qu'on
    dépose sur Vega quand le deck utilise des figures empruntées -- jamais sur GitHub.
    Absent quand la source n'a que des figures `libre` (serait un doublon strict du
    fichier public, jamais régénéré -- voir JOURNAL, LOT 9 de la même consigne).

Et, SI ET SEULEMENT SI la source contient un bloc marqué
`<!-- RATTRAPAGE G1-G2 --> ... <!-- FIN RATTRAPAGE -->` (détection automatique, pas un
argument à passer) — produit un fichier supplémentaire :
  - `Seances/<STEM>_groupes1-2.pptx` — même source, bloc rattrapage INCLUS. Le fichier
    public ci-dessus reste la version SANS ce bloc (ce que le groupe 3 a reçu).
Ce mécanisme remplace `_Setup/outils/generer_variantes_deck.py` (LOT 5, même consigne)
-- une seule logique de variantes, pas deux.

## Licence des figures (LOT 4, consigne du 18/09 "Consolidee_Figures-et-variante-Vega")

Chaque ligne `**Figure(s)**` porte désormais `— licence: libre` ou
`— licence: restreint — auteur: X, titre: Y, source: Z, année: NNNN` (les quatre champs
d'attribution tous requis pour `restreint`, GARDE 1 -- voir `_parse_figures`). Contrôle
indépendant, en aval de ce générateur : `_Setup/outils/verifier_pptx_restreint.sh` déplie
l'exemplaire PUBLIC et vérifie qu'aucune image restreinte (par contenu, pas par nom) n'y
est embarquée -- GARDE 2, seconde moitié.

**Contrôle obligatoire** avant toute livraison :
`_Setup/verifier_deck.sh Seances/<STEM>.pptx` — rendu en images, à REGARDER, pas
seulement généré sans erreur (voir JOURNAL.md ENSM-Enseignement, débordements du 28/08).
Vérifier aussi l'absence de notes sur l'exemplaire Vega :
`unzip -l Seances/<STEM>.pptx | grep notesSlide` doit ne rien renvoyer.

## Ce qui rend ce script portable

Remonte l'arborescence à la recherche d'un dossier `_Setup/` contenant le gabarit,
plutôt que de supposer une profondeur fixe (héritage du modèle partagé -- fonctionne
identiquement dans le monorepo `ENSM-Enseignement` et dans un dépôt de cours autonome).
`Images/` reste résolu en `../Images` (sibling de `Seances/`), déjà indépendant de la
profondeur.

## Contrat gabarit (inchangé) — treize dispositions, nommées EXACTEMENT ainsi
    Couverture · Section · Accroche · Revelation · Figure · DeuxFigures · Tableau · Cloture ·
    Corps · Rappel · FigureCommentee · Comparaison · Exemple
Voir `_Setup/NOTE_GABARIT_PPTX.md` pour le détail des placeholders par disposition et
`_Setup/specification/INVENTAIRE_DISPOSITIONS_ENSM.md` pour le mapping champ `.md` ↔
disposition. Le format `S<NN>_Slides.md` (une diapo = `## Diapo <N> — <titre>` suivi de
champs `**Disposition**`, `**Segment / timing**`, `**Contenu affiché**`, `**Figure(s)**`,
`**Crédit**`, le champ des notes, terminé par `---`) est identique à celui déjà en
usage — copier un `S02_Slides.md` existant comme gabarit de départ est le chemin le plus
rapide plutôt que d'inventer le format à partir de ce docstring.

## Piège de rédaction récurrent (LOT G+H, audit charte 12/09) — une ligne = une pensée complète
La PREMIÈRE ligne du champ `**Contenu affiché** :` devient TOUJOURS le titre de la
disposition (`body_lines[0]`, voir `build_slide`) ; les lignes suivantes vont dans le corps
— y compris pour les dispositions génériques (Corps, Accroche, Section...), pas seulement
les spécialisées. Une phrase écrite sur deux lignes dans la source, en pensant qu'elle
s'affichera comme un seul bloc continu, se retrouve donc coupée en deux : un titre qui
s'arrête au milieu d'une clause, un corps qui commence par sa fin. Trouvé QUATRE fois en
une seule boucle (deux dispositions Rappel de S01, une Accroche et une Exemple de S02,
trois Corps de S03) — un réflexe de rédaction à corriger, pas des accidents isolés :
chaque ligne de `Contenu affiché` doit être une phrase complète et autonome, jamais la
moitié d'une phrase qui se termine à la ligne suivante. Si le titre naturel est long,
mieux vaut le raccourcir que le couper.
"""
import os
import re
import sys
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import PP_PLACEHOLDER
from pptx.util import Pt

HERE = os.path.dirname(os.path.abspath(__file__))

def _find_upwards(start, dirname, max_levels=6):
    """Remonte depuis `start` à la recherche d'un dossier `dirname` (ex. `_Setup`) —
    rend ce script indépendant de la profondeur du dépôt qui l'héberge."""
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
    sys.exit(f"_Setup/ introuvable en remontant depuis {HERE} — synchronisez le noyau "
              f"d'abord (voir _Setup/SYNCHRONISER.md).")

# --- Séance passée en argument, résolue ici -- source unique pour les quatre séances.
# Vide depuis le 18/09 (consigne « Supports-Vega », LOT 3, S00 fusionné dans S01) --
# gardé comme mécanisme, pas comme registre : ne pas ajouter d'entrée ici "pour la
# prochaine séance" tant que sa source suit la convention par défaut (Seances/<STEM>_
# Slides.md) -- une entrée non nécessaire serait elle-même une divergence non
# paramétrable cachée.
SLIDES_MD_OVERRIDE = {}

if len(sys.argv) < 2:
    sys.exit(f"Usage : python3 {os.path.basename(__file__)} <STEM>  (ex. S01, S02, S03)")
STEM = sys.argv[1]
SLIDES_MD = os.path.join(HERE, SLIDES_MD_OVERRIDE.get(STEM, f"{STEM}_Slides.md"))
OUT = os.path.join(HERE, f"{STEM}.pptx")
IMG_DIR = os.path.join(HERE, "..", "Images")

def _resolve_template():
    """Le gabarit peut être .potx ou .pptx selon l'issue du repli content-type (E1,
    _Setup/generer_gabarit_ENSM_cours.py) — chercher les deux plutôt que supposer l'extension."""
    for name in ("TEMPLATE_ENSM_cours.potx", "TEMPLATE_ENSM_cours.pptx"):
        p = os.path.join(_SETUP_DIR, name)
        if os.path.isfile(p):
            return p
    return os.path.join(_SETUP_DIR, "TEMPLATE_ENSM_cours.potx")  # défaut pour le message d'erreur

TEMPLATE = _resolve_template()

FIELD_NAMES = ["Disposition", "Segment / timing", "Contenu affiché", "Figure(s)", "Crédit",
               "Notes d'orateur", "Rappel", "Figure commentée", "Comparaison", "Exemple", "Progression"]

# Charte ENSM (LOT F, audit charte 12/09) -- couleurs des cartes/pastilles de la disposition
# `Progression`. Reprises telles quelles de `_Setup/generer_gabarit_ENSM_cours.py`, pas
# redéfinies indépendamment -- une seule source pour ces sept couleurs serait préférable,
# mais MODELE_generer_pptx_seance.py doit rester exécutable seul (copié dans un dépôt de
# cours sans le reste de _Setup), donc dupliquées ici à l'identique plutôt qu'importées.
_MARINE = RGBColor(0x1A, 0x34, 0x6D)
_CORAIL = RGBColor(0xEB, 0x56, 0x00)
_WHITE = RGBColor(0xFF, 0xFF, 0xFF)
# TEAL/PALE (charte, NOTE_GABARIT_PPTX.md "Charte appliquée") -- utilisées UNIQUEMENT
# pour le remplissage direct des tableaux (LOT 4, consigne du 18/09 "Supports-Vega") :
# `ppt/tableStyles.xml` du gabarit (182 octets, `def` pointe un styleId sans aucun
# `<a:tblStyle>` le définissant) est le même fichier, non fonctionnel, que python-pptx
# lui-même distribue par défaut (vérifié le 18/09 dans `pptx/templates/default.pptx`) --
# PowerPoint/LibreOffice retombent alors sur un style Office générique (bleu/gris),
# jamais la charte. Plutôt que d'écrire à la main un `<a:tblStyle>` OOXML complet (schéma
# strict, aucun exemple valide dans ce dépôt pour le vérifier, risque de corrompre le
# fichier sans le retour visuel de PowerPoint) -- même logique que le remplissage direct
# déjà utilisé ci-dessous pour les cartes/pastilles de `Progression` -- ce script
# applique désormais le remplissage/police directement à chaque cellule, sans dépendre
# du style nommé (cassé) du gabarit.
_TEAL = RGBColor(0x1A, 0x99, 0x88)
_PALE = RGBColor(0xE8, 0xF4, 0xF2)

# ---- Parsing de <STEM>_Slides.md --------------------------------------------------------------------

_RATTRAPAGE_RE = re.compile(
    r"<!-- RATTRAPAGE G1-G2 -->.*?<!-- FIN RATTRAPAGE -->\n?", re.DOTALL
)

def strip_rattrapage(text):
    """Retire le bloc rattrapage groupes 1-2 (fusionné le 15/09, LOT 3) marqué par
    `<!-- RATTRAPAGE G1-G2 -->` ... `<!-- FIN RATTRAPAGE -->`. Utilisé pour que
    S02.pptx (canonique) reste la séance telle que le groupe 3 l'a reçue ; la variante
    « groupes 1-2 » (avec ce bloc) est produite séparément par
    `_Setup/outils/generer_variantes_deck.py`, qui réutilise `parse_slides` ci-dessous
    avec `keep_rattrapage=True` plutôt que dupliquer le parseur."""
    return _RATTRAPAGE_RE.sub("", text)

def parse_slides(path, keep_rattrapage=False):
    """Découpe le fichier Slides.md en une liste de dicts {title, disposition, body, figures,
    credit, notes, ...}. Un bloc de diapo commence à '## Diapo <N> — <titre>' et se termine au
    '---' suivant (ou à la fin)."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if not keep_rattrapage:
        text = strip_rattrapage(text)

    blocks = re.split(r"\n## Diapo \d+ — ", text)[1:]  # jette le préambule avant la 1re diapo
    slides = []
    field_re = re.compile(r"^\*\*(" + "|".join(re.escape(n) for n in FIELD_NAMES) + r")\*\*\s*:?\s*(.*)$")
    for block in blocks:
        lines = block.split("\n")
        title = lines[0].strip()
        fields = {n: [] for n in FIELD_NAMES}
        current = None
        for line in lines[1:]:
            if line.strip() == "---":
                break
            m = field_re.match(line.strip())
            if m:
                current = m.group(1)
                inline = m.group(2).strip()
                if inline:
                    fields[current].append(inline)
                continue
            if current:
                fields[current].append(line)
        slide = {
            "title": title,
            "disposition": "\n".join(fields["Disposition"]).strip(),
            "timing": "\n".join(fields["Segment / timing"]).strip(),
            "body": "\n".join(fields["Contenu affiché"]).strip("\n").replace("`", ""),  # pas de balisage Markdown à l'écran
            "figures": _parse_figures("\n".join(fields["Figure(s)"]), title),
            "credit": "\n".join(fields["Crédit"]).strip().replace("`", ""),
            "notes": "\n".join(fields["Notes d'orateur"]).strip("\n"),
            "rappel": "\n".join(fields["Rappel"]).strip("\n"),
            "figure_commentee": "\n".join(fields["Figure commentée"]).strip("\n"),
            "comparaison": "\n".join(fields["Comparaison"]).strip("\n"),
            "exemple": "\n".join(fields["Exemple"]).strip("\n"),
            "progression": "\n".join(fields["Progression"]).strip("\n"),
        }
        slides.append(slide)
    return slides

_ATTRIBUTION_RE = re.compile(
    r"auteur\s*:\s*([^,]+?)\s*,\s*titre\s*:\s*([^,]+?)\s*,\s*source\s*:\s*([^,]+?)\s*,\s*année\s*:\s*(\d{4})",
    re.IGNORECASE,
)

def _parse_figures(text, titre_diapo="?"):
    """Extrait les chemins d'image + licence depuis les lignes
    `` `Images/....png` — licence: libre `` ou
    `` `Images/....png` — licence: restreint — auteur: X, titre: Y, source: Z, année: NNNN ``.

    `TD-Helice-Marine` range sa galerie sous `Helice/Images/galerie/`, pas `Images/` à
    la racine -- la regex accepte les deux préfixes, résolution toujours relative à la
    racine du dépôt (`HERE/..`).

    GARDE 1 (LOT 4, consigne du 18/09 "Consolidee_Figures-et-variante-Vega") : une figure
    sans `licence:` explicite, ou une figure `restreint` sans les QUATRE champs
    d'attribution complets, fait ÉCHOUER la génération -- jamais un défaut silencieux vers
    "libre" (qui publierait par erreur), jamais une attribution partielle acceptée.
    """
    figures = []
    for line in text.split("\n"):
        m = re.search(r"`((?:Helice/)?Images/[^`]+\.png)`", line)
        if not m:
            continue
        rel = m.group(1)
        path = os.path.normpath(os.path.join(HERE, "..", rel))
        lm = re.search(r"licence\s*:\s*(libre|restreint)", line, re.IGNORECASE)
        if not lm:
            sys.exit(f"Diapo « {titre_diapo} » : figure {rel} sans `licence:` déclarée -- "
                      f"chaque figure doit porter `licence: libre` ou `licence: restreint` "
                      f"(GARDE 1, consigne du 18/09).")
        licence = lm.group(1).lower()
        attribution = None
        if licence == "restreint":
            am = _ATTRIBUTION_RE.search(line)
            if not am:
                sys.exit(f"Diapo « {titre_diapo} » : figure {rel} déclarée `licence: restreint` "
                          f"SANS attribution complète (auteur, titre, source, année tous les "
                          f"quatre requis) -- GARDE 1, consigne du 18/09. Corriger la ligne "
                          f"`Figure(s)` de cette diapo avant de régénérer.")
            attribution = {
                "auteur": am.group(1).strip(),
                "titre": am.group(2).strip(),
                "source": am.group(3).strip(),
                "annee": am.group(4).strip(),
            }
        figures.append({"path": path, "rel": rel, "licence": licence, "attribution": attribution})
    return figures

def _parse_comparaison(text):
    """Découpe le champ `**Comparaison** :` en quatre textes (en-tête A, corps A, en-tête B, corps B)."""
    a_head = a_body = b_head = b_body = ""
    current = None
    for line in text.split("\n"):
        m = re.match(r"^([AB])\s*—\s*(.*)$", line.strip())
        if m:
            current = m.group(1)
            if current == "A":
                a_head = m.group(2).strip()
            else:
                b_head = m.group(2).strip()
            continue
        if current == "A":
            a_body = (a_body + "\n" + line).strip("\n") if a_body else line
        elif current == "B":
            b_body = (b_body + "\n" + line).strip("\n") if b_body else line
    return a_head, a_body.strip(), b_head, b_body.strip()

def _parse_progression(text):
    """Découpe le champ `**Progression** :` — `actif: <n>`, jusqu'à 4 cartes `<n> — titre` suivies de
    leur description, et `liaison: <texte>`. Format choisi pour rester lisible en Markdown brut, sur le
    modèle de `_parse_comparaison` (LOT F, audit charte 12/09)."""
    actif = None
    liaison = ""
    cards = []
    current_title = None
    current_desc = []
    for raw in text.split("\n"):
        line = raw.strip()
        m_actif = re.match(r"^actif\s*:\s*(\d+)\s*$", line, re.IGNORECASE)
        m_liaison = re.match(r"^liaison\s*:\s*(.*)$", line, re.IGNORECASE)
        m_card = re.match(r"^(\d+)\s*—\s*(.*)$", line)
        if m_actif:
            actif = int(m_actif.group(1))
        elif m_liaison:
            if current_title is not None:
                cards.append((current_title, "\n".join(current_desc).strip()))
                current_title, current_desc = None, []
            liaison = m_liaison.group(1).strip()
        elif m_card:
            if current_title is not None:
                cards.append((current_title, "\n".join(current_desc).strip()))
            current_title, current_desc = m_card.group(2).strip(), []
        elif current_title is not None and line:
            current_desc.append(line)
    if current_title is not None:
        cards.append((current_title, "\n".join(current_desc).strip()))
    return actif, cards[:4], liaison

def _parse_table(body_text):
    """Parse un tableau Markdown en liste de lignes (chaque ligne = liste de cellules)."""
    rows = []
    for line in body_text.split("\n"):
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(re.fullmatch(r"-+", c) for c in cells):
            continue  # ligne de séparation
        rows.append(cells)
    return rows

# ---- Remplissage des placeholders -------------------------------------------------------------------

def _find_layout(prs, name):
    for layout in prs.slide_layouts:
        if layout.name.strip().lower() == name.strip().lower():
            return layout
    return None

def _placeholders_by_type(slide, ph_type):
    return [ph for ph in slide.placeholders if ph.placeholder_format.type == ph_type]

def _ph_by_idx(slide, idx):
    for ph in slide.placeholders:
        if ph.placeholder_format.idx == idx:
            return ph
    return None

def _fill_text(ph, text):
    ph.text_frame.text = text

def _remove_placeholder(ph):
    ph._element.getparent().remove(ph._element)

def _fill_table(slide, ph, rows):
    if not rows:
        return
    n_rows, n_cols = len(rows), max(len(r) for r in rows)
    ph_height = ph.height
    if hasattr(ph, "insert_table"):
        table = ph.insert_table(rows=n_rows, cols=n_cols).table
    else:
        left, top, width, height = ph.left, ph.top, ph.width, ph.height
        gframe = slide.shapes.add_table(n_rows, n_cols, left, top, width, height)
        table = gframe.table
        _remove_placeholder(ph)
    for i, row in enumerate(rows):
        for j in range(n_cols):
            table.cell(i, j).text = row[j] if j < len(row) else ""

    # Remplissage direct à la charte ENSM (LOT 4, 18/09) -- voir le commentaire sur
    # _TEAL/_PALE ci-dessus : `ppt/tableStyles.xml` du gabarit ne définit aucun style,
    # ne JAMAIS compter sur `table.first_row`/`table.horz_banding` (ils pointent ce
    # style cassé) -- désactivés explicitement, chaque cellule reçoit sa couleur ici.
    table.first_row = False
    table.horz_banding = False
    header_is_empty = all(not c.strip() for c in rows[0])
    font_pt = 14 if n_rows <= 5 else 11 if n_rows <= 8 else 9
    row_height = max(int(ph_height / n_rows), Pt(1))
    for i, row in enumerate(table.rows):
        row.height = row_height
        is_header = (i == 0) and not header_is_empty
        for cell in row.cells:
            cell.margin_top = cell.margin_bottom = Pt(1)
            cell.margin_left = cell.margin_right = Pt(3)
            cell.fill.solid()
            cell.fill.fore_color.rgb = _TEAL if is_header else (_PALE if i % 2 == 0 else _WHITE)
            for para in cell.text_frame.paragraphs:
                for run in para.runs:
                    run.font.size = Pt(font_pt)
                    run.font.color.rgb = _WHITE if is_header else _MARINE
                    if is_header:
                        run.font.bold = True

def _fill_picture(slide, ph, path):
    # Toujours ajuster DANS le cadre en gardant les proportions. `insert_picture` de python-pptx RECADRE l'image pour remplir le
    # placeholder : constaté le 20/09 sur le rendu de S03 (axes, légendes et titres de figures coupés).
    from PIL import Image
    with Image.open(path) as im:
        iw, ih = im.size
    ratio = iw / ih
    box_w, box_h = ph.width, ph.height
    w, h = box_w, box_w / ratio
    if h > box_h:
        h, w = box_h, box_h * ratio
    left = ph.left + (box_w - w) // 2
    top = ph.top + (box_h - h) // 2
    slide.shapes.add_picture(path, int(left), int(top), width=int(w), height=int(h))
    _remove_placeholder(ph)

def _notes(slide, text):
    if text:
        slide.notes_slide.notes_text_frame.text = text

def build_slide(prs, s, avec_notes=True, variante_figures="public"):
    layout = _find_layout(prs, s["disposition"])
    if layout is None:
        sys.exit(f"Diapo « {s['title']} » : disposition « {s['disposition']} » absente du gabarit "
                  f"{TEMPLATE}. Dispositions attendues : Couverture, Section, Accroche, Revelation, "
                  f"Figure, DeuxFigures, Tableau, Cloture, Corps, Rappel, FigureCommentee, "
                  f"Comparaison, Exemple (voir _Setup/NOTE_GABARIT_PPTX.md).")

    slide = prs.slides.add_slide(layout)
    titles = _placeholders_by_type(slide, PP_PLACEHOLDER.TITLE)
    bodies = (_placeholders_by_type(slide, PP_PLACEHOLDER.BODY)
              + _placeholders_by_type(slide, PP_PLACEHOLDER.SUBTITLE))
    objects = _placeholders_by_type(slide, PP_PLACEHOLDER.OBJECT)
    pictures = _placeholders_by_type(slide, PP_PLACEHOLDER.PICTURE) or list(objects)
    tables = _placeholders_by_type(slide, PP_PLACEHOLDER.TABLE) or list(objects)

    body_lines = [l for l in s["body"].split("\n") if l.strip() and not l.strip().startswith("|")]
    disp_lower = s["disposition"].lower()

    if disp_lower == "tableau":
        if not tables:
            sys.exit(f"Diapo « {s['title']} » (Tableau) : aucun placeholder TABLE ni CONTENU dans le "
                      f"gabarit.")
        if titles and body_lines:
            _fill_text(titles[0], body_lines[0])
        _fill_table(slide, tables[0], _parse_table(s["body"]))
    elif disp_lower == "rappel":
        if titles and body_lines:
            _fill_text(titles[0], body_lines[0])
        if bodies:
            _fill_text(bodies[0], s["rappel"])
        if len(bodies) > 1 and s["timing"]:
            _fill_text(bodies[1], s["timing"])
    elif disp_lower == "figurecommentee":
        if titles and body_lines:
            _fill_text(titles[0], body_lines[0])
        if bodies:
            _fill_text(bodies[0], s["figure_commentee"])
    elif disp_lower == "comparaison":
        if titles and body_lines:
            _fill_text(titles[0], body_lines[0])
        a_head, a_body, b_head, b_body = _parse_comparaison(s["comparaison"])
        for ph, text in zip(bodies, [a_head, a_body, b_head, b_body]):
            _fill_text(ph, text)
    elif disp_lower == "exemple":
        if titles and body_lines:
            _fill_text(titles[0], body_lines[0])
        if bodies:
            _fill_text(bodies[0], s["exemple"])
    elif disp_lower == "progression":
        # Contrat LOT F (audit charte 12/09) : 4 couples carte(idx 10-13)/pastille(idx 20-23) à
        # géométrie FIXE (posée par le gabarit, jamais recalculée ici) + 1 ligne de liaison (idx 14).
        # Seuls la carte et la pastille de l'index `actif` reçoivent un remplissage -- exception bornée
        # au §4 de la consigne, voir docstring de `make_placeholder` dans generer_gabarit_ENSM_cours.py.
        if titles and body_lines:
            _fill_text(titles[0], body_lines[0])
        actif, cards, liaison = _parse_progression(s["progression"])
        for i in range(4):
            card_ph = _ph_by_idx(slide, 10 + i)
            pastille_ph = _ph_by_idx(slide, 20 + i)
            if i < len(cards):
                titre_i, desc_i = cards[i]
                _fill_text(card_ph, f"{titre_i}\n{desc_i}" if desc_i else titre_i)
                _fill_text(pastille_ph, str(i + 1))
                if actif == i + 1:
                    card_ph.fill.solid(); card_ph.fill.fore_color.rgb = _MARINE
                    for para in card_ph.text_frame.paragraphs:
                        for run in para.runs:
                            run.font.color.rgb = _WHITE
                    pastille_ph.fill.solid(); pastille_ph.fill.fore_color.rgb = _CORAIL
            else:
                # Moins de 4 séances dans cette source (ex. TD-Helice-Marine, 3 séances) : le couple
                # inutilisé se NEUTRALISE, jamais ne se retire -- géométrie des autres cartes inchangée
                # (pas de recentrage/redimensionnement, réserve du §3 de la consigne LOT F). PAS
                # `_remove_placeholder` ici : constaté à l'écran (LOT F, pas au XML seul) qu'un
                # placeholder ABSENT de la diapositive fait retomber LibreOffice sur le rendu du
                # placeholder de la DISPOSITION -- texte d'invite ("Séance 4 — intitulé...") et fond
                # compris, SUPERPOSÉ à toute tentative de contenu propre à la diapositive. Repli sûr
                # pour PIC/TBL ailleurs dans ce fichier uniquement parce que leur texte d'invite de
                # disposition est vide ; ici il ne l'est pas (LAYOUTS, generer_gabarit_ENSM_cours.py).
                # PAS `fill.background()` (`<a:noFill/>`) non plus, en dépit des apparences : constaté
                # à l'écran que `noFill` déclenche EXACTEMENT le même repli de superposition sur un
                # placeholder qui porte un `prstGeom` personnalisé (roundRect/ellipse) -- deux voies
                # différentes vers le même défaut LibreOffice, isolées l'une de l'autre par test. Seul
                # un remplissage SOLIDE (blanc, confondu avec le fond de la diapositive) laisse
                # LibreOffice utiliser le contenu de LA diapositive sans repli : c'est la même famille
                # d'opération que le remplissage MARINE de la carte active, jamais une géométrie.
                _fill_text(card_ph, "")
                card_ph.fill.solid(); card_ph.fill.fore_color.rgb = _WHITE
                _fill_text(pastille_ph, "")
                pastille_ph.fill.solid(); pastille_ph.fill.fore_color.rgb = _WHITE
        liaison_ph = _ph_by_idx(slide, 14)
        if liaison_ph is not None:
            _fill_text(liaison_ph, liaison)
    else:
        if titles and body_lines:
            _fill_text(titles[0], body_lines[0])
        if bodies and len(body_lines) > 1:
            _fill_text(bodies[0], "\n".join(body_lines[1:]))

    attribution_a_imprimer = []
    if s["figures"]:
        # GARDE 2 (LOT 4, consigne du 18/09) : la sortie PUBLIQUE (GitHub) ne doit JAMAIS
        # embarquer une figure `restreint` -- le générateur ÉCHOUE plutôt que de l'omettre
        # en silence (un silence qui masquerait le problème au lieu de forcer une décision :
        # reclasser la figure, ou la retirer explicitement de la source).
        if variante_figures == "public":
            restreintes = [fig["rel"] for fig in s["figures"] if fig["licence"] == "restreint"]
            if restreintes:
                sys.exit(f"Diapo « {s['title']} » : figure(s) `restreint` dans une sortie "
                          f"PUBLIQUE -- INTERDIT (GARDE 2, consigne du 18/09) : {restreintes}. "
                          f"Utiliser la variante `vega` pour cette diapo, ou reclasser la "
                          f"figure `libre` si elle peut l'être.")
        if len(pictures) < len(s["figures"]):
            sys.exit(f"Diapo « {s['title']} » : {len(s['figures'])} figure(s) déclarée(s) mais "
                      f"{len(pictures)} placeholder(s) IMAGE/CONTENU dans le gabarit.")
        for ph, fig in zip(pictures, s["figures"]):
            if not os.path.isfile(fig["path"]):
                sys.exit(f"Diapo « {s['title']} » : figure introuvable — {fig['path']}")
            _fill_picture(slide, ph, fig["path"])
            if fig["licence"] == "restreint" and variante_figures == "vega":
                a = fig["attribution"]
                attribution_a_imprimer.append(
                    f"{fig['rel']} : © {a['auteur']}, « {a['titre']} », {a['source']}, {a['annee']}"
                )

    credit_texte = s["credit"]
    if attribution_a_imprimer:
        bloc = "\n".join(attribution_a_imprimer)
        credit_texte = f"{credit_texte}\n{bloc}" if credit_texte else bloc
    if credit_texte and disp_lower not in ("rappel", "comparaison"):
        body_ph_used_for_text = bool(bodies) and len(body_lines) > 1
        if len(bodies) > 1:
            credit_ph = bodies[1]
        elif bodies and not body_ph_used_for_text:
            credit_ph = bodies[0]
        else:
            credit_ph = None
        if credit_ph is not None:
            _fill_text(credit_ph, credit_texte)
        else:
            sys.exit(f"Diapo « {s['title']} » : crédit déclaré (« {credit_texte} ») mais aucun "
                      f"placeholder CORPS/SOUS-TITRE disponible pour l'afficher dans le gabarit.")

    if avec_notes:
        _notes(slide, s["notes"])
    return slide

OUT_ENSEIGNANT = os.path.join(HERE, f"{STEM}_enseignant.pptx")

def _construire(slides, avec_notes, variante_figures="public"):
    """Presentation() indépendante par exemplaire -- pas de notes_slide créé du tout sur
    l'exemplaire public (pas une suppression après coup : _notes() n'est simplement jamais
    appelée), donc aucune part `notesSlide` dans le zip, pas seulement un texte vidé."""
    prs = Presentation(TEMPLATE)
    for s in slides:
        build_slide(prs, s, avec_notes=avec_notes, variante_figures=variante_figures)
    return prs

def build():
    if not os.path.isfile(TEMPLATE):
        sys.exit(
            f"Gabarit introuvable : {TEMPLATE}\n"
            "Synchronisez le noyau d'abord (voir _Setup/SYNCHRONISER.md)."
        )
    if not os.path.isfile(SLIDES_MD):
        sys.exit(f"Source introuvable : {SLIDES_MD} — écrivez-la d'abord (une diapo par bloc).")
    with open(SLIDES_MD, encoding="utf-8") as f:
        has_rattrapage = "<!-- RATTRAPAGE G1-G2 -->" in f.read()

    slides = parse_slides(SLIDES_MD)  # keep_rattrapage=False par défaut -- variante canonique

    # GARDE 2 (LOT 4, consigne du 18/09 "Consolidee_Figures-et-variante-Vega") : vérifiée
    # ICI, EN AMONT de toute construction -- pas laissée à build_slide (un sys.exit() lancé
    # au milieu de la construction publique tuerait tout le PROCESSUS Python, empêchant
    # même la construction légitime de `vega`/`enseignant` pour ce même deck). Un deck qui
    # emprunte une figure a droit à `vega` et `enseignant` ; il n'a pas droit à `public`.
    diapos_restreintes = {
        s["title"]: [fig["rel"] for fig in s["figures"] if fig["licence"] == "restreint"]
        for s in slides if any(fig["licence"] == "restreint" for fig in s["figures"])
    }
    public_interdit = bool(diapos_restreintes)

    if public_interdit:
        # Retire un exemplaire public PÉRIMÉ déjà sur disque (construit avant qu'une
        # figure ne soit reclassée `restreint`) -- le laisser en place serait pire que
        # ne rien générer : un fichier qui a l'air à jour mais embarque encore une image
        # qui ne devrait plus jamais être publique (voir verifier_pptx_restreint.sh, le
        # contrôle indépendant qui détecte précisément ce cas par le contenu).
        if os.path.isfile(OUT):
            os.remove(OUT)
            print(f"SUPPRIMÉ -- {OUT} (périmé, construit avant reclassement `restreint`).", file=sys.stderr)
        print(f"REFUS -- sortie PUBLIQUE (GARDE 2) : {sum(len(v) for v in diapos_restreintes.values())} "
              f"figure(s) `restreint` trouvée(s), {OUT} NON généré :", file=sys.stderr)
        for titre, figs in diapos_restreintes.items():
            print(f"  diapo « {titre} » : {figs}", file=sys.stderr)
        print("  -> utiliser Seances/<STEM>_vega.pptx (espace fermé) pour ce deck.", file=sys.stderr)
    else:
        # Exemplaire PUBLIC (défaut, nom court, celui qui part sur GitHub) : AUCUNE part
        # notesSlide -- les notes de conduite sont des notes de préparation pour
        # l'enseignant, pas un contenu à donner aux étudiants (LOT B, audit charte 11/09).
        prs_public = _construire(slides, avec_notes=False, variante_figures="public")
        prs_public.save(OUT)
        print(f"OK -> {OUT}  ({len(slides)} diapositives, public/GitHub -- sans notes de conduite, aucune figure restreinte)")

    # Exemplaire enseignant : notes de conduite incluses ET toutes les figures (y compris
    # `restreint`, avec attribution imprimée) -- jamais déposé sur Vega ni sur GitHub.
    prs_ens = _construire(slides, avec_notes=True, variante_figures="vega")
    prs_ens.save(OUT_ENSEIGNANT)

    n_notes = sum(1 for s in slides if s["notes"].strip())
    print(f"OK -> {OUT_ENSEIGNANT}  ({n_notes}/{len(slides)} diapositives annotées -- enseignant, jamais publié)")

    # Variante VEGA (LOT 4, consigne du 18/09 "Consolidee_Figures-et-variante-Vega") :
    # espace fermé de l'école -- toutes les figures (attribution imprimée sur chaque
    # `restreint`), sans notes de conduite (reste un support projeté, pas un cours à lire).
    # Construite seulement si la source porte au moins une figure `restreint` : sinon
    # cette variante serait un doublon strict de l'exemplaire public, jamais régénéré
    # (la leçon même du LOT 9 de cette consigne -- deux sorties identiques, l'une des
    # deux finit par diverger sans qu'on s'en rende compte).
    if public_interdit:
        out_vega = os.path.join(HERE, f"{STEM}_vega.pptx")
        prs_vega = _construire(slides, avec_notes=False, variante_figures="vega")
        prs_vega.save(out_vega)
        print(f"OK -> {out_vega}  ({len(slides)} diapositives, Vega (espace fermé) -- "
              f"toutes les figures, attribution imprimée sur chaque figure restreinte)")

    # Variante rattrapage (LOT 5, consigne du 15/09) : uniquement si la source porte le
    # marqueur -- détecté, jamais demandé par argument. Remplace generer_variantes_deck.py.
    # Suppose elle-même un deck public (jamais construite si public_interdit) -- un deck
    # avec rattrapage ET figure restreinte n'existe pas aujourd'hui ; le jour où ça
    # arrivera, il faudra choisir sciemment, pas ajouter un cas ici par anticipation.
    if has_rattrapage and not public_interdit:
        slides_avec = parse_slides(SLIDES_MD, keep_rattrapage=True)
        out_variante = os.path.join(HERE, f"{STEM}_groupes1-2.pptx")
        prs_variante = _construire(slides_avec, avec_notes=False, variante_figures="public")
        prs_variante.save(out_variante)
        print(f"OK -> {out_variante}  ({len(slides_avec)} diapositives, public, "
              f"AVEC le bloc rattrapage -- source contient le marqueur)")

    if public_interdit:
        print(f"ÉCHEC -- {OUT} non généré (GARDE 2, figure(s) restreinte(s) ci-dessus). "
              f"{OUT_ENSEIGNANT} et la variante vega, eux, sont à jour.", file=sys.stderr)
        sys.exit(1)

    print(f"Contrôle obligatoire : _Setup/verifier_deck.sh {OUT}")

if __name__ == "__main__":
    build()
