---
title: "Contrôle d'ouverture — Environnement de travail"
subtitle: "FON-S7 · TD Hélice marine · Groupe 1"
date: "Lundi 7 septembre 2026"
lang: fr
geometry: margin=2.2cm
fontsize: 11pt
---

**Durée : 30 minutes · Sans document · Noté sur 20 (+ 2 points bonus possibles, question B3)**

> **Lisez ceci avant de commencer.**

Les trois parties sont **indépendantes** et pondérées : **A** vaut 8 points, **B** vaut 5 points
(+ 2 points **bonus** en B3, qui ne retirent rien si la réponse manque ou est fausse), **C** vaut
5 points. Traitez-les dans l'ordre que vous voulez.

On note **le raisonnement, pas l'orthographe des commandes**. Une faute de frappe, un accent
manquant, un nom de dossier approché : cela ne coûte rien. N'écrivez pas moins par peur de
vous tromper de syntaxe.

Ce contrôle porte sur l'environnement de travail installé au semestre dernier, **pas** sur le TD qui
commence aujourd'hui. Il sert à savoir d'où l'on repart.



# Partie A — Ligne de commande *(8 points, ~12 min)*

**A1 — Arborescence *(3 pts)*.** Depuis votre dossier personnel, créez **en ligne de commande**
l'arborescence ci-dessous, puis vérifiez qu'elle est correcte. Donnez les commandes exactes,
création **et** vérification.

```
TD_Helice/
├── data/
├── figures/
└── rendu/
```

**A2 — Déplacer et renommer *(2 pts)*.** Vous avez récupéré le fichier `perf_kepsilon.csv`
dans votre dossier de téléchargements. Placez-le dans `TD_Helice/data/` **en le renommant**
`cas_A.csv`. **Une seule commande.**

**A3 — Droits *(2 pts)*.** Vous avez écrit un script `trace.sh`. Il refuse de se lancer :

```
bash: ./trace.sh: Permission denied
```

**a)** Expliquez la cause et donnez la commande qui corrige. *(1 pt)*
**b)** Que signifient les trois chiffres de `chmod 755` ? *(1 pt)*

**A4 — Suppression *(1 pt)*.** Quelle est la différence entre `rm figures/` et
`rm -r figures/` ? Laquelle est dangereuse, et pourquoi l'est-elle davantage sous Linux que
dans l'explorateur Windows ?

# Partie B — WSL, Ubuntu et VS Code *(5 points, + 2 points bonus, ~10 min)*

**B1 — Pourquoi WSL *(2 pts)*.** Qu'est-ce que WSL ? Pourquoi l'utilise-t-on dans ce cours
**plutôt que** d'installer OpenFOAM directement sous Windows, et **plutôt qu'**une machine
virtuelle complète ? Deux arguments suffisent.

**B2 — Se situer *(2 pts)*.** Vous ouvrez un terminal Ubuntu. Donnez une commande pour
vérifier : **a)** que vous êtes bien sur **Ubuntu 24.04** ; **b)** **où** vous vous trouvez
dans l'arborescence.

**B3 — Les deux mondes *(BONUS, 2 pts)*.** Depuis WSL, où retrouvez-vous les fichiers du disque
`C:` de Windows ? Pourquoi est-il **déconseillé d'y faire tourner un calcul** OpenFOAM ?
*(Question bonus : une réponse absente ou fausse ne retire aucun point.)*

**B4 — VS Code *(1 pt)*.** Comment ouvre-t-on un dossier WSL dans VS Code ? À quoi voit-on,
à l'écran, que VS Code est bien connecté à WSL et non à Windows ?

# Partie C — ParaView *(5 points, ~8 min)*

**C1 — Rôle et entrée *(1,5 pt)*.** Qu'est-ce que ParaView et quelle est sa place dans la
chaîne de travail OpenFOAM ? **Quel fichier** ouvre-t-on pour charger un cas ?

**C2 — Rien ne s'affiche *(1,5 pt)*.** Vous ouvrez un cas et **rien n'apparaît** dans la vue.
Citez la cause la plus fréquente, puis deux autres vérifications à faire.

**C3 — Comparer trois calculs *(2 pts)*.** Vous devez comparer trois calculs entre eux.
**a)** Citez **deux réglages** sans lesquels la comparaison est fausse. *(1 pt)*
**b)** Citez **un filtre** permettant de regarder l'intérieur de l'écoulement. *(1 pt)*
