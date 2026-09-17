# Auto-évaluation — avant la séance 3

Dix questions, sans les réponses. Le but n'est pas de deviner juste mais de vérifier
que vous savez OÙ chercher — chaque question pointe vers un fichier réel du dépôt.
Si une question vous bloque plus de cinq minutes, ouvrez le fichier indiqué avant de
demander de l'aide : c'est le réflexe que la séance notée évalue.

1. **Une vitesse sans unité vérifiée.** La vitesse de rotation de l'hélice est écrite
   dans un fichier sous la forme d'un simple nombre, suivi d'un commentaire donnant son
   unité. Le solveur vérifie-t-il que ce commentaire est juste ? Que se passerait-il si
   quelqu'un l'avait mal écrit ?
   → `constant/dynamicMeshDict`

2. **Le fichier qu'on édite n'est pas le fichier qu'on lit.** Pour changer la vitesse
   imposée à l'entrée du domaine, quel fichier faut-il éditer — et quel autre fichier,
   au même nom mais sans le même statut, est en réalité relu par le solveur à chaque
   lancement ? Que se passe-t-il si on édite le mauvais des deux ?
   → `0.orig/U` et `0/U` ; mécanisme décrit dans `Helice/docs/TUTORIEL_OpenFOAM-et-ParaView.md` §3, étape 5.

3. **Deux vitesses qui portent presque le même nom.** Le J que vous IMPOSEZ en réglant
   la vitesse d'entrée et le J que le calcul RAPPORTE dans son fichier de résultats
   sont-ils rigoureusement identiques ? Si non, dans quel fichier lit-on chacun des
   deux, et pourquoi un écart entre les deux n'est-il pas une erreur ?
   → `0.orig/U` (imposé) et `postProcessing/propellerInfo1/*/propellerPerformance.dat`, colonne `URef` (mesuré).

4. **Une masse volumique qui ne sert à rien — ou presque.** Le solveur utilisé dans ce
   TD est-il incompressible ou compressible ? Deux fichiers du cas déclarent chacun une
   valeur de ρ, différente l'une de l'autre. Cela change-t-il le résultat final en K_T ?
   → `system/forces` et `system/propellerInfo`.

5. **Demandé n'est pas obtenu.** Sur le maillage à couches, combien de couches de
   prismes sont DEMANDÉES sur la pale (`propeller.*`) ? Combien sont réellement
   OBTENUES, en moyenne, sur `propellerTip` ? Les deux chiffres viennent-ils du même
   fichier ?
   → demandé : `Helice/case_kEpsilon_layers/system/snappyHexMeshDict` (bloc `addLayersControls`) ; obtenu : `Helice/docs/PARAMETRES_CAS.md`.

6. **Raffiner n'est pas toujours améliorer.** Le maillage AVEC couches de prismes
   converge-t-il plus facilement ou moins facilement que le maillage SANS couches ?
   Qu'est-ce qui a permis de stabiliser le calcul sur le maillage à couches ?
   → `Helice/docs/03_BASE_THEORIQUE.md` §4 et `Helice/docs/PLAN_SEANCE-3.md`.

7. **Blocs ou lissé.** Dans ParaView, un champ affiché juste après ouverture du
   `.foam` apparaît en blocs rectangulaires plutôt que lissé. Est-ce un défaut du
   maillage ou un défaut d'affichage ? Quel filtre corrige cela ?
   → `Helice/docs/TUTORIEL_OpenFOAM-et-ParaView.md`, §4.1 et §4.4 (filtre `Cell Data to Point Data`).

8. **Linéaire ou logarithmique.** Certains champs (l'énergie cinétique turbulente k,
   par exemple) sont presque toujours affichés en échelle logarithmique plutôt que
   linéaire dans les figures de ce dépôt. Pourquoi — et cette règle vaut-elle pour tous
   les champs, ou seulement pour certains ?
   → `Helice/Images/galerie/LEGENDES.md` (règle générale sur les champs étalés sur des décades).

9. **Une case jamais cochée.** La convergence en maillage (vérifier que le résultat ne
   change plus si l'on raffine encore) a-t-elle été démontrée sur ce dépôt, pour un
   quelconque des chiffres publiés (K_T, K_Q, η₀, y+) ? Si non, ce point est-il passé
   sous silence ou consigné explicitement comme non tranché ?
   → `Helice/docs/ETAT-DES-LIEUX.md`, section « Convergence en maillage ».

10. **Le contrôle qui trahit une confusion.** Le fichier `data/perf_kEpsilon.csv`
    contient 1853 lignes. Le dossier du cas contient 62 répertoires de temps
    (`0`, `0.001`, … `0.06`). Ces deux nombres mesurent-ils la même chose ? Combien de
    lignes du CSV couvrent, en moyenne, UN SEUL tour complet d'hélice — et que vaut ce
    même calcul si on le fait, par erreur, à partir du nombre de répertoires plutôt que
    du nombre de lignes ?
    → `Helice/docs/METHODO_DONNEES.md` §2-3.
