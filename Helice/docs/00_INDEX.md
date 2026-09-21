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
5. `05_GUIDE_PARAVIEW.md` — post-traiter les résultats, PUBLIC. Voir note de
   recouvrement ci-dessous.
6. `11_PORTANCE_TRAINEE_PALE.md` — séance 1-B, du torseur à la portance/traînée
   d'une pale, PUBLIC.
7. `13_CONTROLE-G1_SUJET.md` — contrôle d'ouverture (groupe 1 uniquement), PUBLIC.

**Enseignant, en regard de la séance 1** (non lus par les étudiants) :
`08_CORRIGE_QCM.md`, `09_FICHE_ENSEIGNANT.md`, `14_CONTROLE-G1_ENSEIGNANT.md`,
`MATERIAU-INTRO_TD-Helice.md`, `STATUT.md` (registre de statut, notes de
préparation).

## Séance 2 — confronter

8. Deck projeté : celui de la séance 2 (distribué par Moodle ; voir `Seances/README.md`).

**Enseignant** : `10_CORRIGE_ETUDIANT_DETAILLE.md` (corrigé détaillé, sert la
confrontation de séance 2 — ne jamais distribuer avant).

## Séance 3 — arborescence, y⁺, perspective couches

9. `PLAN_SEANCE-3.md` — déroulé complet (Acte 1 : diagramme en eau libre construit
    en classe ; Acte 2 : auto-propulsion ; piste avancée : maillage à couches), PUBLIC.
10. Deck projeté : celui de la séance 3 (distribué par Moodle).

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
- **Régime des images (règle posée le 17/09, LOT 4, consigne « Quatre-tours »)** :
  `Helice/Images/galerie/*.png` est un atelier, intégralement gitignoré (invisible
  sur GitHub). `Helice/Images/*.png` (convention `FIG-fon-s7-*`) est SUIVI. Toute
  image citée par un support destiné aux étudiants (un deck de `Seances/`, un `.md`
  public de ce dossier) doit vivre sous `Images/`, jamais sous `galerie/` — sinon le
  renvoi ne se voit cassé qu'en clonant à froid. Détail : `Seances/README.md` §5.

**Enseignant, hors séquence** : `FICHES-CONDUITE_Enseignant.md` (antisèche de
conduite, onze contrastes pédagogiques, renvois vers `ETAT-DES-LIEUX.md`).

---

## Recouvrement constaté, non corrigé (audit du 15/09)

Quatre documents traitent de ParaView et/ou de l'installation, avec un recouvrement de
contenu réel :

| Document | Occurrences ParaView/installation (audit) |
|---|---|
| `ANNEXE_Installation-OpenFOAM-ParaView.md` | 24/43 |
| `05_GUIDE_PARAVIEW.md` | 12 |
| `14_CONTROLE-G1_ENSEIGNANT.md` | 12 |
| `TUTORIEL_OpenFOAM-et-ParaView.md` | 10 |

*(Non listés ci-dessus : `13_CONTROLE-G1_SUJET.docx/.pdf`, `14_CONTROLE-G1_ENSEIGNANT.docx`,
`DECK-SEANCE1.pptx` — artefacts binaires régénérés depuis leur `.md`/source, pas des
documents de lecture distincts ; tous gitignorés.)*

**Ce que cet index tranche, sans fusionner les fichiers** (la fusion est un chantier
d'après les séances, hors périmètre de cette boucle) :
- Pour l'**installation du poste** : `ANNEXE_Installation-OpenFOAM-ParaView.md` fait
  autorité — c'est son objet explicite, et c'est le document le plus complet
  (1626 lignes).
- Pour la **méthode ParaView** (post-traitement, pièges réellement rencontrés) :
  `TUTORIEL_OpenFOAM-et-ParaView.md` fait autorité — c'est le seul des quatre
  activement corrigé cette semaine (13-15/09, incidents réels sourcés) ;
  `05_GUIDE_PARAVIEW.md` (05/09, jamais retouché depuis) et les occurrences dans
  `14_CONTROLE-G1_ENSEIGNANT.md` sont plus anciens et n'ont pas été vérifiés contre les corrections récentes
  (D, Z=4, y⁺, couches) — **à ne pas prendre pour argent comptant sans les
  recouper contre `PARAMETRES_CAS.md` et `TUTORIEL_OpenFOAM-et-ParaView.md`.**
