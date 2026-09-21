#!/usr/bin/env bash
# Falsificateur (INV-21) pour les DECKS PPTX -- LOT 4, consigne du 18/09
# "Supports-Vega". `verifier_valeurs_perimees.sh` ne grep que du texte (.md, .py,
# .sh) : un .pptx est un binaire, il ne le voit jamais. C'est exactement le trou qui a
# laissé l'erreur des 3 pales survivre onze jours dans DECK-SEANCE1.pptx (JOURNAL du
# 18/09, LOT 6) -- un livrable sans source en clair est hors de toute garde. Ce script
# déplie chaque .pptx et applique les MÊMES motifs périmés au texte qu'il contient.
#
# Portée (LOT 2, consigne du 18/09 "Cloture-et-passation") : les exemplaires PUBLICS
# (S<NN>.pptx) ET les exemplaires ENSEIGNANT/VEGA (ppt/notesSlides/*.xml) -- l'incohérence
# du 18/09 sur le nombre de pales vivait justement dans les notes de diapo, jamais vue
# par la version précédente de ce script (portée limitée à ppt/slides/). C'est ce que
# l'enseignant lit À VOIX HAUTE : une valeur périmée dans une note est une erreur DITE
# aux étudiants, pas seulement un texte projeté à corriger.
#
# Exclusions : RÉUTILISE celles de verifier_valeurs_perimees.sh, jamais une liste à
# part. Découvert en écrivant ce script (18/09) : des diapos de S03_Slides.md
# ("mécanismes de nos erreurs") ENSEIGNENT explicitement une valeur périmée comme
# exemple historique -- exactement la même nature que les "citations historiques
# étiquetées" déjà exclues côté texte. Un motif périmé trouvé dans le pptx n'échoue
# donc que s'il n'apparaît dans AUCUNE des lignes déjà exclues du .md source de cette
# séance -- pas de nouvelle liste, pas de jugement au cas par cas ici.
#
# Usage :
#   _Setup/outils/verifier_pptx_perime.sh                    # les S01/S02/S03.pptx de Seances/
#   _Setup/outils/verifier_pptx_perime.sh chemin/vers/X.pptx [Y.pptx ...]

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../.." && pwd)"
FALSIFICATEUR_TEXTE="$HERE/verifier_valeurs_perimees.sh"

if [ ! -f "$FALSIFICATEUR_TEXTE" ]; then
    echo "ERREUR : $FALSIFICATEUR_TEXTE introuvable -- ce script réutilise ses motifs, pas une copie." >&2
    exit 2
fi

# Réutilise le tableau PATTERNS de verifier_valeurs_perimees.sh à l'identique --
# jamais dupliqué à la main (deux listes qui divergent seraient pires qu'une seule
# jamais tenue à jour). Extraction bornée au bloc "PATTERNS=( ... )", sourcée seule :
# ne déclenche jamais la boucle principale de ce fichier.
PATTERNS_BLOC="$(sed -n '/^PATTERNS=(/,/^)/p' "$FALSIFICATEUR_TEXTE")"
if [ -z "$PATTERNS_BLOC" ]; then
    echo "ERREUR : bloc PATTERNS introuvable dans $FALSIFICATEUR_TEXTE -- ce script a divergé de sa source, corriger avant de continuer." >&2
    exit 2
fi
eval "$PATTERNS_BLOC"

# Même principe pour EXCLUSIONS -- "chemin:ligne" vers les .md source.
EXCLUSIONS_BLOC="$(sed -n '/^EXCLUSIONS=(/,/^)/p' "$FALSIFICATEUR_TEXTE")"
if [ -z "$EXCLUSIONS_BLOC" ]; then
    echo "ERREUR : bloc EXCLUSIONS introuvable dans $FALSIFICATEUR_TEXTE." >&2
    exit 2
fi
eval "$EXCLUSIONS_BLOC"

