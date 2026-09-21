# Seances/ — génération des decks de séance

Ce dossier ne contient que le **générateur** des decks projetés, `generer_pptx_seance.py`. Les decks eux-mêmes (`S01`, `S02`, `S03`) sont
distribués par Moodle/Vega, pas par ce dépôt. Leurs **sources** (`S<NN>_Slides.md`) sont conservées par l'enseignant et ne sont pas suivies
ici (voir `.gitignore`) : elles portent les notes de conduite du présentateur.

## Convention

1. **Source** : un fichier `S<NN>_Slides.md` par séance (une diapo = un bloc `## Diapo <N> — <titre>`, contrat de champs et de
   dispositions dans `_Setup/NOTE_GABARIT_PPTX.md`). C'est le seul endroit où l'on édite un deck à la main.
2. **Généré** : `S<NN>.pptx` (version déposée sur Vega, sans notes) et `S<NN>_enseignant.pptx` (avec notes, jamais déposée). Ne jamais éditer
   un `.pptx` à la main : il serait écrasé à la prochaine régénération et la source resterait fausse.
3. **Non suivi** : `Seances/*.pptx`, `Seances/*.pdf`, `Seances/_rendu/` (générés) et les sources `S<NN>_Slides.md`.
4. **Régénérer** (poste de l'enseignant) :
   ```
   pip install python-pptx pillow   # une fois, dans un venv
   python3 Seances/generer_pptx_seance.py S<NN>
   _Setup/verifier_deck.sh Seances/S<NN>.pptx   # regarder le rendu avant toute livraison
   ```
5. **Images** : `Helice/Images/*.png` (convention `FIG-fon-s7-*`) est SUIVI et destiné aux étudiants ; `Helice/Images/galerie/` est un atelier
   entièrement gitignoré. Toute image citée par un support destiné aux étudiants doit vivre sous `Images/`, jamais sous `galerie/` : un PNG
   gitignoré est invisible pour un étudiant qui clone.

## Tableaux

`_Setup/TEMPLATE_ENSM_cours.pptx` a un `ppt/tableStyles.xml` vide : le générateur applique la charte ENSM **cellule par cellule**
(`_fill_table`, constantes `_TEAL`/`_PALE`/`_MARINE`/`_WHITE`). Un changement de charte sur les tableaux se fait dans ces constantes, pas
dans le gabarit ; il faut ensuite régénérer les decks.
