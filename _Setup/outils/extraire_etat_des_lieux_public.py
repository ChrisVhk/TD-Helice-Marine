#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère `Helice/docs/ETAT-DES-LIEUX.md` (publique, suivie) depuis
`Helice/docs/ETAT-DES-LIEUX_Enseignant.md` (source complète, gitignorée).

Ne JAMAIS éditer `ETAT-DES-LIEUX.md` à la main -- les deux fichiers divergeraient
silencieusement, sans qu'aucun outil ne le signale. Ce script est la SEULE voie
d'écriture de la version publique. Idempotent : le relancer sans changer la source
ne change pas la sortie (LOT 6, consigne du 14/09).

Règle de filtrage (décidée par la consigne du 14/09) :
  - ÉTABLI          : copié intégralement.
  - OÙ ON VA        : copié intégralement.
  - INCERTAIN       : chaque item ne garde que son titre, son champ **Énoncé** et son
                       champ **Trancherait** -- le champ **Détail**, s'il existe, ne
                       passe jamais dans la version publique.

Usage :
    python3 _Setup/outils/extraire_etat_des_lieux_public.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SOURCE = os.path.join(REPO_ROOT, "Helice", "docs", "ETAT-DES-LIEUX_Enseignant.md")
OUT = os.path.join(REPO_ROOT, "Helice", "docs", "ETAT-DES-LIEUX.md")

HEADER = """# État des lieux — TD Hélice marine (version publique)

**Généré depuis la source enseignante par `_Setup/outils/extraire_etat_des_lieux_public.py`
-- ne jamais éditer ce fichier à la main.** Chaque affirmation d'`ÉTABLI` porte sa source
dans la version enseignante (non publiée ici, gitignorée) ; cette version publique reprend
`ÉTABLI` et `OÙ ON VA` intégralement, et d'`INCERTAIN` seulement l'énoncé et le test qui
trancherait -- pas le détail.

---
"""


def _extract_section(text, name, next_names):
    """Isole le texte entre `## <name>` et le prochain `## <next>` de la liste (ou la fin)."""
    start_m = re.search(rf"^## {re.escape(name)}\s*$", text, re.MULTILINE)
    if not start_m:
        sys.exit(f"Section « {name} » introuvable dans {SOURCE}.")
    start = start_m.end()
    end = len(text)
    for other in next_names:
        m = re.search(rf"^## {re.escape(other)}", text[start:], re.MULTILINE)
        if m:
            end = min(end, start + m.start())
    section = text[start:end].strip("\n")
    return re.sub(r"\n+---\s*$", "", section).strip("\n")


def _filter_incertain(block):
    """Découpe le bloc INCERTAIN en items `### <titre>` et ne garde que Énoncé/Trancherait."""
    items = re.split(r"^### ", block, flags=re.MULTILINE)[1:]
    out_items = []
    for item in items:
        lines = item.split("\n")
        titre = lines[0].strip()
        rest = "\n".join(lines[1:])
        enonce_m = re.search(r"\*\*Énoncé\*\*\s*:\s*(.*?)(?=\n\*\*|\Z)", rest, re.DOTALL)
        tranche_m = re.search(r"\*\*Trancherait\*\*\s*:\s*(.*?)(?=\n\*\*|\Z)", rest, re.DOTALL)
        if not enonce_m or not tranche_m:
            sys.exit(f"Item INCERTAIN « {titre} » : champ Énoncé ou Trancherait manquant.")
        enonce = enonce_m.group(1).strip()
        tranche = tranche_m.group(1).strip()
        out_items.append(f"### {titre}\n**Énoncé** : {enonce}\n\n**Trancherait** : {tranche}")
    return "\n\n".join(out_items)


def build():
    if not os.path.isfile(SOURCE):
        sys.exit(f"Source introuvable : {SOURCE} -- rien à générer.")
    with open(SOURCE, encoding="utf-8") as f:
        text = f.read()

    etabli = _extract_section(text, "ÉTABLI", ["INCERTAIN", "OÙ ON VA"])
    incertain_full = _extract_section(text, "INCERTAIN — et ce qui le trancherait",
                                       ["OÙ ON VA"])
    ou_va = _extract_section(text, "OÙ ON VA", [])
    incertain_public = _filter_incertain(incertain_full)

    out_text = (
        HEADER
        + "\n## ÉTABLI\n\n" + etabli
        + "\n\n---\n\n## INCERTAIN — et ce qui le trancherait\n\n" + incertain_public
        + "\n\n---\n\n## OÙ ON VA\n\n" + ou_va
        + "\n"
    )

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(out_text)
    n_items = len(re.findall(r"^### ", incertain_full, re.MULTILINE))
    print(f"OK -> {OUT}")
    print(f"   ÉTABLI copié intégralement, OÙ ON VA copié intégralement, "
          f"{n_items} item(s) INCERTAIN réduits à énoncé + test.")


if __name__ == "__main__":
    build()
