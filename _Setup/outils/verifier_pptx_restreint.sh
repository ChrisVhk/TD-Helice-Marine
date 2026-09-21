#!/usr/bin/env bash
# Contrôle INDÉPENDANT (LOT 4, consigne du 18/09 "Consolidee_Figures-et-variante-Vega")
# -- seconde moitié de la GARDE 2. `generer_pptx_seance.py` refuse déjà de PRODUIRE une
# sortie publique portant une figure `licence: restreint` (première moitié, dans le
# générateur). Ce script est la vérification par contenu, indépendante du générateur :
# il déplie un .pptx PUBLIC déjà généré et compare CHAQUE image qu'il embarque, par
# contenu (hash), au contenu de chaque image du dossier `Helice/Images/restreint/`
# (gitignoré, jamais suivi). Sans ce contrôle, un pptx public généré AVANT qu'une figure
# ne soit reclassée `restreint`, jamais régénéré depuis, embarquerait quand même les
# octets restreints sans que rien ne le signale -- exactement le trou documenté pour
# les valeurs périmées (JOURNAL du 18/09, consigne "Supports-Vega" LOT 6), transposé aux
# images.
#
# Comparaison PAR CONTENU (hash), jamais par nom de fichier : un fichier renommé ou une
# figure restreinte réutilisée sous un autre nom serait invisible à une comparaison par
# chemin.
#
# Usage :
#   _Setup/outils/verifier_pptx_restreint.sh                 # les S01/S02/S03.pptx de Seances/
#   _Setup/outils/verifier_pptx_restreint.sh chemin/X.pptx [Y.pptx ...]

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../.." && pwd)"
DOSSIER_RESTREINT="$REPO_ROOT/Helice/Images/restreint"

cibles=("$@")
if [ ${#cibles[@]} -eq 0 ]; then
    for s in S01 S02 S03; do
        p="$REPO_ROOT/Seances/${s}.pptx"
        [ -f "$p" ] && cibles+=("$p")
    done
fi
if [ ${#cibles[@]} -eq 0 ]; then
    echo "Aucun .pptx à vérifier (ni en argument, ni Seances/S01/S02/S03.pptx présents)." >&2
    exit 2
fi

if [ ! -d "$DOSSIER_RESTREINT" ]; then
    echo "OK -- $DOSSIER_RESTREINT absent : aucune figure restreinte n'existe sur ce poste, rien à vérifier."
    exit 0
fi

# Hashes des images restreintes connues.
hashes_restreints=()
while IFS= read -r -d '' f; do
    h="$(sha256sum "$f" | cut -d' ' -f1)"
    hashes_restreints+=("$h:$f")
done < <(find "$DOSSIER_RESTREINT" -type f -print0)

if [ ${#hashes_restreints[@]} -eq 0 ]; then
    echo "OK -- $DOSSIER_RESTREINT existe mais est vide : rien à vérifier."
    exit 0
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
    unzip -oq "$pptx" "ppt/media/*" -d "$dep" 2>/dev/null
    n_trouve=0
    if [ -d "$dep/ppt/media" ]; then
        while IFS= read -r -d '' media; do
            h_media="$(sha256sum "$media" | cut -d' ' -f1)"
            for entry in "${hashes_restreints[@]}"; do
                h_restreint="${entry%%:*}"
                src_restreint="${entry#*:}"
                if [ "$h_media" = "$h_restreint" ]; then
                    echo "RESTREINT EMBARQUÉ : $pptx contient $(basename "$media") -- contenu identique à $src_restreint (hash $h_media)" >&2
                    n_trouve=$((n_trouve + 1))
                    fail=1
                fi
            done
        done < <(find "$dep/ppt/media" -type f -print0)
    fi
    if [ "$n_trouve" -eq 0 ]; then
        echo "OK -- $pptx : aucune image restreinte embarquée (${#hashes_restreints[@]} figure(s) restreinte(s) connue(s) testée(s))."
    fi
done

exit $fail