cibles=("$@")
if [ ${#cibles[@]} -eq 0 ]; then
    for s in S01 S02 S03; do
        for suffixe in "" "_enseignant"; do
            p="$REPO_ROOT/Seances/${s}${suffixe}.pptx"
            [ -f "$p" ] && cibles+=("$p")
        done
    done
fi
if [ ${#cibles[@]} -eq 0 ]; then
    echo "Aucun .pptx à vérifier (ni en argument, ni Seances/S01/S02/S03.pptx présents -- régénérer d'abord)." >&2
    exit 2
fi

fail=0
tmp_racine="$(mktemp -d)"
trap 'rm -rf "$tmp_racine"' EXIT

for pptx in "${cibles[@]}"; do
    if [ ! -f "$pptx" ]; then
        echo "ERREUR : $pptx introuvable." >&2
        fail=1
        continue
    fi
    dep="$tmp_racine/$(basename "$pptx" .pptx)"
    mkdir -p "$dep"
    unzip -oq "$pptx" "ppt/slides/slide*.xml" "ppt/notesSlides/notesSlide*.xml" -d "$dep" 2>/dev/null
    texte="$(grep -rho '<a:t>[^<]*</a:t>' "$dep/ppt/" 2>/dev/null | sed -E 's/<a:t>(.*)<\/a:t>/\1/')"
    n_notes=0
    [ -d "$dep/ppt/notesSlides" ] && n_notes=$(find "$dep/ppt/notesSlides" -name "notesSlide*.xml" | wc -l)

    # Source .md de cette séance -- retire un éventuel suffixe _enseignant du nom de
    # fichier pour retrouver le bon Seances/S<NN>_Slides.md (même source pour les deux
    # exemplaires). Les lignes déjà exclues côté texte y sont relues pour savoir si un
    # motif trouvé ici est le MÊME texte historique déjà vérifié, ou une occurrence
    # nouvelle.
    stem="$(basename "$pptx" .pptx)"
    stem="${stem%_enseignant}"
    md_source="$REPO_ROOT/Seances/${stem}_Slides.md"
    exclu_texte=""
    if [ -f "$md_source" ]; then
        for e in "${EXCLUSIONS[@]}"; do
            case "$e" in
                "Seances/${stem}_Slides.md:"*)
                    ligne_num="${e#*:}"
                    ligne_txt="$(sed -n "${ligne_num}p" "$md_source" 2>/dev/null)"
                    exclu_texte="${exclu_texte}${ligne_txt}"$'\n'
                    ;;
            esac
        done
    fi

    n_trouve=0
    n_exclu=0
    for pat in "${PATTERNS[@]}"; do
        while IFS= read -r ligne; do
            [ -z "$ligne" ] && continue
            # Ancrage sur la PHRASE COMPLÈTE, pas sur une ressemblance de motif (GATE,
            # consigne du 18/09 "Lever-la-contradiction") : la ligne de la diapo doit
            # être EXACTEMENT (égalité de chaîne, après recadrage des espaces) une des
            # lignes déjà exclues du .md -- pas seulement contenir le même motif que
            # l'une d'elles ailleurs dans le fichier. Deux occurrences distinctes du
            # même motif, une exclue et une nouvelle, ne peuvent plus se couvrir l'une
            # l'autre.
            exclue=0
            if [ -n "$exclu_texte" ]; then
                while IFS= read -r cand; do
                    [ -z "$cand" ] && continue
                    if [ "$cand" = "$ligne" ]; then
                        exclue=1
                        break
                    fi
                done <<< "$exclu_texte"
            fi
            if [ "$exclue" -eq 1 ]; then
                n_exclu=$((n_exclu + 1))
                continue
            fi
            echo "PÉRIMÉ : $pptx -- motif « ${pat} » -- ${ligne}" >&2
            n_trouve=$((n_trouve + 1))
            fail=1
        done < <(printf '%s\n' "$texte" | grep -E "$pat")
    done
    if [ "$n_trouve" -eq 0 ]; then
        echo "OK -- $pptx : aucun motif périmé hors citation historique déjà exclue côté texte (${n_exclu} occurrence(s) exclue(s), ${n_notes} notesSlide(s) inclus(es))."
    fi
done

exit $fail
