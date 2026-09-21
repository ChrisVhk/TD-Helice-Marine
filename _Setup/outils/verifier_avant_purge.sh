#!/usr/bin/env bash
# Protocole anti-recidive (LOT 6, consigne du 18/09 "Rayon-explosion-et-relance") --
# ecrit comme script executable, pas comme note : une regle qui ne s'execute pas
# sera oubliee.
#
# Motif : la prolongation a 4 tours de case_kEpsilon_layers (17/09) a fait
# `rm -rf processor*` puis `decomposePar -latestTime` SANS verifier que la
# racine du cas portait bien l'avancement des 2 tours -- elle ne le portait
# pas (seuls processor*/ le portaient, jamais reconstruits). Resultat :
# decomposePar est reparti de t=0, et les 2 tours de calcul ont ete perdus
# (le fichier d'efforts brut a ete ecrase par la reprise avortee).
#
# REGLE : ne JAMAIS supprimer processor*/ avant d'avoir verifie que la racine
# du cas porte deja le temps que l'on croit reprendre. Si on ne peut pas le
# verifier, on ne supprime pas.
#
# Usage :
#   _Setup/outils/verifier_avant_purge.sh <dossier_cas>
#   -> exit 0 et imprime le dernier temps racine si la racine a un temps
#      AUTRE que "0" (donc probablement deja reconstruite a un point utile) ;
#   -> exit 1 (et n'efface RIEN -- ce script ne touche jamais processor*/
#      lui-meme, il ne fait QUE repondre oui/non) si la racine n'a que "0" --
#      dans ce cas, `rm -rf processor*` DETRUIRAIT le seul exemplaire de
#      l'avancement s'il vit uniquement dans processor*/. Reconstruire
#      D'ABORD (`reconstructPar -latestTime`) avant de refaire tourner ce
#      script.
set -u

CASE_DIR="${1:-}"
if [ -z "$CASE_DIR" ] || [ ! -d "$CASE_DIR" ]; then
    echo "Usage: $0 <dossier_cas>" >&2
    exit 2
fi

cd "$CASE_DIR" || exit 2

temps_racine=$(find . -maxdepth 1 -mindepth 1 -type d -regextype posix-extended -regex './[0-9]+\.?[0-9]*' \
    | xargs -n1 basename 2>/dev/null | sort -g | tail -1)

if [ -z "$temps_racine" ]; then
    echo "REFUS -- ${CASE_DIR} : aucun repertoire de temps a la racine (pas meme 0/) -- cas dans un etat inattendu." >&2
    exit 1
fi

if [ "$temps_racine" = "0" ]; then
    n_proc_temps=$(find processor0 -maxdepth 1 -mindepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+\.?[0-9]*' 2>/dev/null | wc -l)
    if [ "$n_proc_temps" -gt 1 ]; then
        echo "REFUS -- ${CASE_DIR} : la racine n'a que 0/, mais processor0/ porte ${n_proc_temps} temps -- l'avancement" >&2
        echo "         vit UNIQUEMENT dans processor*/. rm -rf processor* le detruirait (c'est exactement ce qui" >&2
        echo "         est arrive a case_kEpsilon_layers le 17/09). Lancer 'reconstructPar -latestTime' D'ABORD," >&2
        echo "         PUIS relancer ce script." >&2
    else
        echo "REFUS -- ${CASE_DIR} : la racine n'a que 0/, aucun avancement visible ni a la racine ni en processeur." >&2
    fi
    exit 1
fi

echo "OK -- ${CASE_DIR} : la racine porte deja le temps ${temps_racine} -- rm -rf processor* suivi de"
echo "      'decomposePar -latestTime' reprendra correctement a partir de ce temps, jamais de zero."
exit 0
