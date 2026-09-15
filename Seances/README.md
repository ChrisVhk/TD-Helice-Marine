# Seances/ — decks PPTX de séance

## Convention (LOT 6, consigne du 15/09)

1. **Source** : un fichier `S<NN>_Slides.md` par séance (une diapo = un bloc
   `## Diapo <N> — <titre>`, voir `_Setup/NOTE_GABARIT_PPTX.md` pour le contrat de
   champs/dispositions). C'est le seul endroit qu'on édite à la main.
2. **Généré** : `S<NN>.pptx` (Vega, sans notes), `S<NN>_enseignant.pptx` (avec notes,
   jamais déposé sur Vega), et pour `S02` uniquement (détecté automatiquement, voir
   plus bas) `S02_groupes1-2.pptx`. Ne JAMAIS éditer un `.pptx` à la main — il serait
   écrasé sans préavis à la prochaine régénération, et la source resterait fausse.
3. **Ignoré** (`Seances/*.pptx`, `Seances/_rendu/` dans `.gitignore`) : tous les
   `.pptx` ci-dessus, et le rendu de contrôle image-par-image. Rien de généré n'est
   suivi — seuls les fichiers `_Slides.md` et le générateur le sont.
4. **Régénérer** :
   ```
   pip install python-pptx pillow   # une fois, dans un venv
   python3 Seances/generer_pptx_seance.py S<NN>
   _Setup/verifier_deck.sh Seances/S<NN>.pptx   # regarder le rendu avant toute livraison
   ```
5. **Dépendance à la galerie (INV-11)** — `S00_Intro-CFD-Helice_Slides.md` et
   `S03_Arborescence-et-perspective_Slides.md` référencent des images de
   `Helice/Images/galerie/*.png` (produites par `_Setup/outils/rendre_vues_helice.py`).
   **Ces PNG sont gitignorés** (`Helice/.gitignore`) — seuls le script qui les produit
   et `Helice/Images/galerie/LEGENDES.md` sont suivis. Conséquence directe : sur un
   autre poste ou après un changement de compte, ces deux decks ne sont PAS
   régénérables tel quels — `generer_pptx_seance.py` échouera (« figure introuvable »)
   tant que la galerie n'a pas été reconstruite d'abord :
   ```
   pvbatch _Setup/outils/rendre_vues_helice.py --cas case_kEpsilon --time 0.06
   python3 Seances/generer_pptx_seance.py S00
   ```

## Un seul générateur, paramétré par séance (LOT 4, 15/09)

`generer_pptx_S00.py`/`S02.py`/`S03.py` (trois copies du même modèle) ont été
remplacés par **`Seances/generer_pptx_seance.py`**, un script unique qui prend le
numéro de séance en argument :
```
python3 Seances/generer_pptx_seance.py S00
python3 Seances/generer_pptx_seance.py S02
python3 Seances/generer_pptx_seance.py S03
```
Diff des trois anciens fichiers avant suppression (LOT 4) : aucune divergence
FONCTIONNELLE trouvée — seulement (a) `S00`/`S03` ont un nom de source qui ne suit pas
la convention `S<NN>_Slides.md` (géré par `SLIDES_MD_OVERRIDE` dans le script unique,
un nom de fichier historique, pas un comportement différent), et (b) le
retrait/inclusion du bloc rattrapage, qui ne concernait que `S02` (voir ci-dessous).
Les trois decks régénérés par le script unique reproduisent EXACTEMENT le contenu des
trois anciens scripts (vérifié par diff après désarchivage des trois paires
avant/après) — aucune régression.

## Une seule logique de variantes (LOT 5, 15/09)

Deux mécanismes coexistaient : le suffixe `_enseignant` (notes d'orateur ou pas,
s'applique à TOUTE séance) et un script séparé `generer_variantes_deck.py`
(rattrapage ou pas, ne s'appliquait qu'à `S02`). Le second est **supprimé** : sa
logique est absorbée dans `generer_pptx_seance.py`, qui détecte automatiquement le
marqueur `<!-- RATTRAPAGE G1-G2 --> ... <!-- FIN RATTRAPAGE -->` dans la source et
produit alors une troisième sortie (`S02_groupes1-2.pptx`) EN PLUS des deux sorties
standard — rien à passer en argument, rien à retenir de plus qu'une seule commande par
séance. Avant cette fusion, `S02.pptx` (généré par l'ancien `generer_pptx_S02.py`) et
`S02_groupe3.pptx` (généré par `generer_variantes_deck.py`) étaient deux fichiers
identiques sous deux noms — supprimé, `S02.pptx` est maintenant la seule sortie « sans
rattrapage ».

## `S00_Intro-CFD-Helice_Slides.md` / `S03_..._Slides.md` — regex de chemin d'image

`TD-Helice-Marine` range sa galerie sous `Helice/Images/galerie/`, pas `Images/` à la
racine (vrai pour un dépôt de cours autonome, faux ici) — la regex d'extraction du
champ `**Figure(s)**` accepte les deux préfixes, **pour les trois séances** (vérifié
le 15/09 par diff : ce n'était plus vrai seulement pour `S00` comme l'affirmait une
version antérieure de cette page — les trois scripts avaient déjà convergé sur ce
point avant même la fusion en un seul fichier).

## Le deck de la séance 1 — hors de ce dossier, pour l'instant (LOT 6, 15/09)

`Helice/docs/15_DECK-SEANCE1_Slides.md` (source) et `_Setup/outils/
generer_deck_seance1.py` (générateur dédié, écrit avant l'unification ci-dessus, pas
inclus dans `generer_pptx_seance.py`) vivent dans `Helice/docs/`, pas ici. **Pas une
incohérence à corriger maintenant** : les étudiants ont cloné le dépôt en cours de
séquence, déplacer ce fichier casserait leur lien. Il rejoindra `Seances/` (renommé
`S01_Slides.md`) **après la dernière séance**, quand plus personne n'a besoin du lien
actuel — voir `Helice/docs/00_INDEX.md`, item 11.
