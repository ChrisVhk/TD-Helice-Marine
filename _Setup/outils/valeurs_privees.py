"""Accès aux valeurs-réponses du TD, conservées HORS de ce dépôt public (document enseignant).

Chemin : variable d'environnement VALEURS_COULISSES, sinon ~/.config/ensm-td-helice/valeurs_reponses.json
(sur la machine de l'enseignant, lien vers le fichier du dépôt privé).
Si le fichier est absent (clone public seul), les outils qui en dépendent s'arrêtent avec un
message explicite, code de sortie 3 : ce n'est pas une erreur du dépôt, c'est un contrôle réservé
à l'enseignant.
En ligne de commande : `python3 valeurs_privees.py patterns` écrit les motifs périmés, un par ligne.
"""
import json
import os
import sys
from pathlib import Path

DEFAUT = Path.home() / ".config/ensm-td-helice/valeurs_reponses.json"


def chemin():
    return Path(os.environ.get("VALEURS_COULISSES", DEFAUT))


def charger_privees():
    p = chemin()
    if not p.is_file():
        sys.stderr.write(
            "Fichier de valeurs des coulisses privées absent : %s\n"
            "Ce contrôle compare à des valeurs enseignant, non distribuées avec ce dépôt public. "
            "Indiquez le fichier par la variable VALEURS_COULISSES, ou lancez-le depuis la machine de l'enseignant.\n" % p)
        sys.exit(3)
    return json.loads(p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    if sys.argv[1:] == ["patterns"]:
        print("\n".join(charger_privees()["patterns_perimes"]))
    else:
        sys.exit("usage : valeurs_privees.py patterns")
