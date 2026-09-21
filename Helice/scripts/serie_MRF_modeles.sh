#!/usr/bin/env bash
# MRF en kOmegaSST puis en laminaire, dans la configuration EXACTE de case_kEpsilon_MRF (20/09 soir).
# Critère, variables tenues égales / qui bougent, prévisions et risque laminaire écrits AVANT :
#   ENSM-Enseignement/_Reserve/comparaison-3-modeles/LOT4b_MRF_kOmegaSST_laminaire_critere.md
# Deux cas en SÉQUENCE, un seul lancement chacun, aucune reprise ni réglage : un run qui diverge ou plafonne est un résultat, pas un défaut.
# État écrit par le script lui-même dans Helice/_ETAT_SERIE.txt ; aucun gardien détaché (attente par PID, kill -0).
# Arrêts : espace libre de l'hôte < 15 Go, durée maximale par cas dépassée. Un rc != 0 est CONSIGNÉ (c'est un résultat) et n'empêche pas de lancer le second cas.
# Usage : SERIE_MODE=prep bash Helice/scripts/serie_MRF_modeles.sh   (prépare les deux cas, ne lance rien)
#         bash Helice/scripts/serie_MRF_modeles.sh                     (prépare et lance)
set -o pipefail
HELICE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ETAT="$HELICE/_ETAT_SERIE.txt"
SEUIL_GO=15
LIM=2400
SRC="$HELICE/case_kEpsilon_MRF"
source /usr/lib/openfoam/openfoam2412/etc/bashrc >/dev/null 2>&1   # avant `set -u`
set -u

libre_go() { df -BG --output=avail /mnt/c | tail -1 | tr -dc '0-9'; }
ecrire()   { printf '%s | libre %s Go | %s | %s\n' "$(date '+%F %T')" "$(libre_go)" "$1" "${2:-}" >> "$ETAT"; }
residu() { grep -E "Solving for $2," "$1" 2>/dev/null | tail -1 | sed -E 's/.*Initial residual = ([0-9.e+-]+),.*/\1/'; }
moyennes() { awk '!/^#/ && NF>=7 {a[NR]=$5; b[NR]=$6; c[NR]=$7; n=NR} END{if(n<200){print "moins de 200 lignes"; exit} s1=s2=s3=0; k=0; for(i=n-199;i<=n;i++){s1+=a[i];s2+=b[i];s3+=c[i];k++} printf "K_T %.5f  10K_Q %.5f  eta0_solveur %.5f  (%d dernières lignes)", s1/k, s2/k, s3/k, k}' \
        "$1/postProcessing/propellerInfo1/0/propellerPerformance.dat"; }

preparer() { # nom_du_modele  (kOmegaSST | laminar)
    local m="$1" D="$HELICE/case_${1}_MRF"
    rm -rf "$D"; mkdir -p "$D/0"
    cp -r "$SRC/constant" "$SRC/system" "$D/"
    cp "$SRC/0/U" "$SRC/0/p" "$D/0/"
    case "$m" in
        kOmegaSST)
            cp "$SRC/0/k" "$SRC/0/nut" "$D/0/"
            cp "$HELICE/case_kOmegaSST/0.orig/omega" "$D/0/"
            cp "$HELICE/case_kOmegaSST/constant/turbulenceProperties" "$D/constant/turbulenceProperties"
            sed -i 's/^    div(phi,epsilon) \$turbulence;/    div(phi,epsilon) $turbulence;\n    div(phi,omega)  $turbulence;/' "$D/system/fvSchemes"
            sed -i 's/"(U|k|epsilon)"/"(U|k|epsilon|omega)"/' "$D/system/fvSolution" ;;
        laminar)
            cp "$HELICE/case_laminar/constant/turbulenceProperties" "$D/constant/turbulenceProperties" ;;
    esac
    ( cd "$D" && decomposePar > log.decomposePar 2>&1 ) || return 1
}

lancer() { # modele
    local m="$1" dir="$HELICE/case_${1}_MRF" pid rc t0 dernier=0 it
    bash "$HELICE/../_Setup/outils/preflight.sh" >> "$ETAT" 2>&1 || { ecrire "$m ARRÊT : pré-vol INV-23 non vert" ""; return 90; }   # sans argument : disque et RAM ; avec un cas il exige un calcul DÉJÀ en cours
    ( cd "$dir" || exit 90; exec mpirun -np 8 simpleFoam -parallel > log.simpleFoam 2>&1 ) &
    pid=$!
    ecrire "MRF $m DÉMARRÉ" "PID $pid, durée max ${LIM}s"
    sleep 20; bash "$HELICE/../_Setup/outils/preflight.sh" "$dir" >> "$ETAT" 2>&1 || ecrire "MRF $m : pré-vol avec cas ROUGE après démarrage" ""
    t0=$(date +%s)
    while kill -0 "$pid" 2>/dev/null; do
        sleep 20
        if [ "$(libre_go)" -lt "$SEUIL_GO" ]; then ecrire "MRF $m ARRÊT : espace libre < ${SEUIL_GO} Go" "kill $pid"; kill "$pid" 2>/dev/null; wait "$pid" 2>/dev/null; return 91; fi
        if [ $(( $(date +%s) - t0 )) -gt "$LIM" ]; then ecrire "MRF $m ARRÊT : durée max dépassée" "kill $pid"; kill "$pid" 2>/dev/null; wait "$pid" 2>/dev/null; return 92; fi
        if [ $(( $(date +%s) - dernier )) -ge 120 ]; then
            dernier=$(date +%s); it=$(grep -c '^Time = ' "$dir/log.simpleFoam")
            ecrire "MRF $m en cours" "itérations $it, résidus initiaux p $(residu "$dir/log.simpleFoam" p) Ux $(residu "$dir/log.simpleFoam" Ux)"
        fi
    done
    wait "$pid"; rc=$?
    ecrire "MRF $m TERMINÉ rc=$rc" "$(grep -c '^Time = ' "$dir/log.simpleFoam") itérations ; $(moyennes "$dir")"
    return "$rc"
}

: > "$ETAT"
ecrire "SÉRIE MRF MODÈLES DÉMARRÉE" "script PID $$ ; critères : LOT4b_MRF_kOmegaSST_laminaire_critere.md"
bash "$HELICE/../_Setup/outils/preflight.sh" >> "$ETAT" 2>&1 || { ecrire "ARRÊT : pré-vol INV-23 non vert" ""; exit 1; }
for m in kOmegaSST laminar; do preparer "$m" || { ecrire "ARRÊT : préparation de $m impossible" ""; exit 1; }; done
[ "${SERIE_MODE:-}" = "prep" ] && { ecrire "PRÉPARATION SEULE faite" "rien lancé"; exit 0; }
for m in kOmegaSST laminar; do lancer "$m" || ecrire "MRF $m : rc≠0, CONSIGNÉ (résultat, pas de relance)" ""; done
ecrire "SÉRIE TERMINÉE" "comparer avec case_kEpsilon_MRF (K_T 0,21398 ; 10K_Q 0,54145)"
