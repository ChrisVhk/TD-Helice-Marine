# Travaux inter-séances — TD Hélice marine

Deux travaux de binôme, à rendre **au début** de la séance suivante. C'est là que se fait le
travail personnel du TD : chaque séance suppose le précédent fait.

---

## Inter-séance A (entre séance 1 et séance 2) — ~1 h

### A.1 — Caractériser *votre* fermeture

Chaque binôme reçoit **une seule** des trois séries (`data/perf_<fermeture>.csv`). Vous ne verrez
les deux autres qu'en séance 2 : ne les cherchez pas.

Colonnes du fichier : `time, n, URef, J, KT, 10KQ, eta0` (une ligne par pas de temps écrit).

Produisez, pour **votre** cas :

1. **Le tracé** de $K_T(t)$ et de $10\,K_Q(t)$ sur tout le calcul. Repérez à l'œil le moment où le
   régime s'établit.
2. **La moyenne** de $K_T$, $10\,K_Q$, $\eta_0$ sur le **dernier tour complet**
   $[\,t_{end} - T,\ t_{end}\,]$ avec $T = 1/n$. (Justifiez le choix de la fenêtre — c'est la
   question de la séance 1.)
3. **L'amplitude** crête-à-crête de $K_T$ sur cette même fenêtre.
4. **Une phrase** : votre $\eta_0$ moyen, avec son incertitude = la demi-amplitude. Écrivez-le sous
   la forme $\eta_0 = \overline{\eta_0} \pm \tfrac{1}{2}\,\text{ampl}$.

> Outil libre : tableur, ou 15 lignes de Python. Aucune installation OpenFOAM requise — vous
> travaillez sur le CSV.

### A.2 — Terminer la décomposition d'efforts (doc 11)

Reprenez la méthode de la séance 1-B pour une **deuxième section**, à $r/R = 0{,}4$ :

- triangle des vitesses ($\varphi$, $W$, $\alpha$ avec $\beta = 40°$ comme en 4.) ;
- $\eta_{\text{section}}$ à ce rayon ;
- comparez $r/R = 0{,}4$ et $r/R = 0{,}7$ : qu'est-ce qui change, et pourquoi la pale est-elle
  **vrillée** ?

### Rendu A (une page recto-verso par binôme)

- recto : le tracé + les 3 moyennes + l'amplitude + la ligne $\eta_0 = \ldots \pm \ldots$ ;
- verso : les deux triangles de vitesses et la phrase sur le vrillage.

---

## Inter-séance B (entre séance 2 et séance 3) — installation de ParaView

La séance 3 se fait **sur ParaView en lecture seule**. Il faut qu'il s'ouvre et lise les données
avant d'arriver — on ne débogue pas d'installation en séance.

### B.1 — Installer

Suivez la partie **ParaView** de l'annexe
[`ANNEXE_Installation-OpenFOAM-ParaView.md`](ANNEXE_Installation-OpenFOAM-ParaView.md). Même
démarche que le pré-vol du cours *Informatique appliquée S5* :

1. installer (ParaView seul suffit — pas besoin d'OpenFOAM pour cette séance) ;
2. lancer le **script de vérification** fourni dans le kit (`data/verifie_paraview.py` ou la
   procédure de l'annexe) : il vous dit **en clair** si ParaView voit le jeu de données allégé ;
3. si ça ne marche pas, lisez la page **« ça n'a pas marché »** de l'annexe (virtualisation, droits
   admin, version de Windows, pilote graphique).

> **Repli explicite** : en binôme, **un seul poste qui marche suffit**. Ne perdez pas l'inter-séance
> à réparer deux machines.

### B.2 — Préparer une question

Regardez le jeu de données allégé (`data/`, ~750 Mo) : ouvrez-le, tournez autour, affichez le champ
de vitesse. **Préparez une seule question** à poser aux images en séance 3 — sur le sillage, les
tourbillons de bout de pale, la différence entre les trois cas, le critère $Q$… Une question
précise, pas « c'est quoi ce truc rouge ».

Vous y répondrez **devant les autres binômes** en séance 3-B (restitution croisée).

### Rendu B

- une capture d'écran de ParaView ouvert sur le jeu de données, avec le champ de vitesse affiché ;
- votre question, écrite en une phrase.

---

## Ce que l'enseignant vérifie au début de la séance suivante

| | attendu | rouge si… |
|---|---|---|
| Rendu A | tracé + moyennes + amplitude + $\eta_0 \pm$ ; 2 sections décomposées | la moyenne est prise sur la dernière ligne, ou la fenêtre n'est pas justifiée |
| Rendu B | capture ParaView + 1 question précise | ParaView pas installé et pas de solution de repli identifiée |
