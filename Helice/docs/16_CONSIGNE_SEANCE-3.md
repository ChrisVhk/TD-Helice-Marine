# Consigne — Séance 3 (y+ et couches de prismes)

## a) Objectifs

- Construire le maillage à couches de prismes (`case_kEpsilon_layers`) jusqu'à un état mesurable.
- Mesurer y+ sur ce maillage.
- Dire si les couches améliorent le calcul — vous savez déjà qu'elles gagnent sur la pale
  (`propellerTip`) et perdent sur le moyeu (`propellerStem`) : ce n'est pas un verdict binaire à
  découvrir, c'est un compromis à décrire dans ses deux sens.

## b) À faire avant lundi

Lire, dans l'ordre :
- `Helice/docs/03_BASE_THEORIQUE.md` §4 — y+, les trois régions de la couche limite, ce que font
  les couches de prismes.
- `Helice/docs/CARTE_DU_CAS_recto-verso.md` — l'arborescence du cas, les quatre états.
- `Helice/docs/PARAMETRES_CAS.md` — la table de référence sourcée. Ne recopiez jamais un chiffre
  d'ailleurs (une diapo, un souvenir de séance précédente) sans revenir vérifier ici.

Savoir répondre SANS aide, avant la séance :
- **Où est réglée la vitesse de rotation** sur le cas que vous allez construire
  (`case_kEpsilon_layers`) ? `constant/dynamicMeshDict`, lignes 37-42 — attention, PAS une valeur
  simple comme sur les trois autres cas du dépôt : ici `omega` est une **rampe** (`Function1`
  type `table`) : 0 rad/s à t=0, 158 rad/s atteint à t=0,005 s, maintenu ensuite.
- **Combien de pales** a cette hélice ? Vérifié par histogramme azimutal, pas par comptage à
  l'œil sur une image — `Helice/docs/ETAT-DES-LIEUX.md` §ÉTABLI, entrée « Z = 4 ».

REFAIRE vous-même la figure K_T en fonction des tours (pas la relire, la régénérer) :
- Script : `_Setup/outils/tracer_series_temporelles.py`
- Données lues : `Helice/data/perf_kEpsilon.csv`, `perf_kOmegaSST.csv`, `perf_laminar.csv`
- Commande, depuis la racine du dépôt : `python3 _Setup/outils/tracer_series_temporelles.py`
- **Question de contrôle**, à vous poser avant de demander à qui que ce soit d'autre : combien
  de lignes du CSV couvrent un seul tour d'hélice ? (Un répertoire de temps écrit n'est pas un
  pas de temps calculé — ce sont deux choses différentes, voir `Helice/docs/METHODO_DONNEES.md`
  §2-3 si la question bloque.)

## c) Ce qui est noté

Le rapport de fin de séance. Critères :
- **Exactitude des chiffres ET source citée** (fichier + ligne) pour chacun — un chiffre juste
  sans source ne compte pas plus qu'un chiffre faux.
- **Lecture de courbe** : abscisse, fenêtre de moyenne, amplitude, le piège des deux échelles.
- **Capacité à dire ce que vous ne savez pas** — plutôt que d'inventer une valeur ou d'arrondir
  une incertitude en certitude.

## d) Avant de venir en séance

Faites `Helice/docs/17_AUTO-EVALUATION_avant-seance-3.md` (dix questions, sans les réponses) —
c'est le meilleur indicateur de si vous êtes prêt pour lundi.
