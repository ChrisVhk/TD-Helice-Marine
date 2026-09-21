#!/usr/bin/env bash
# Falsificateur (INV-21) -- grep les motifs de valeurs PÉRIMÉES dans Helice/docs et
# Seances, et échoue (code != 0) si l'un d'eux apparaît hors de la liste d'exclusion
# explicite ci-dessous. Consigne du 15/09 : onze documents portaient simultanément la
# valeur fausse et la corrigée, recopiée au lieu d'être sourcée depuis
# Helice/docs/PARAMETRES_CAS.md -- ce script est le test qui aurait attrapé ça.
#
# Usage : _Setup/outils/verifier_valeurs_perimees.sh
#
# LIMITE (20/09) : les ~95 exclusions ci-dessous n'ont JAMAIS été revues une à une ; le garde ne prouve donc pas qu'elles ne masquent rien.
#
# Ce qu'il NE fait PAS : deviner qu'une occurrence est une citation historique
# légitime (un erratum, une ligne « c'était X, corrigé en Y ») à partir du contexte --
# ce serait une exception silencieuse. Les citations légitimes trouvées le 15/09 sont
# listées EXPLICITEMENT ci-dessous, fichier:ligne, avec leur raison. Toute nouvelle
# occurrence légitime doit être ajoutée ici À LA MAIN, jamais absorbée par un motif
# plus permissif.

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../.." && pwd)"
cd "$REPO_ROOT" || exit 2

# Motifs périmés (consigne du 15/09) -- extended regex, un par ligne.
PATTERNS=(
    '3 pales'
    'tripale'
    '75,4'
    'D ?= ?0,2\b'
    '0,2 m'
    'radius 0\.1\b'
    '0,3625'
    '1,024'
    '60 ?%'
    '4,42'
    '82,7'
    '0,0404'
    '0,0373'
    '0,0294'
    'M=1,031'
    'N=6 '
    '2,4287'
    '2,2967'
    '2,2312'
    'P/D≈2,3'
    # 20/09 -- valeurs à 1,5 tour (fenêtre recouvrant la mise en régime), remplacées par celles à 4,00 tours
    '0,2170|0,2221|0,2261'        # K_T à 1,5 tour
    '0,5556|0,5401|0,5371'        # 10K_Q à 1,5 tour
    '0,5599|0,5901|0,6033'        # eta_0 à 1,5 tour
    '0,0176|0,0223|0,0242'        # amplitudes K_T à 1,5 tour
    '0,9033'                      # J à t=0,06 s
    '0,029 à 0,040|2 à 2,7 fois|ΔK_T ?≈ ?0,015'   # forme 13/09 de la comparaison amplitude/écart (fiche consigne), jamais recopiée de PARAMETRES_CAS
    # 20/09 (soir) -- J et eta_0 du solveur : URef est relevée à 0,17 D EN AVAL des pales (induction), pas une avance.
    # J correct = avance imposée 0,8743 (les quatre cas) ; eta_0 correct 0,5457 / 0,5738 / 0,5873 (couches 0,5245).
    '0,8936|0,8912|0,8922'        # J du solveur (URef mesuré en aval)
    '0,5578|0,5864|0,5986|0,5352'  # eta_0 calculé avec ce J
)

