#!/usr/bin/env bash
# Falsificateur (INV-21) -- grep les motifs de valeurs PÉRIMÉES dans Helice/docs et
# Seances, et échoue (code != 0) si l'un d'eux apparaît hors de la liste d'exclusion
# explicite ci-dessous. Consigne du 15/09 : onze documents portaient simultanément la
# valeur fausse et la corrigée, recopiée au lieu d'être sourcée depuis
# Helice/docs/PARAMETRES_CAS.md -- ce script est le test qui aurait attrapé ça.
#
# Usage : _Setup/outils/verifier_valeurs_perimees.sh
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
)

# Citations historiques légitimes (LOT 2, consigne du 15/09) -- chaque entrée porte sa
# raison. Format : "chemin:ligne". Revérifié le 15/09 : chaque ligne listée ici porte
# une étiquette explicite dans le fichier ("corrigé le", "PÉRIMÉ", "SURCLASSÉ",
# "Avant correction", "était ... avec D=0,2", etc.) -- ce n'est pas une liste de
# complaisance, c'est la liste de ce qui a déjà été vérifié étiqueté.
EXCLUSIONS=(
    "Helice/docs/STATUT.md:85"    # étiquette PÉRIMÉ ajoutée le 15/09
    "Helice/docs/STATUT.md:92"    # table périmée, étiquetée juste au-dessus (ligne 85)
    "Helice/docs/STATUT.md:94"    # idem
    "Helice/docs/STATUT.md:140"   # "pas tripale" -- négation, erratum Z=4 du 13/09
    "Helice/docs/STATUT.md:148"   # passage barré (~~...~~), SURCLASSÉ le 13/09, gardé par INV-19
    "Helice/docs/STATUT.md:432"   # cite les notes d'orateur d'un AUTRE document, analyse un écart
    "Helice/docs/STATUT.md:433"   # suite de la même citation
    "Helice/docs/STATUT.md:434"   # suite de la même citation
    "Helice/docs/STATUT.md:440"   # "Sans objet depuis le 13/09" -- explicitement retiré
    "Helice/docs/MATERIAU-INTRO_TD-Helice.md:50"   # "codé en dur ... jusqu'ici" -- récit de correction du 14/09
    "Helice/docs/MATERIAU-INTRO_TD-Helice.md:66"   # "était 1,024 avec D=0,2" -- étiqueté explicitement
    "Helice/docs/MATERIAU-INTRO_TD-Helice.md:116"  # "Avant correction, l'argument reposait..." -- historique
    "Helice/docs/TUTORIEL_OpenFOAM-et-ParaView.md:65"   # "jusqu'au 14/09 ... corrigé le 14/09"
    "Helice/docs/TUTORIEL_OpenFOAM-et-ParaView.md:194"  # "portait D=0,2 m ... contre D=0,227 m"
    "Helice/docs/TUTORIEL_OpenFOAM-et-ParaView.md:218"  # liste des quatre erreurs PASSÉES trouvées le 13-14/09
    "Helice/docs/TUTORIEL_OpenFOAM-et-ParaView.md:235"  # "établi, contre 0,2 m codé en dur" -- contraste explicite
    "Helice/docs/PLAN_SEANCE-3.md:87"   # "faux, corrigé le 13/09"
    "Helice/docs/PLAN_SEANCE-3.md:95"   # "Écart avec la documentation existante (D=0,2m)... " -- signalé comme écart, pas comme fait
    "Helice/docs/PLAN_SEANCE-3.md:104"  # même paragraphe que 95, suivi de l'arbitrage rendu (ligne 110)
    "Helice/docs/PLAN_SEANCE-3.md:110"  # "Arbitrage rendu le 14/09 : D=... remplace 0,2m" -- la résolution elle-même
    "Helice/docs/FICHES-CONDUITE_Enseignant.md:75"   # "corrigé le 14/09 -- portait radius 0.1"
    "Helice/docs/FICHES-CONDUITE_Enseignant.md:159"  # récit du J calculé par l'ancien radius, suivi de "Correction du 14/09" (ligne 164)
    "Helice/docs/FICHES-CONDUITE_Enseignant.md:219"  # "INTROUVABLE ... ne plus jamais l'écrire" -- rétractation explicite du 60%
    "Helice/docs/FICHES-CONDUITE_Enseignant.md:306"  # "contre 0,2 m qui était écrit ... avant la correction du 14/09"
    "Helice/docs/09_FICHE_ENSEIGNANT.md:32"  # "mesuré le 14/09, remplace 0,2 m codé en dur"
    "Helice/docs/09_FICHE_ENSEIGNANT.md:52"  # "Rééchelonné le 14/09 : ... remplace 0,2 m"
    "Helice/docs/09_FICHE_ENSEIGNANT.md:90"  # "pas tripale" -- négation, erratum
    "Helice/docs/10_CORRIGE_ETUDIANT_DETAILLE.md:25"  # "remplace 0,2 m codé en dur"
    "Helice/docs/10_CORRIGE_ETUDIANT_DETAILLE.md:40"  # "Rééchelonné le 14/09 ... remplace 0,2 m"
    "Helice/docs/15_DECK-SEANCE1_Slides.md:94"  # "mesuré le 14/09 ... remplace 0,2 m codé en dur"
    "Helice/docs/ETAT-DES-LIEUX.md:20"   # "Remplace 0,2 m codé en dur ... (corrigé le 14/09)"
    "Helice/docs/ETAT-DES-LIEUX.md:38"   # "(« 60 % » retiré, remplacé par cette mesure sourcée)"
    "Helice/docs/ETAT-DES-LIEUX_Enseignant.md:30"  # source enseignante du même passage que ci-dessus
    "Helice/docs/ETAT-DES-LIEUX_Enseignant.md:48"  # idem
    "Seances/S00_Intro-CFD-Helice_Slides.md:194"  # "qui a remplacé les 0,2 m codés en dur" -- contraste explicite
    "Helice/docs/ERRATUM.md:5"  # "(et non 75,44 Hz)" -- l'erratum EST la correction elle-même
    "Helice/docs/PARAMETRES_CAS.md:6"    # ce fichier explique lui-même pourquoi ces valeurs sont périmées
    "Helice/docs/PARAMETRES_CAS.md:7"    # idem
    "Helice/docs/PARAMETRES_CAS.md:42"   # section "valeurs explicitement PÉRIMÉES, à ne jamais recopier"
    "Helice/docs/PARAMETRES_CAS.md:43"   # idem
    "Helice/docs/PARAMETRES_CAS.md:44"   # idem
    "Seances/S03_Arborescence-et-perspective_Slides.md:138"  # "D était faux de 14 %" -- diapo sur le mécanisme d'erreur, au passé
    "Seances/S03_Arborescence-et-perspective_Slides.md:155"  # "Constantes héritées jamais mesurées" -- idem, diapo mécanismes
    "Seances/S03_Arborescence-et-perspective_Slides.md:158"  # "a circulé ... sans qu'aucun log ne soit jamais ouvert" -- rétractation
    "Seances/S03_Arborescence-et-perspective_Slides.md:162"  # notes d'orateur, même rétractation sourcée JOURNAL
    "Seances/S03_Arborescence-et-perspective_Slides.md:202"  # "Écart signalé : ... citent encore « 4,42 »" -- signale l'écart, ne le recopie pas comme fait
    "Seances/S03_Arborescence-et-perspective_Slides.md:203"  # suite de la même note
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
