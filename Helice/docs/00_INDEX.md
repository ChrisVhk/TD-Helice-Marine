# Index — TD Hélice marine (`Helice/docs/`)

**Ne renomme ni ne renumérote rien** : les étudiants ont cloné, un renommage casse leurs
liens en pleine séquence. Cet index ne fait que RANGER les fichiers existants dans
l'ordre de lecture — il ne réorganise pas `docs/`.

Régime : **PUBLIC** = suivi, distribué aux étudiants. **ENSEIGNANT** = gitignoré, sur
disque local uniquement, jamais dans le dépôt étudiant (voir `_Methodo/JOURNAL.md`
côté `ENSM-Enseignement`, INV-11 : un fichier gitignoré ne traverse pas un changement
de machine — sa trace de préparation vit dans ce dépôt-là, pas ici).

---

## Séance 1 — découverte

Ordre de lecture :

1. `01_FICHE_CONSIGNE.md` — présentation du TD, PUBLIC.
2. `ANNEXE_Installation-OpenFOAM-ParaView.md` — installation du poste, **à faire
   avant la séance**, PUBLIC. Voir note de recouvrement ci-dessous.
3. `02_QCM_PREREQUIS.md` — positionnement avant de commencer, PUBLIC.
4. `03_BASE_THEORIQUE.md` — hélice en eau libre, fermetures de turbulence, et
   (ajouté le 15/09) théorie de paroi $y^+$/couches de prismes, PUBLIC.
5. `04_GUIDE_PAS_A_PAS.md` — exécuter la chaîne OpenFOAM sur le cas fourni, PUBLIC.
6. `05_GUIDE_PARAVIEW.md` — post-traiter les résultats, PUBLIC. Voir note de
   recouvrement ci-dessous.
7. `07_AIDE_MEMOIRE.md` — référence rapide à garder ouverte pendant la séance, PUBLIC.
8. `11_PORTANCE_TRAINEE_PALE.md` — séance 1-B, du torseur à la portance/traînée
   d'une pale, PUBLIC.
9. `06_QCM_FINAL.md` — fin de séance 1, PUBLIC.
10. `13_CONTROLE-G1_SUJET.md` — contrôle d'ouverture (groupe 1 uniquement), PUBLIC.
11. `15_DECK-SEANCE1_Slides.md` — source du deck projeté en séance 1, PUBLIC.
   **Anomalie connue (documentée le 15/09, LOT 6)** : ce fichier vit dans `Helice/docs/`,
   alors que les sources des séances 2 et 3 vivent dans `Seances/` (`S02_Slides.md`,
   `S03_Arborescence-et-perspective_Slides.md`) — INTERDIT de le déplacer maintenant, les
   étudiants ont cloné le dépôt et un lien mort casserait leur accès en cours de séquence
   (règle générale de ce dépôt, `Helice/docs/` jamais renommé/déplacé en cours de TD). Il
   rejoindra `Seances/` (renommé `S01_Slides.md` pour la cohérence) **après la dernière
   séance**, quand plus aucun étudiant n'a besoin du lien actuel. Détail et convention
   complète : `Seances/README.md`.

**Enseignant, en regard de la séance 1** (non lus par les étudiants) :
`08_CORRIGE_QCM.md`, `09_FICHE_ENSEIGNANT.md`, `14_CONTROLE-G1_ENSEIGNANT.md`,
`MATERIAU-INTRO_TD-Helice.md`, `STATUT.md` (registre de statut, notes de
préparation).

## Séance 2 — confronter

12. `12_TRAVAUX_INTER_SEANCES.md` — travail à faire ENTRE la séance 1 et la
    séance 2, PUBLIC.
13. Deck projeté : `Seances/S02_Slides.md` (hors `docs/`, voir `Seances/README.md`).

**Enseignant** : `10_CORRIGE_ETUDIANT_DETAILLE.md` (corrigé détaillé, sert la
confrontation de séance 2 — ne jamais distribuer avant).