# Citations historiques légitimes (LOT 2, consigne du 15/09) -- chaque entrée porte sa
# raison. Format : "chemin:ligne". Revérifié le 15/09 : chaque ligne listée ici porte
# une étiquette explicite dans le fichier ("corrigé le", "PÉRIMÉ", "SURCLASSÉ",
# "Avant correction", "était ... avec D=0,2", etc.) -- ce n'est pas une liste de
# complaisance, c'est la liste de ce qui a déjà été vérifié étiqueté.
EXCLUSIONS=(
    "Helice/docs/STATUT.md:91"    # étiquette PÉRIMÉ ajoutée le 15/09
    "Helice/docs/STATUT.md:98"    # table périmée, étiquetée juste au-dessus (ligne 85)
    "Helice/docs/STATUT.md:100"    # idem
    "Helice/docs/STATUT.md:149"   # "pas tripale" -- négation, erratum Z=4 du 13/09
    "Helice/docs/STATUT.md:157"   # passage barré (~~...~~), SURCLASSÉ le 13/09, gardé par INV-19
    "Helice/docs/STATUT.md:441"   # cite les notes de diapo d'un AUTRE document, analyse un écart
    "Helice/docs/STATUT.md:442"   # suite de la même citation
    "Helice/docs/STATUT.md:443"   # suite de la même citation
    "Helice/docs/STATUT.md:449"   # "Sans objet depuis le 13/09" -- explicitement retiré
    "Helice/docs/MATERIAU-INTRO_TD-Helice.md:50"   # "codé en dur ... jusqu'ici" -- récit de correction du 14/09
    "Helice/docs/MATERIAU-INTRO_TD-Helice.md:66"   # "était 1,024 avec D=0,2" -- étiqueté explicitement
    "Helice/docs/MATERIAU-INTRO_TD-Helice.md:116"  # "Avant correction, l'argument reposait..." -- historique
    "Helice/docs/TUTORIEL_OpenFOAM-et-ParaView.md:65"   # "jusqu'au 14/09 ... corrigé le 14/09"
    "Helice/docs/TUTORIEL_OpenFOAM-et-ParaView.md:194"  # "portait D=0,2 m ... contre D=0,227 m"
    "Helice/docs/TUTORIEL_OpenFOAM-et-ParaView.md:347"  # liste des quatre erreurs PASSÉES trouvées le 13-14/09 (décalé le 17/09 par la correction M/N)
    "Helice/docs/TUTORIEL_OpenFOAM-et-ParaView.md:364"  # "établi, contre 0,2 m codé en dur" -- contraste explicite (décalé le 17/09)
    "Helice/docs/TUTORIEL_OpenFOAM-et-ParaView.md:282"  # "N=6 est le plafond, pas une valeur calculée" -- discussion du plafond, LOT 17/09
    "Helice/docs/PLAN_SEANCE-3.md:97"   # "faux, corrigé le 13/09" (décalé le 16/09, LOT D2, piste avancée)
    "Helice/docs/PLAN_SEANCE-3.md:105"  # "Écart avec la documentation existante (D=0,2m)... " -- signalé comme écart, pas comme fait (décalé)
    "Helice/docs/PLAN_SEANCE-3.md:114"  # même paragraphe, suivi de l'arbitrage rendu (décalé)
    "Helice/docs/PLAN_SEANCE-3.md:120"  # "Arbitrage rendu le 14/09 : D=... remplace 0,2m" -- la résolution elle-même (décalé)
    "Helice/docs/FICHES-CONDUITE_Enseignant.md:75"   # "corrigé le 14/09 -- portait radius 0.1"
    "Helice/docs/FICHES-CONDUITE_Enseignant.md:159"  # récit du J calculé par l'ancien radius, suivi de "Correction du 14/09" (ligne 164)
    "Helice/docs/FICHES-CONDUITE_Enseignant.md:219"  # "INTROUVABLE ... ne plus jamais l'écrire" -- rétractation explicite du 60%
    "Helice/docs/FICHES-CONDUITE_Enseignant.md:306"  # "contre 0,2 m qui était écrit ... avant la correction du 14/09"
    "Helice/docs/09_FICHE_ENSEIGNANT.md:32"  # "mesuré le 14/09, remplace 0,2 m codé en dur"
    "Helice/docs/09_FICHE_ENSEIGNANT.md:55"  # "Rééchelonné le 14/09 : ... remplace 0,2 m"
    "Helice/docs/09_FICHE_ENSEIGNANT.md:100"  # "pas tripale" -- négation, erratum
    "Helice/docs/10_CORRIGE_ETUDIANT_DETAILLE.md:27"  # "remplace 0,2 m codé en dur"
    "Helice/docs/10_CORRIGE_ETUDIANT_DETAILLE.md:42"  # "Rééchelonné le 14/09 ... remplace 0,2 m"
    "Helice/docs/15_DECK-SEANCE1_Slides.md:105"  # "mesuré le 14/09 ... remplace 0,2 m codé en dur" (ligne décalée par le pointeur d'archive, LOT 2 consigne "Lever-la-contradiction" du 18/09)
    "Helice/docs/ETAT-DES-LIEUX.md:20"   # "Remplace 0,2 m codé en dur ... (corrigé le 14/09)"
    "Helice/docs/ETAT-DES-LIEUX.md:38"   # "(« 60 % » retiré, remplacé par cette mesure sourcée)"
    "Helice/docs/ETAT-DES-LIEUX_Enseignant.md:30"  # source enseignante du même passage que ci-dessus
    "Helice/docs/ETAT-DES-LIEUX_Enseignant.md:48"  # idem
    "Seances/S01_Slides.md:189"  # "0,2 m codés en dur" -- contraste explicite (ex-S00_Intro-CFD-Helice, fusionné le 18/09 dans S01, LOT 3 ; décalée le 18/09 consigne "Lever-la-contradiction" LOT 4, notes de conduite facultatives ajoutées plus haut)
    "Helice/docs/ERRATUM.md:5"  # "(et non 75,44 Hz)" -- l'erratum EST la correction elle-même
    "Helice/docs/PARAMETRES_CAS.md:6"    # ce fichier explique lui-même pourquoi ces valeurs sont périmées
    "Helice/docs/PARAMETRES_CAS.md:7"    # idem
    "Helice/docs/PARAMETRES_CAS.md:79"   # "reste au stade PRÉ-correction de D (D=0,2 m..." -- contraste explicite, LOT A1 du 15/09
    "Helice/docs/PARAMETRES_CAS.md:80"   # "radius 0.1 -- vérifié" -- suite du même contraste
    "Helice/docs/PARAMETRES_CAS.md:92"   # "donne K_T=0,3625 ... les valeurs PÉRIMÉES" -- contraste explicite, LOT A1 du 15/09
    "Helice/docs/PARAMETRES_CAS.md:179"  # section "valeurs explicitement PÉRIMÉES, à ne jamais recopier" (lignes décalées le 17/09 par la correction M/N)
    "Helice/docs/PARAMETRES_CAS.md:180"  # idem
    "Helice/docs/PARAMETRES_CAS.md:181"  # idem
    "Seances/S03_Slides.md:320"  # "D était faux de 14 %" -- diapo sur le mécanisme d'erreur, au passé (ex-S03_Arborescence-et-perspective:138)
    "Seances/S03_Slides.md:337"  # "Constantes héritées jamais mesurées" -- idem, diapo mécanismes (ex-S03_Arborescence-et-perspective:155)
    "Seances/S03_Slides.md:340"  # "a circulé ... sans qu'aucun log ne soit jamais ouvert" -- rétractation (ex-S03_Arborescence-et-perspective:158)
    "Seances/S03_Slides.md:344"  # même rétractation sourcée JOURNAL (ex-S03_Arborescence-et-perspective:162)
    "Helice/docs/ETAT-DES-LIEUX.md:95"    # brut jamais réécrit (INV-19), D=0,2 y reste vrai par décision -- pas une valeur périmée à corriger (ligne décalée par LOT 4 du 18/09, section baffle)
    "Helice/docs/METHODO_DONNEES.md:22"   # idem, LOT défauts de données du 15/09
    "Helice/docs/METHODO_DONNEES.md:167"  # idem (ligne décalée par LOT 2 du 17/09, ajout §3)
    "Helice/docs/ETAT-DES-LIEUX_Enseignant.md:105"  # idem (ligne décalée par LOT 4 du 18/09, section baffle)
    "Helice/docs/METHODO_DONNEES.md:46"  # "K_T=0,3625/J=1,0270 ... au lieu de 0,2170/0,9007" -- contraste explicite, LOT A1 du 15/09
    "Helice/docs/TUTORIEL_OpenFOAM-et-ParaView.md:284"  # "M=1,031 et N=6 ... sont CADUCS" -- contraste explicite, LOT D1 du 16/09
    "Helice/docs/PARAMETRES_CAS.md:173"  # "si N=6 tient réellement sous 20h" -- discussion du plafond, LOT 17/09, pas une valeur publiée comme un fait
    "Helice/docs/PARAMETRES_CAS.md:174"  # "N=6 dépasserait 20h" -- idem
    "Helice/docs/PARAMETRES_CAS.md:175"  # "N=6 est le PLAFOND, pas nécessairement..." -- idem
    "Helice/docs/PARAMETRES_CAS.md:183"  # "M=1,031 et N=6 (établis le 13/09" -- contraste explicite, LOT 17/09
    "Helice/docs/PARAMETRES_CAS.md:59"   # "valeur publiée le 17/09 (2,4287) était FAUSSE" -- contraste explicite, LOT 3 du 18/09
    "Helice/docs/PARAMETRES_CAS.md:60"   # "Remplace la valeur erronée du 17/09 (2,2967)" -- idem
    "Helice/docs/PARAMETRES_CAS.md:61"   # "Remplace la valeur erronée du 17/09 (2,2312)" -- idem
    "Seances/S02_Slides.md:106"  # "0,0294/0,0404/0,0373 pour l'amplitude) -- remplacées" -- historique déjà étiqueté (décalé le 18/09, LOT 3 consigne "Cloture-et-passation", diapo figures K_Q/eta0 ajoutée)
    "Seances/S01_Slides.md:273"  # notes de diapo diapo 12, verbatim origine (07/09) -- "D = 0,2 m, 3 pales" -- extraction LOT 1 du 18/09, NON corrigé par choix (hors des deux corrections autorisées) -- ligne décalée par les notes de conduite facultatives, LOT 4 consigne "Lever-la-contradiction"
    "Seances/S01_Slides.md:275"  # idem, suite de la même note -- "D = 0,2 m" verbatim
    "Seances/S01_Slides.md:278"  # idem -- "le patch propellerTip porte les 3 pales" verbatim
    "Seances/S01_Slides.md:484"  # notes de diapo diapo 20, CORRIGÉES le 18/09 (consigne "Cloture-et-passation" LOT 2) -- décrit explicitement l'ANCIENNE erreur ("3 pales (case 3, 75,44 Hz)") au passé, pour expliquer la correction -- pas une valeur actuelle
    "Seances/S01_Slides.md:523"  # idem, diapo 21 -- "l'ancienne version de ces notes cherchait un creux à 3n = 75,44 Hz" -- même nature, décrit le passé
    # --- 20/09 : valeurs à 1,5 tour et anciennes amplitudes, citées EXPLICITEMENT comme périmées (remplacées par les valeurs à 4,00 tours) ---
    "Helice/docs/10_CORRIGE_ETUDIANT_DETAILLE.md:52"  # 20/09 : valeur à 1,5 tour citée comme périmée / historique (section « Historique » de PARAMETRES_CAS pour 196-200)
    "Helice/docs/10_CORRIGE_ETUDIANT_DETAILLE.md:171"  # 20/09 : valeur à 1,5 tour citée comme périmée / historique (section « Historique » de PARAMETRES_CAS pour 196-200)
    "Helice/docs/ETAT-DES-LIEUX.md:45"  # 20/09 : valeur à 1,5 tour citée comme périmée / historique (section « Historique » de PARAMETRES_CAS pour 196-200)
    "Helice/docs/METHODO_DONNEES.md:133"  # 20/09 : valeur à 1,5 tour citée comme périmée / historique (section « Historique » de PARAMETRES_CAS pour 196-200)
    "Helice/docs/METHODO_DONNEES.md:189"  # 20/09 : valeur à 1,5 tour citée comme périmée / historique (section « Historique » de PARAMETRES_CAS pour 196-200)
    "Helice/docs/MATERIAU-INTRO_TD-Helice.md:136"  # 20/09 : valeur à 1,5 tour citée comme périmée / historique (section « Historique » de PARAMETRES_CAS pour 196-200)
    "Helice/docs/MATERIAU-INTRO_TD-Helice.md:154"  # 20/09 : valeur à 1,5 tour citée comme périmée / historique (section « Historique » de PARAMETRES_CAS pour 196-200)
    "Helice/docs/09_FICHE_ENSEIGNANT.md:117"  # 20/09 : valeur à 1,5 tour citée comme périmée / historique (section « Historique » de PARAMETRES_CAS pour 196-200)
    "Helice/docs/09_FICHE_ENSEIGNANT.md:44"  # 20/09 : valeur à 1,5 tour citée comme périmée / historique (section « Historique » de PARAMETRES_CAS pour 196-200)
    "Helice/docs/09_FICHE_ENSEIGNANT.md:65"  # 20/09 : valeur à 1,5 tour citée comme périmée / historique (section « Historique » de PARAMETRES_CAS pour 196-200)
    "Helice/docs/09_FICHE_ENSEIGNANT.md:66"  # 20/09 : valeur à 1,5 tour citée comme périmée / historique (section « Historique » de PARAMETRES_CAS pour 196-200)
    "Helice/docs/09_FICHE_ENSEIGNANT.md:116"  # 20/09 : valeur à 1,5 tour citée comme périmée / historique (section « Historique » de PARAMETRES_CAS pour 196-200)
    "Helice/docs/FICHES-CONDUITE_Enseignant.md:44"  # 20/09 : valeur à 1,5 tour citée comme périmée / historique (section « Historique » de PARAMETRES_CAS pour 196-200)
    "Helice/docs/ETAT-DES-LIEUX_Enseignant.md:55"  # 20/09 : valeur à 1,5 tour citée comme périmée / historique (section « Historique » de PARAMETRES_CAS pour 196-200)
    "Helice/docs/PARAMETRES_CAS.md:94"  # 20/09 : valeur à 1,5 tour citée comme périmée / historique (section « Historique » de PARAMETRES_CAS pour 196-200)
    "Helice/docs/10_CORRIGE_ETUDIANT_DETAILLE.md:53"  # 20/09 : valeur à 1,5 tour citée comme périmée / historique (section « Historique » de PARAMETRES_CAS pour 196-200)
    "Helice/docs/METHODO_DONNEES.md:45"  # 20/09 : valeur à 1,5 tour citée comme périmée / historique (section « Historique » de PARAMETRES_CAS pour 196-200)
    "Helice/docs/MATERIAU-INTRO_TD-Helice.md:135"  # 20/09 : valeur à 1,5 tour citée comme périmée / historique (section « Historique » de PARAMETRES_CAS pour 196-200)
    "Helice/docs/PARAMETRES_CAS.md:200"  # 20/09 : valeur à 1,5 tour citée comme périmée / historique (section « Historique » de PARAMETRES_CAS pour 196-200)
    "Helice/docs/PARAMETRES_CAS.md:201"  # 20/09 : valeur à 1,5 tour citée comme périmée / historique (section « Historique » de PARAMETRES_CAS pour 196-200)
    "Helice/docs/PARAMETRES_CAS.md:202"  # 20/09 : valeur à 1,5 tour citée comme périmée / historique (section « Historique » de PARAMETRES_CAS pour 196-200)
    "Helice/docs/PARAMETRES_CAS.md:203"  # 20/09 : valeur à 1,5 tour citée comme périmée / historique (section « Historique » de PARAMETRES_CAS pour 196-200)
    "Helice/docs/PARAMETRES_CAS.md:204"  # 20/09 : valeur à 1,5 tour citée comme périmée / historique (section « Historique » de PARAMETRES_CAS pour 196-200)
    "Seances/S03_Slides.md:520"  # 20/09 soir : diapo 26, « le solveur affichait 0,8936 » -- citation étiquetée de la valeur corrigée
    "Seances/S03_Slides.md:521"  # 20/09 soir : diapo 26, « 0,5578 au lieu de 0,5457 » -- citation étiquetée de la valeur corrigée
    "Helice/docs/MATERIAU-INTRO_TD-Helice.md:46"  # 20/09 soir : « J mesuré 0,8936 » présenté comme J du calcul, FAUX ; GELÉ, E-60
    "Helice/docs/09_FICHE_ENSEIGNANT.md:60"  # 20/09 soir : tableau J et eta_0 du solveur, FAUX ; GELÉ, E-60
    "Helice/docs/09_FICHE_ENSEIGNANT.md:61"  # idem, E-60
    "Helice/docs/09_FICHE_ENSEIGNANT.md:62"  # idem, E-60
    "Helice/docs/09_FICHE_ENSEIGNANT.md:77"  # 20/09 soir : « eta_0 le plus haut (0,5986) » avec le J du solveur, FAUX (0,5873) ; GELÉ, E-60
    "Helice/docs/10_CORRIGE_ETUDIANT_DETAILLE.md:48"  # 20/09 soir : tableau J et eta_0 du solveur, FAUX ; document GELÉ, à corriger au dégel, E-60
    "Helice/docs/10_CORRIGE_ETUDIANT_DETAILLE.md:49"  # 20/09 soir : idem ; document GELÉ, à corriger au dégel, E-60
    "Helice/docs/10_CORRIGE_ETUDIANT_DETAILLE.md:50"  # 20/09 soir : idem ; document GELÉ, à corriger au dégel, E-60
    "Helice/docs/10_CORRIGE_ETUDIANT_DETAILLE.md:81"  # 20/09 soir : « eta_0 le plus élevé (0,5986) » avec le J du solveur, FAUX (0,5873) ; document GELÉ, à corriger au dégel, E-60
)

