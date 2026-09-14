# Seances/ — decks PPTX de séance

Chaque séance : une source `S<NN>_Slides.md` (une diapo = un bloc `## Diapo <N> — <titre>`,
voir `_Setup/NOTE_GABARIT_PPTX.md` pour le contrat de champs/dispositions) + son générateur
`generer_pptx_S<NN>.py` (copié puis adapté depuis `_Setup/MODELE_generer_pptx_seance.py`,
jamais exécuté directement depuis `_Setup/`).

```
pip install python-pptx pillow   # une fois, dans un venv
python3 Seances/generer_pptx_S<NN>.py
_Setup/verifier_deck.sh Seances/S<NN>.pptx   # regarder le rendu avant toute livraison
```

## `S00_Intro-CFD-Helice_Slides.md` — attention, dépend de la galerie régénérée

Ce deck d'introduction s'appuie sur les huit images de
`Helice/Images/galerie/*.png` (générées par `_Setup/outils/rendre_vues_helice.py`). **Ces
PNG sont gitignorés** (`Helice/.gitignore`) — seuls le script qui les produit et
`Helice/Images/galerie/LEGENDES.md` sont suivis.

**Conséquence directe (INV-11)** : sur un autre poste ou après un changement de compte, ce
deck n'est PAS régénérable tel quel — `Seances/generer_pptx_S00.py` échouera (« figure
introuvable ») tant que la galerie n'a pas été reconstruite d'abord :

```
pvbatch _Setup/outils/rendre_vues_helice.py --cas case_kEpsilon --time 0.06
python3 Seances/generer_pptx_S00.py
_Setup/verifier_deck.sh Seances/S00.pptx
```

Le `.pptx` produit, lui, n'est pas versionné non plus (artefact régénérable, comme tous les
decks de ce dossier) — seuls `S00_Intro-CFD-Helice_Slides.md` et `generer_pptx_S00.py` le
sont.

## Divergence de convention connue — chemins d'image

`generer_pptx_S00.py` accepte des chemins `Helice/Images/...png` dans le champ
`**Figure(s)**`, en plus de `Images/...png` (regex adaptée localement, voir commentaire dans
le fichier) — `TD-Helice-Marine` range sa galerie sous `Helice/`, contrairement à un dépôt de
cours autonome où `Images/` est un sibling direct de `Seances/`. N'affecte que ce script ;
les autres `generer_pptx_S0N.py` du dossier gardent la regex d'origine du modèle.
