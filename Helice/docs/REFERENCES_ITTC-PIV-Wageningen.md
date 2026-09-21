# Références web — ITTC, PIV, série B Wageningen

LOT 7, consigne du 18/09 « Consolidee_Figures-et-variante-Vega ». Du texte, jamais
une figure copiée — une donnée publiée peut être retracée avec citation, une figure
ne le peut pas (voir en-tête de la consigne). Recherches faites le 18/09.

## Procédures ITTC — essai en eau libre et analyse d'incertitude

- **ITTC – Recommended Procedures and Guidelines 7.5-02-03-02.1**, *Propulsion,
  Performance — Propulsion Test — Open Water Test*, dernière révision consultée : 04
  (2021). Fixe la procédure de l'essai en eau libre lui-même (montage, mesures,
  précisions indicatives) — les précisions indicatives citées y sont explicitement
  décrites comme indicatives, pas comme les exigences réelles : c'est l'analyse
  d'incertitude (ci-dessous) qui donne les exigences.
- **ITTC – Recommended Procedures and Guidelines 7.5-02-01-01**, *Uncertainty
  Analysis in EFD — Uncertainty Assessment Methodology*. Méthodologie générale
  d'analyse d'incertitude en essai (EFD = Experimental Fluid Dynamics).
- **ITTC – Recommended Procedures and Guidelines 7.5-02-01-02**, *Uncertainty
  Analysis in EFD — Guidelines for Uncertainty Assessment*. Lignes directrices
  d'application de la méthodologie ci-dessus.
- **ITTC – Recommended Procedures and Guidelines 7.5-02-03-02.2**, *Uncertainty
  Analysis Example for Propeller Open Water Test*. Exemple chiffré complet
  d'application au cas précis de l'essai en eau libre d'hélice — le plus directement
  transposable à ce TD si un volet essais/incertitude devait s'y ajouter.

Trouvées via le portail officiel `ittc.info` (`www.ittc.info/media/…`), plusieurs
révisions/miroirs du même numéro de procédure recensés (04 la plus récente vue) — le
numéro de procédure et son titre sont la référence stable, pas l'URL exacte du PDF
(qui change de révision en révision).

## Traitement PIV — intercorrélation, fenêtre d'interrogation, rejet de vecteurs aberrants

Pas de procédure ITTC dédiée trouvée équivalente aux deux ci-dessus pour le PIV
spécifiquement — la littérature de référence est ici une revue, pas une norme :

- **Adrian, R.J. & Westerweel, J.**, *Particle Image Velocimetry*, Cambridge
  University Press — référence historique du domaine (non consultée directement le
  18/09, citée par la littérature secondaire trouvée, à vérifier directement avant
  toute citation ferme dans un support étudiant).
- **« Particle image velocimetry — Classical operating rules from today's
  perspective »**, *Experiments in Fluids* / ScienceDirect (2019) — revue de synthèse
  trouvée le 18/09, couvre explicitement : l'intercorrélation comme opérateur
  standard (robustesse, calcul par FFT, détection d'un pic de déplacement valide
  au-dessus du bruit) ; le schéma multi-grille à fenêtre décroissante (résolution
  spatiale vs. plage dynamique de vitesse) ; le recouvrement à 50 % des fenêtres
  (critère de Nyquist) ; le rejet de vecteurs aberrants (validation du pic, seuil de
  corrélation < 0,7 rejeté, seuil de vitesse physique, moyenne mobile) — les valeurs
  numériques exactes (résolution spatiale, seuils) sont des EXEMPLES cités par cette
  revue pour des configurations particulières, pas des constantes universelles à
  recopier sans les rattacher à un montage précis.

**Périmètre non couvert ici** : aucune donnée de calibration ou de montage optique
propre à ce TD — ce TD ne fait pas de PIV, ce lot ne fait que consigner la méthode
pour un usage futur éventuel (inter-séance B, ParaView vs. essai réel).

## Série B Wageningen — offsets géométriques

**Toujours bloqué**, comme constaté le 17/09 — voir
`ENSM-Enseignement/_Reserve/pale-B4/BLOQUANT_source-offsets.md` (note complète,
tentatives documentées : Kuiper 1992 MARIN Publication 92-001, CiteSeerX,
scholarworks.uno.edu, générateur interactif `wageningen-b-series-propeller.com`,
`BladeX`). Non retenté le 18/09 : rien dans le contexte de cette consigne ne change
l'accès à ces sources. Les deux références les plus citées pour cette table restent :

- **van Lammeren, W.P.A., van Manen, J.D. & Oosterveld, M.W.C.** (1969), *The
  Wageningen B-Screw Series*, SNAME Transactions, vol. 77.
- **Carlton, J.S.**, *Marine Propellers and Propulsion*, Butterworth-Heinemann —
  reproduit la table B4-70 complète dans ses éditions successives (non consulté
  directement le 18/09, à vérifier avant toute citation ferme).

Aucune des deux n'a été récupérée le 18/09 — signalé, pas reconstitué. Une table
d'offsets DE LA SÉRIE B4 elle-même dont on ne peut pas répondre serait la même faute
qu'un chiffre inventé (même règle que le 17/09).
