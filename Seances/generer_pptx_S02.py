#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODÈLE documenté — générateur de support PPTX pour une séance (LOT 1, audit charte 07/09).

Ce fichier n'est PAS destiné à être exécuté ici. C'est le point de départ à copier dans
un cours, à renommer, et à adapter s'il le faut. Généralisé depuis
`Cours/EGN-S9_Performances-Navire/Seances/generer_pptx_S00.py` (premier générateur à la
charte, boucle 10) — la logique de remplissage des placeholders est identique et déjà
éprouvée sur cinq séances/dispositions ; seule la résolution des chemins a été rendue
indépendante de la profondeur du dépôt (voir ci-dessous).

## Comment l'utiliser dans un nouveau cours

1. Copier ce fichier dans `Seances/generer_pptx_S<NN>.py` de votre cours (ex.
   `Seances/generer_pptx_S01.py`).
2. Écrire `Seances/S<NN>_Slides.md` à côté (une diapo = un bloc, voir le format ci-dessous).
3. Depuis la racine du dépôt du cours :
   ```
   pip install python-pptx pillow
   python3 Seances/generer_pptx_S<NN>.py
   ```
   Produit DEUX fichiers (LOT B, audit charte 11/09) :
   - `Seances/S<NN>.pptx` — **exemplaire Vega**, sans aucune part `notesSlide`. C'est
     celui qu'on dépose sur Vega ou qu'on projette : les notes d'orateur sont des notes
     de préparation pour l'enseignant, pas un contenu pour les étudiants qui liraient
     le deck en dehors de la séance.
   - `Seances/S<NN>_enseignant.pptx` — même contenu, notes d'orateur incluses. **Jamais
     déposé sur Vega.**
4. **Contrôle obligatoire** avant toute livraison :
   `_Setup/verifier_deck.sh Seances/S<NN>.pptx` — rendu en images, à REGARDER, pas
   seulement généré sans erreur (voir JOURNAL.md ENSM-Enseignement, débordements du 28/08).
   Vérifier aussi l'absence de notes sur l'exemplaire Vega :
   `unzip -l Seances/S<NN>.pptx | grep notesSlide` doit ne rien renvoyer.

## Ce qui rend ce script portable (contrairement à generer_pptx_S00.py littéral)

`generer_pptx_S00.py` suppose `_Setup/` trois niveaux au-dessus de son propre dossier
(`Cours/<UE>/Seances/generer_pptx_S00.py` → `../../../_Setup`) : exact pour le monorepo
`ENSM-Enseignement`, faux pour un dépôt de cours autonome où `Seances/` est à la racine
(`Seances/generer_pptx_S01.py` → `../_Setup`, deux niveaux de moins). Ce modèle **remonte
l'arborescence à la recherche d'un dossier `_Setup/`** contenant le gabarit, plutôt que de
supposer une profondeur fixe — il fonctionne identiquement dans les deux structures, et
dans toute structure intermédiaire. `Images/` reste résolu en `../Images` (sibling de
`Seances/`), ce qui est déjà indépendant de la profondeur.

## Contrat gabarit (inchangé) — treize dispositions, nommées EXACTEMENT ainsi
    Couverture · Section · Accroche · Revelation · Figure · DeuxFigures · Tableau · Cloture ·
    Corps · Rappel · FigureCommentee · Comparaison · Exemple
Voir `_Setup/NOTE_GABARIT_PPTX.md` pour le détail des placeholders par disposition et
`_Setup/specification/INVENTAIRE_DISPOSITIONS_ENSM.md` pour le mapping champ `.md` ↔
disposition. Le format `S<NN>_Slides.md` (une diapo = `## Diapo <N> — <titre>` suivi de
champs `**Disposition**`, `**Segment / timing**`, `**Contenu affiché**`, `**Figure(s)**`,
`**Crédit**`, `**Notes d'orateur**`, terminé par `---`) est identique à celui déjà en
usage — copier un `S00_Slides.md` existant comme gabarit de départ est le chemin le plus
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

# --- À adapter : dérivé du nom de CE fichier une fois copié/renommé -----------------
# generer_pptx_S01.py -> STEM "S01" -> S01_Slides.md en entrée, S01.pptx en sortie.
# Renommez OUT ci-dessous si vous voulez un titre plus parlant (ex. "S01_Introduction.pptx").
_SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0]  # ex. "generer_pptx_S01"
STEM = re.sub(r"^generer_pptx_", "", _SCRIPT_NAME) or "SEANCE"
SLIDES_MD = os.path.join(HERE, f"{STEM}_Slides.md")
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

# ---- Parsing de <STEM>_Slides.md --------------------------------------------------------------------

