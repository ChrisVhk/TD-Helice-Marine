#!/usr/bin/env python3
"""Recale les exclusions de `verifier_valeurs_perimees.sh` après l'édition d'un document.

PIÈGE CONNU (20/09) : les exclusions du falsificateur sont indexées par NUMÉRO DE LIGNE (`"fichier:ligne"`).
Toute insertion ou suppression dans un fichier décale toutes les lignes suivantes : le garde passe ROUGE
(ou pire, exclut la mauvaise ligne). Cet outil compare l'ancienne et la nouvelle version du fichier
(difflib) et remappe chaque exclusion dont la ligne est restée IDENTIQUE ; il SIGNALE, sans les remapper,
celles dont la ligne a été modifiée (à revoir à la main : la raison de l'exclusion tient-elle encore ?).

Usage :
    python3 _Setup/outils/caler_exclusions.py FICHIER [--avant COPIE_AVANT] [--appliquer]
FICHIER : chemin relatif à la racine du dépôt (ex. Helice/docs/PARAMETRES_CAS.md).
Version « avant » : `git show HEAD:FICHIER` par défaut ; pour un fichier gitignoré, une copie prise avant
l'édition (`--avant`). Sans `--appliquer`, ne modifie rien et affiche le plan.
"""
import argparse
import difflib
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GARDE = ROOT / "_Setup" / "outils" / "verifier_valeurs_perimees.sh"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("fichier")
    ap.add_argument("--avant")
    ap.add_argument("--appliquer", action="store_true")
    a = ap.parse_args()

    apres = (ROOT / a.fichier).read_text(encoding="utf-8").split("\n")
    if a.avant:
        avant = Path(a.avant).read_text(encoding="utf-8").split("\n")
    else:
        avant = subprocess.run(["git", "show", f"HEAD:{a.fichier}"], cwd=ROOT, capture_output=True, text=True,
                               check=True).stdout.split("\n")
    ops = difflib.SequenceMatcher(None, avant, apres, autojunk=False).get_opcodes()

    def nouvelle(n):  # n : numéro de ligne 1-based dans l'ancienne version
        for tag, i1, i2, j1, j2 in ops:
            if i1 <= n - 1 < i2:
                return (j1 + (n - 1 - i1) + 1, None) if tag == "equal" else (None, tag)
        return (None, "hors fichier")

    texte = GARDE.read_text(encoding="utf-8")
    motif = re.compile(r'"' + re.escape(a.fichier) + r':(\d+)"')
    modifs, a_revoir = [], []
    for m in motif.finditer(texte):
        n = int(m.group(1))
        nv, raison = nouvelle(n)
        if nv is None:
            a_revoir.append((n, raison))
        elif nv != n:
            modifs.append((n, nv))
    print(f"{a.fichier} : {len(list(motif.finditer(texte)))} exclusion(s) ; {len(modifs)} à décaler ; {len(a_revoir)} à REVOIR")
    for n, nv in modifs:
        print(f"  {n} -> {nv}")
    for n, raison in a_revoir:
        print(f"  {n} : ligne {raison} -- À REVOIR À LA MAIN (raison de l'exclusion encore valable ?)")
    if a.appliquer and modifs:
        def rempl(m):
            n = int(m.group(1))
            nv, _ = nouvelle(n)
            return f'"{a.fichier}:{nv}"' if nv else m.group(0)
        GARDE.write_text(motif.sub(rempl, texte), encoding="utf-8")
        print("  appliqué.")


if __name__ == "__main__":
    main()