## Séance 3 — arborescence, y⁺, perspective couches

14. `PLAN_SEANCE-3.md` — déroulé complet (Acte 1 : diagramme en eau libre construit
    en classe ; Acte 2 : auto-propulsion ; piste avancée : maillage à couches), PUBLIC.
15. Deck projeté : `Seances/S03_Arborescence-et-perspective_Slides.md` (hors `docs/`).

---

## Hors séquence — références transversales

À consulter À TOUT MOMENT, pas dans un ordre de séance :

- `TUTORIEL_OpenFOAM-et-ParaView.md` — référence méthode détaillée (arborescence,
  cinq pièges réellement rencontrés, fiche d'identité du cas). Voir note de
  recouvrement ci-dessous.
- `PARAMETRES_CAS.md` — **source unique de vérité** pour tout chiffre du cas
  (Z, D, n, K_T, 10K_Q, η₀, y⁺, couverture des couches…), fichier et ligne pour
  chacun. Tout autre document qui cite un chiffre du cas doit y renvoyer.
- `ETAT-DES-LIEUX.md` — ce qui est ÉTABLI et ce qui reste INCERTAIN, source unique
  pour cette distinction (version enseignante complète et sourcée :
  `ETAT-DES-LIEUX_Enseignant.md`, gitignorée).
- `ERRATUM.md` — correctif Z=4 (pas 3) du 13/09 : à lire dès qu'un ancien support
  ou une ancienne note évoque « trois pales ».

**Enseignant, hors séquence** : `FICHES-CONDUITE_Enseignant.md` (antisèche de
conduite, onze contrastes pédagogiques, renvois vers `ETAT-DES-LIEUX.md`).

---

## Recouvrement constaté, non corrigé (audit du 15/09)

Six documents traitent de ParaView et/ou de l'installation, avec un recouvrement de
contenu réel :

| Document | Occurrences ParaView/installation (audit) |
|---|---|
| `ANNEXE_Installation-OpenFOAM-ParaView.md` | 24/43 |
| `05_GUIDE_PARAVIEW.md` | 12 |
| `14_CONTROLE-G1_ENSEIGNANT.md` | 12 |
| `12_TRAVAUX_INTER_SEANCES.md` | 11 |
| `TUTORIEL_OpenFOAM-et-ParaView.md` | 10 |
| `04_GUIDE_PAS_A_PAS.md` | 3 |

*(Non listés ci-dessus : `13_CONTROLE-G1_SUJET.docx/.pdf`, `14_CONTROLE-G1_ENSEIGNANT.docx`,
`DECK-SEANCE1.pptx` — artefacts binaires régénérés depuis leur `.md`/source, pas des
documents de lecture distincts ; tous gitignorés.)*

**Ce que cet index tranche, sans fusionner les fichiers** (la fusion est un chantier
d'après les séances, hors périmètre de cette boucle) :
- Pour l'**installation du poste** : `ANNEXE_Installation-OpenFOAM-ParaView.md` fait
  autorité — c'est son objet explicite, et c'est le document le plus complet
  (1626 lignes).
- Pour la **méthode ParaView** (post-traitement, pièges réellement rencontrés) :
  `TUTORIEL_OpenFOAM-et-ParaView.md` fait autorité — c'est le seul des six
  activement corrigé cette semaine (13-15/09, incidents réels sourcés) ;
  `05_GUIDE_PARAVIEW.md` (05/09, jamais retouché depuis) et les occurrences dans
  `12_TRAVAUX_INTER_SEANCES.md`/`14_CONTROLE-G1_ENSEIGNANT.md`/`04_GUIDE_PAS_A_PAS.md`
  sont plus anciens et n'ont pas été vérifiés contre les corrections récentes
  (D, Z=4, y⁺, couches) — **à ne pas prendre pour argent comptant sans les
  recouper contre `PARAMETRES_CAS.md` et `TUTORIEL_OpenFOAM-et-ParaView.md`.**