def parse_slides(path):
    """Découpe le fichier Slides.md en une liste de dicts {title, disposition, body, figures,
    credit, notes, ...}. Un bloc de diapo commence à '## Diapo <N> — <titre>' et se termine au
    '---' suivant (ou à la fin)."""
    with open(path, encoding="utf-8") as f:
        text = f.read()

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
            "body": "\n".join(fields["Contenu affiché"]).strip("\n"),
            "figures": _parse_figures("\n".join(fields["Figure(s)"])),
            "credit": "\n".join(fields["Crédit"]).strip(),
            "notes": "\n".join(fields["Notes d'orateur"]).strip("\n"),
            "rappel": "\n".join(fields["Rappel"]).strip("\n"),
            "figure_commentee": "\n".join(fields["Figure commentée"]).strip("\n"),
            "comparaison": "\n".join(fields["Comparaison"]).strip("\n"),
            "exemple": "\n".join(fields["Exemple"]).strip("\n"),
            "progression": "\n".join(fields["Progression"]).strip("\n"),
        }
        slides.append(slide)
    return slides

def _parse_figures(text):
    """Extrait les chemins d'image depuis les lignes `FIG:... — Images/....png — description`."""
    paths = []
    for line in text.split("\n"):
        m = re.search(r"`(Images/[^`]+\.png)`", line)
        if m:
            rel = m.group(1)
            paths.append(os.path.normpath(os.path.join(HERE, "..", rel)))
    return paths

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

    font_pt = 14 if n_rows <= 5 else 11 if n_rows <= 8 else 9
    row_height = max(int(ph_height / n_rows), Pt(1))
    for row in table.rows:
        row.height = row_height
        for cell in row.cells:
            cell.margin_top = cell.margin_bottom = Pt(1)
            cell.margin_left = cell.margin_right = Pt(3)
            for para in cell.text_frame.paragraphs:
                for run in para.runs:
                    run.font.size = Pt(font_pt)

def _fill_picture(slide, ph, path):
    if hasattr(ph, "insert_picture"):
        ph.insert_picture(path)
        return
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

def build_slide(prs, s, avec_notes=True):
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

    if s["figures"]:
        if len(pictures) < len(s["figures"]):
            sys.exit(f"Diapo « {s['title']} » : {len(s['figures'])} figure(s) déclarée(s) mais "
                      f"{len(pictures)} placeholder(s) IMAGE/CONTENU dans le gabarit.")
        for ph, path in zip(pictures, s["figures"]):
            if not os.path.isfile(path):
                sys.exit(f"Diapo « {s['title']} » : figure introuvable — {path}")
            _fill_picture(slide, ph, path)

    if s["credit"] and disp_lower not in ("rappel", "comparaison"):
        body_ph_used_for_text = bool(bodies) and len(body_lines) > 1
        if len(bodies) > 1:
            credit_ph = bodies[1]
        elif bodies and not body_ph_used_for_text:
            credit_ph = bodies[0]
        else:
            credit_ph = None
        if credit_ph is not None:
            _fill_text(credit_ph, s["credit"])
        else:
            sys.exit(f"Diapo « {s['title']} » : crédit déclaré (« {s['credit']} ») mais aucun "
                      f"placeholder CORPS/SOUS-TITRE disponible pour l'afficher dans le gabarit.")

    if avec_notes:
        _notes(slide, s["notes"])
    return slide

OUT_ENSEIGNANT = os.path.join(HERE, f"{STEM}_enseignant.pptx")

def _construire(slides, avec_notes):
    """Presentation() indépendante par exemplaire -- pas de notes_slide créé du tout sur
    l'exemplaire Vega (pas une suppression après coup : _notes() n'est simplement jamais
    appelée), donc aucune part `notesSlide` dans le zip, pas seulement un texte vidé."""
    prs = Presentation(TEMPLATE)
    for s in slides:
        build_slide(prs, s, avec_notes=avec_notes)
    return prs

def build():
    if not os.path.isfile(TEMPLATE):
        sys.exit(
            f"Gabarit introuvable : {TEMPLATE}\n"
            "Synchronisez le noyau d'abord (voir _Setup/SYNCHRONISER.md)."
        )
    if not os.path.isfile(SLIDES_MD):
        sys.exit(f"Source introuvable : {SLIDES_MD} — écrivez-la d'abord (une diapo par bloc).")
    slides = parse_slides(SLIDES_MD)

    # Exemplaire Vega (défaut, nom court) : AUCUNE part notesSlide -- les notes d'orateur
    # sont des notes de préparation pour l'enseignant, pas un contenu à donner aux
    # étudiants qui liraient le deck sur Vega (LOT B, audit charte 11/09).
    prs_vega = _construire(slides, avec_notes=False)
    prs_vega.save(OUT)

    # Exemplaire enseignant : notes d'orateur incluses, JAMAIS déposé sur Vega.
    prs_ens = _construire(slides, avec_notes=True)
    prs_ens.save(OUT_ENSEIGNANT)

    n_notes = sum(1 for s in slides if s["notes"].strip())
    print(f"OK -> {OUT}  ({len(slides)} diapositives, Vega -- sans notes d'orateur)")
    print(f"OK -> {OUT_ENSEIGNANT}  ({n_notes}/{len(slides)} diapositives annotées -- enseignant, jamais sur Vega)")
    print(f"Contrôle obligatoire : _Setup/verifier_deck.sh {OUT}")

if __name__ == "__main__":
    build()