is_excluded() {
    local needle="$1"
    for e in "${EXCLUSIONS[@]}"; do
        [[ "$e" == "$needle" ]] && return 0
    done
    return 1
}

fail=0
n_checked=0
n_excluded=0

while IFS= read -r -d '' f; do
    rel="${f#./}"
    for pat in "${PATTERNS[@]}"; do
        while IFS=: read -r lineno content; do
            [[ -z "$lineno" ]] && continue
            n_checked=$((n_checked + 1))
            key="${rel}:${lineno}"
            if is_excluded "$key"; then
                n_excluded=$((n_excluded + 1))
                continue
            fi
            echo "PÉRIMÉ : ${key} -- motif « ${pat} » -- ${content}" >&2
            fail=1
        done < <(grep -nE "$pat" "$f" 2>/dev/null)
    done
done < <(find Helice/docs Seances -type f -name '*.md' -print0 2>/dev/null)

echo "---"
echo "${n_checked} occurrence(s) de motifs périmés trouvée(s), ${n_excluded} exclue(s) (citation historique étiquetée)."
if [[ "$fail" -eq 1 ]]; then
    echo "ÉCHEC -- au moins une valeur périmée hors de la liste d'exclusion. Voir ci-dessus." >&2
    exit 1
fi
echo "OK -- aucune valeur périmée hors citation historique étiquetée."
exit 0
